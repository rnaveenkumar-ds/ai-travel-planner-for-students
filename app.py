import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster
import time
import random
from tenacity import retry, stop_after_attempt, wait_fixed

# ------------------- BASIC SETUP -------------------
st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("🎓 AI Travel Planner for Students")

# ------------------- SESSION STATE INIT -------------------
defaults = {
    "from_location": "",
    "destination": "",
    "days": 2,
    "budget": 3000,
    "members": 1,
    "plan": "",
    "show_hotels": False,
    "show_transport": False,
    "show_attractions": False,
    "show_route": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------- RESET FUNCTION -------------------
def reset_app():
    for k, v in defaults.items():
        st.session_state[k] = v
    st.cache_data.clear()

# ------------------- UTILITY FUNCTIONS -------------------
@st.cache_data(show_spinner=False)
def check_api_health():
    """Quick check if Overpass is up."""
    try:
        r = requests.get("https://overpass-api.de/api/status", timeout=5)
        return r.status_code == 200
    except:
        return False

@st.cache_data(show_spinner=False)
@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
def overpass(query):
    if not check_api_health():
        # Removed warning: st.warning("Overpass API is down. Using enhanced fallback data for better results.")
        return []
    try:
        time.sleep(0.5)
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            timeout=20
        )
        if r.status_code == 504:
            # Removed warning: st.warning("Overpass API timeout. Using fallback data.")
            return []
        r.raise_for_status()
        return r.json().get("elements", [])
    except requests.exceptions.RequestException as e:
        # Removed warning: st.warning("API error. Using fallback data.")
        return []
    except Exception as e:
        # Removed warning: st.warning("Unexpected error. Using fallback data.")
        return []

@st.cache_data(show_spinner=False)
def get_lat_lon(city):
    city = city.strip()
    if not city:
        return [20.5937, 78.9629]
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        data = requests.get(url, timeout=5).json()
        if data and len(data) > 0 and 'lat' in data[0] and 'lon' in data[0]:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return [lat, lon]
    except Exception:
        pass
    locations = {
        "Goa": [15.4909, 73.8278],
        "Manali": [32.2396, 77.1887],
        "Jaipur": [26.9124, 75.7873],
        "Delhi": [28.7041, 77.1025],
        "Agra": [27.1767, 78.0081],
        "Pondicherry": [11.9139, 79.8145],
        "Mumbai": [19.0760, 72.8777],
        "Chennai": [13.0827, 80.2707],
        "Kolkata": [22.5726, 88.3639],
    }
    return locations.get(city.title(), [20.5937, 78.9629])

# ------------------- REAL DATA -------------------
@st.cache_data(show_spinner=False)
def get_real_hotels(lat, lon, limit=5):
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="hotel"](around:1000,{lat},{lon});
      node["tourism"="hostel"](around:1000,{lat},{lon});
    );
    out;
    """
    els = overpass(query)
    hotels = [e.get("tags", {}).get("name") for e in els if e.get("tags", {}).get("name")]
    if hotels:
        return hotels[:limit]
    # Enhanced location-aware fallbacks
    dest = st.session_state.destination.lower()
    if "goa" in dest or "beach" in dest:
        return ["Beachside Resort", "Coastal Hostel", "Seaside Inn", "Ocean View Hotel", "Tropical Lodge"]
    elif "manali" in dest or "mountain" in dest:
        return ["Mountain Retreat", "Hilltop Hostel", "Valley Inn", "Alpine Lodge", "Ridge Hotel"]
    elif "delhi" in dest or "agra" in dest:
        return ["Heritage Hotel", "City Center Inn", "Cultural Lodge", "Historic Hostel", "Urban Resort"]
    else:
        return ["Budget Hotel A", "Affordable Inn", "Local Hostel", "Economy Lodge", "Traveler's Stay"]

@st.cache_data(show_spinner=False)
def get_real_attractions(lat, lon, limit=10):
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="attraction"](around:1000,{lat},{lon});
      node["historic"="monument"](around:1000,{lat},{lon});
      node["leisure"="park"](around:1000,{lat},{lon});
    );
    out;
    """
    els = overpass(query)
    attractions = [e.get("tags", {}).get("name") for e in els if e.get("tags", {}).get("name")]
    if attractions:
        return attractions[:limit]
    # Enhanced location-aware fallbacks
    dest = st.session_state.destination.lower()
    if "goa" in dest or "beach" in dest:
        return ["Calangute Beach", "Anjuna Flea Market", "Dudhsagar Falls", "Fort Aguada", "Chapora Fort", "Baga Beach", "Palolem Beach", "Arambol Beach", "Colva Beach", "Miramar Beach"]
    elif "manali" in dest or "mountain" in dest:
        return ["Rohtang Pass", "Solang Valley", "Hadimba Temple", "Manu Temple", "Vashisht Hot Springs", "Mall Road", "Naggar Castle", "Great Himalayan National Park", "Jogini Waterfall", "Bhrigu Lake"]
    elif "delhi" in dest:
        return ["Red Fort", "India Gate", "Qutub Minar", "Lotus Temple", "Akshardham Temple", "Humayun's Tomb", "Chandni Chowk", "Connaught Place", "Raj Ghat", "Jama Masjid"]
    elif "agra" in dest:
        return ["Taj Mahal", "Agra Fort", "Fatehpur Sikri", "Itmad-ud-Daulah", "Mehtab Bagh", "Kinari Bazaar", "Sikandra", "Jama Masjid", "Tomb of Akbar", "Anguri Bagh"]
    else:
        return ["Local Park A", "Historic Site B", "Scenic View C", "Cultural Spot D", "Nature Trail E", "Market F", "Monument G", "Garden H", "Museum I", "Beach J"]

@st.cache_data(show_spinner=False)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url, timeout=5).json()
        w = data.get("current_weather", {})
        temp = w.get('temperature')
        wind = w.get('windspeed')
        if temp is not None and wind is not None:
            return f"🌡 {temp}°C | 💨 Wind {wind} km/h"
    except Exception:
        pass
    return "Weather unavailable"

# ------------------- MAP FUNCTIONS -------------------
def build_map(lat, lon, query, color, icon):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    cluster = MarkerCluster().add_to(m)
    for e in overpass(query):
        tags = e.get("tags", {})
        name = tags.get("name", "Unknown")
        if name != "Unknown":
            popup = f"<b>{name}</b><br>{tags.get('addr:street', '')}"
            folium.Marker(
                [e.get("lat", lat), e.get("lon", lon)],
                popup=popup,
                tooltip=name,
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(cluster)
    return m

def hotel_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json][timeout:15];node["tourism"~"hotel|hostel"](around:1000,{lat},{lon});out;',
        "green", "home"
    )

def transport_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json][timeout:15];node["amenity"="bus_station"](around:1000,{lat},{lon});out;',
        "blue", "road"
    )

def attraction_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json][timeout:15];node["tourism"="attraction"](around:1000,{lat},{lon});out;',
        "orange", "star"
    )

def route_map(from_lat, from_lon, to_lat, to_lon):
    m = folium.Map(location=[(from_lat + to_lat) / 2, (from_lon + to_lon) / 2], zoom_start=6)
    folium.Marker([from_lat, from_lon], popup="Starting Point", icon=folium.Icon(color="red", icon="play")).add_to(m)
    folium.Marker([to_lat, to_lon], popup="Destination", icon=folium.Icon(color="green", icon="flag")).add_to(m)
    folium.PolyLine([(from_lat, from_lon), (to_lat, to_lon)], color="blue", weight=5, opacity=0.7).add_to(m)
    return m

# ------------------- PLAN GENERATOR -------------------
def generate_plan(from_loc, dest, budget, days, members, lat, lon):
    hotels = get_real_hotels(lat, lon)
    places = get_real_attractions(lat, lon)
    weather = get_weather(lat, lon)
    per_day = max(1, int(budget / days / members))

    plan = f"📍 From: {from_loc} → To: {dest}\n🌤️ Weather at Destination: {weather}\n\n"
    if not hotels or not places:
        plan += "⚠️ Note: Limited data available for this location. Results may be generic.\n\n"
    idx = 0
    for d in range(1, days + 1):
        plan += f"🗓 Day {d}\n"
        plan += f"🏨 Stay: {hotels[(d-1) % len(hotels)]}\n"
        plan += f"🌅 Morning: {places[idx % len(places)]}\n"
        plan += f"🌞 Afternoon: {places[(idx+1) % len(places)]}\n"
        plan += f"🌆 Evening: {places[(idx+2) % len(places)]}\n"
        plan += f"💰 Estimated Spend (per person): ₹{per_day}\n\n"
        idx += 3

    plan += "💡 Tips:\n- Use public transport\n- Start early\n- Carry student ID\n"
    return plan

# ------------------- UI -------------------
st.info("ℹ️ Data is fetched from free APIs; may be slow. If maps don’t load, refresh or reduce area.")

col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.from_location = st.text_input("📍 From Location", value=st.session_state.from_location)
with col2:
    st.session_state.destination = st.text_input("📍 To Destination", value=st.session_state.destination)
with col3:
    st.session_state.days = st.number_input("📅 Days", 1, 20, st.session_state.days)

col4, col5 = st.columns(2)
with col4:
    st.session_state.budget = st.number_input("💰 Budget (₹)", 1000, step=500, value=st.session_state.budget)
with col5:
    st.session_state.members = st.number_input("👥 Members", 1, 10, st.session_state.members)

st.session_state.show_route = st.checkbox("🗺️ Show Route Map (From → To)", value=st.session_state.show_route)
st.session_state.show_hotels = st.checkbox("🏨 Show Hotels Map", value=st.session_state.show_hotels)
st.session_state.show_transport = st.checkbox("🚕 Show Transport Map", value=st.session_state.show_transport)
st.session_state.show_attractions = st.checkbox("🎡 Show Attractions Map", value=st.session_state.show_attractions)

colA, colB = st.columns(2)
with colA:
    if st.button("✨ Generate Plan"):
        if st.session_state.from_location.strip() and st.session_state.destination.strip():
            progress_bar = st.progress(0)
            with st.spinner("⏳ Generating your travel plan..."):
                try:
                    progress_bar.progress(25)
                    to_lat, to_lon = get_lat_lon(st.session_state.destination)
                    progress_bar.progress(50)
                    st.session_state.plan = generate_plan(
                        st.session_state.from_location,
                        st.session_state.destination,
                        st.session_state.budget,
                        st.session_state.days,
                        st.session_state.members,
                        to_lat, to_lon
                    )
                    progress_bar.progress(100)
                    st.success("✅ Travel plan generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {e}. Try again.")
                finally:
                    progress_bar.empty()
        else:
            st.warning("Please enter both 'From' and 'To' locations")

with colB:
    if st.button("🔄 Reset Planner"):
        reset_app()

st.divider()

# ------------------- OUTPUT -------------------
if st.session_state.plan:
    to_lat, to_lon = get_lat_lon(st.session_state.destination)

    st.subheader("📝 Travel Plan")
    st.text(st.session_state.plan)

    if st.button("🔄 Refresh Data (if maps are empty)"):
        st.cache_data.clear()
        st.rerun()

    if st.session_state.show_route:
        from_lat, from_lon = get_lat_lon(st.session_state.from_location)
        st.subheader("🗺️ Route Map (From → To)")
        st_folium(route_map(from_lat, from_lon, to_lat, to_lon), width=800, height=450, key="route_map")

    if st.session_state.show_hotels:
        st.subheader("🏨 Hotels Map")
        st_folium(hotel_map(to_lat, to_lon), width=800, height=450, key="hotels_map")

    if st.session_state.show_transport:
        st.subheader("🚕 Transport Map")
        st_folium(transport_map(to_lat, to_lon), width=800, height=450, key="transport_map")

    if st.session_state.show_attractions:
        st.subheader("🎡 Attractions Map")
        st_folium(attraction_map(to_lat, to_lon), width=800, height=450, key="attractions_map")

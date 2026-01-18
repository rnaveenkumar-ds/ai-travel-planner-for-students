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
    "from_location": "",  # NEW: Added for starting location
    "destination": "",
    "days": 2,
    "budget": 3000,
    "members": 1,
    "plan": "",
    "show_hotels": False,
    "show_transport": False,
    "show_attractions": False,
    "show_route": False  # NEW: Added for route map checkbox
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
@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def overpass(query):
    try:
        time.sleep(2)
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            timeout=45
        )
        if r.status_code == 504:
            st.warning("Overpass API is temporarily slow (504 Timeout). Using fallback data. Try again later or refresh.")
            return []
        r.raise_for_status()
        return r.json().get("elements", [])
    except requests.exceptions.RequestException as e:
        st.warning(f"API request failed: {e}. Using fallback data.")
        return []
    except Exception as e:
        st.warning(f"Unexpected API error: {e}. Using fallback data.")
        return []

@st.cache_data(show_spinner=False)
def get_lat_lon(city):
    if not city.strip():
        return [20.5937, 78.9629]
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        data = requests.get(url, timeout=10).json()
        if data:
            return [float(data[0]['lat']), float(data[0]['lon'])]
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
    return locations.get(city.strip().title(), [20.5937, 78.9629])

# ------------------- REAL DATA -------------------
@st.cache_data(show_spinner=False)
def get_real_hotels(lat, lon, limit=5):
    query = f"""
    [out:json];
    (
      node["tourism"="hotel"](around:3000,{lat},{lon});
      node["tourism"="hostel"](around:3000,{lat},{lon});
    );
    out;
    """
    els = overpass(query)
    return [e.get("tags", {}).get("name") for e in els if e.get("tags", {}).get("name")][:limit] or ["Budget hotels in the area"]

@st.cache_data(show_spinner=False)
def get_real_attractions(lat, lon, limit=10):
    query = f"""
    [out:json];
    (
      node["tourism"="attraction"](around:3000,{lat},{lon});
      node["historic"="monument"](around:3000,{lat},{lon});
      node["leisure"="park"](around:3000,{lat},{lon});
    );
    out;
    """
    els = overpass(query)
    return [e.get("tags", {}).get("name") for e in els if e.get("tags", {}).get("name")][:limit] or ["Explore local sights and parks"]

@st.cache_data(show_spinner=False)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url, timeout=10).json()
        w = data.get("current_weather", {})
        return f"🌡 {w.get('temperature','N/A')}°C | 💨 Wind {w.get('windspeed','N/A')} km/h"
    except Exception as e:
        st.warning(f"Weather API error: {e}. Weather unavailable.")
        return "Weather unavailable"

# ------------------- MAP FUNCTIONS -------------------
def build_map(lat, lon, query, color, icon):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    cluster = MarkerCluster().add_to(m)
    for e in overpass(query):
        tags = e.get("tags", {})
        popup = f"<b>{tags.get('name', 'Unknown')}</b><br>{tags.get('addr:street', '')}"
        folium.Marker(
            [e["lat"], e["lon"]],
            popup=popup,
            tooltip=tags.get("name", "Unknown"),
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(cluster)
    return m

def hotel_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json];node["tourism"~"hotel|hostel"](around:3000,{lat},{lon});out;',
        "green", "home"
    )

def transport_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json];node["amenity"="bus_station"](around:3000,{lat},{lon});out;',
        "blue", "road"
    )

def attraction_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json];node["tourism"="attraction"](around:3000,{lat},{lon});out;',
        "orange", "star"
    )

# NEW: Route map from "from" to "destination"
def route_map(from_lat, from_lon, to_lat, to_lon):
    m = folium.Map(location=[(from_lat + to_lat) / 2, (from_lon + to_lon) / 2], zoom_start=6)
    # Add markers for start and end
    folium.Marker([from_lat, from_lon], popup="Starting Point", icon=folium.Icon(color="red", icon="play")).add_to(m)
    folium.Marker([to_lat, to_lon], popup="Destination", icon=folium.Icon(color="green", icon="flag")).add_to(m)
    # Draw a simple line (straight route)
    folium.PolyLine([(from_lat, from_lon), (to_lat, to_lon)], color="blue", weight=5, opacity=0.7).add_to(m)
    return m

# ------------------- PLAN GENERATOR -------------------
def generate_plan(from_loc, dest, budget, days, members, lat, lon):  # UPDATED: Added from_loc parameter
    hotels = get_real_hotels(lat, lon)
    places = get_real_attractions(lat, lon)
    weather = get_weather(lat, lon)
    per_day = max(1, int(budget / days / members))

    plan = f"📍 From: {from_loc} → To: {dest}\n🌤️ Weather at Destination: {weather}\n\n"  # UPDATED: Added "From → To"
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
st.info("ℹ️ Note: Data is fetched from free APIs, which may be slow or unavailable at times. If you see 'fallback data,' try refreshing or choosing a smaller area.")

col1, col2, col3 = st.columns(3)  # UPDATED: Changed to 3 columns to fit new input
with col1:
    st.session_state.from_location = st.text_input("📍 From Location", value=st.session_state.from_location)  # NEW: Added input
with col2:
    st.session_state.destination = st.text_input("📍 To Destination", value=st.session_state.destination)
with col3:
    st.session_state.days = st.number_input("📅 Days", 1, 20, st.session_state.days)

col4, col5 = st.columns(2)
with col4:
    st.session_state.budget = st.number_input("💰 Budget (₹)", 1000, step=500, value=st.session_state.budget)
with col5:
    st.session_state.members = st.number_input("👥 Members", 1, 10, st.session_state.members)

st.session_state.show_route = st.checkbox("🗺️ Show Route Map (From → To)", value=st.session_state.show_route)  # NEW: Added checkbox
st.session_state.show_hotels = st.checkbox("🏨 Show Hotels Map", value=st.session_state.show_hotels)
st.session_state.show_transport = st.checkbox("🚕 Show Transport Map", value=st.session_state.show_transport)
st.session_state.show_attractions = st.checkbox("🎡 Show Attractions Map", value=st.session_state.show_attractions)

colA, colB = st.columns(2)
with colA:
    if st.button("✨ Generate Plan"):
        if st.session_state.from_location.strip() and st.session_state.destination.strip():  # UPDATED: Require both locations
            with st.spinner("⏳ Generating your travel plan..."):
                try:
                    to_lat, to_lon = get_lat_lon(st.session_state.destination)
                    st.session_state.plan = generate_plan(
                        st.session_state.from_location,  # NEW: Pass from_location
                        st.session_state.destination,
                        st.session_state.budget,
                        st.session_state.days,
                        st.session_state.members,
                        to_lat, to_lon
                    )
                    st.success("✅ Travel plan generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating plan: {e}. Try again or check inputs.")
        else:
            st.warning("Please enter both 'From' and 'To' locations")  # UPDATED: New warning

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

    if st.session_state.show_route:  # NEW: Display route map if checked
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
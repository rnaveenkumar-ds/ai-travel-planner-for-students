import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster
import time

# ------------------- FUNCTIONS -------------------

@st.cache_data
def get_ai_activities(dest, budget):
    activities_map = {
        "manali": ["Hike to Rohtang Pass (if budget allows)", "Visit Hadimba Temple", "Explore local markets"],
        "jaipur": ["Visit Amber Fort", "Stroll through City Palace", "Shop at Johari Bazaar"],
        "delhi": ["Explore Red Fort", "Visit India Gate", "Try street food at Chandni Chowk"],
        "agra": ["See Taj Mahal at sunrise", "Visit Agra Fort", "Local rickshaw tours"],
        "pondicherry": ["Relax on Auroville Beach", "Visit French Quarter", "Explore Sri Aurobindo Ashram"],
        "goa": ["Beach hopping", "Visit Basilica of Bom Jesus", "Water sports if budget permits"],
    }
    base = activities_map.get(dest.lower(), ["Explore local attractions", "Visit markets", "Enjoy nature walks"])
    if budget < 1000:
        return ", ".join(base[:2])
    return ", ".join(base)

@st.cache_data
def generate_travel_plan(destination, total_budget, days, members):
    try:
        destinations = [d.strip() for d in destination.split(",") if d.strip()]
        if not destinations:
            return "❌ Please enter at least one valid destination."

        budget_per_person_per_day = total_budget / days / members
        plan_text = f"📍 Destination(s): {', '.join(destinations)}\n\n"
        plan_text += "🤖 AI-Generated Insights: Tailored for students (budget + adventure + culture).\n\n"

        day = 1
        for dest in destinations:
            dest_days = max(1, days // len(destinations))
            for _ in range(dest_days):
                if day > days:
                    break
                # Hotel suggestion
                if budget_per_person_per_day < 1000:
                    hotel_type = "Budget hostel (dorm beds)"
                    hotel_cost = 600 * members
                elif budget_per_person_per_day <= 3000:
                    hotel_type = "Mid-range hotel (private rooms)"
                    hotel_cost = 1800 * members
                else:
                    hotel_type = "Luxury hotel (resorts)"
                    hotel_cost = 3500 * members

                transport_cost = 400 * members
                food_cost = int(budget_per_person_per_day * 0.4 * members)
                activities = get_ai_activities(dest, budget_per_person_per_day)

                plan_text += f"🗓 Day {day} ({dest}):\n"
                plan_text += f"- 🏨 Stay: {hotel_type} (₹{hotel_cost})\n"
                plan_text += f"- 🚕 Transport: Local buses/trains/rented vehicles (₹{transport_cost})\n"
                plan_text += f"- 🍲 Food: Street food/cafes (₹{food_cost})\n"
                plan_text += f"- 🎉 Activities: {activities}\n\n"
                day += 1

        total_hotel = sum([600 if budget_per_person_per_day < 1000 else 1800 if budget_per_person_per_day <= 3000 else 3500 for _ in range(days)]) * members
        total_transport = 400 * members * days
        total_food = int(budget_per_person_per_day * 0.4 * members * days)
        total_estimated = total_hotel + total_transport + total_food

        plan_text += f"💰 Estimated Total Cost (₹{total_estimated}):\n- Hotel: ₹{total_hotel}\n- Transport: ₹{total_transport}\n- Food: ₹{total_food}\n"
        plan_text += "💡 Tips: Book via apps for discounts, use student IDs, stay hydrated, respect local customs.\n"
        return plan_text

    except Exception as e:
        return f"❌ Error generating plan: {e}"

@st.cache_data
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url, timeout=10).json()
        w = data.get("current_weather", {})
        temp = w.get("temperature", "N/A")
        wind = w.get("windspeed", "N/A")
        return f"🌡 {temp}°C | 💨 Wind: {wind} km/h"
    except Exception:
        return "Weather unavailable"

@st.cache_data
def overpass(query):
    try:
        response = requests.post("http://overpass-api.de/api/interpreter", data=query, timeout=30)
        data = response.json()
        return data.get("elements", [])
    except Exception:
        return []

def create_map(lat, lon, query, color="blue", icon="info-sign", empty_msg="No data found"):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    cluster = MarkerCluster().add_to(m)
    try:
        elements = overpass(query)
        if not elements:
            folium.Marker([lat, lon], popup=empty_msg, icon=folium.Icon(color="gray")).add_to(cluster)
        for e in elements:
            name = e.get("tags", {}).get("name", "Unnamed")
            folium.Marker([e["lat"], e["lon"]], popup=name, icon=folium.Icon(color=color, icon=icon)).add_to(cluster)
    except Exception:
        folium.Marker([lat, lon], popup="Error loading map", icon=folium.Icon(color="gray")).add_to(cluster)
    return m

@st.cache_data
def hotel_map(lat, lon, budget_per_day):
    query = f"""
    [out:json][timeout:10];
    (
      node["tourism"="hotel"](around:5000,{lat},{lon});
      node["tourism"="hostel"](around:5000,{lat},{lon});
    );
    out;
    """
    color = "green" if budget_per_day < 1000 else "blue" if budget_per_day <= 3000 else "red"
    return create_map(lat, lon, query, color=color, icon="home", empty_msg="No hotels found nearby.")

@st.cache_data
def transport_map(lat, lon):
    query = f"""
    [out:json][timeout:10];
    (
      node["amenity"="bus_station"](around:5000,{lat},{lon});
      node["railway"="station"](around:5000,{lat},{lon});
      node["aeroway"="aerodrome"](around:5000,{lat},{lon});
    );
    out;
    """
    return create_map(lat, lon, query, color="green", icon="road", empty_msg="Check local transport apps.")

@st.cache_data
def attractions_map(lat, lon):
    query = f"""
    [out:json][timeout:10];
    (
      node["tourism"="attraction"](around:5000,{lat},{lon});
      node["historic"="monument"](around:5000,{lat},{lon});
    );
    out;
    """
    return create_map(lat, lon, query, color="orange", icon="star", empty_msg="Explore nearby attractions.")

# ------------------- UI -------------------

st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("🎓 Free AI Travel Planner for Students")

col1, col2 = st.columns(2)
with col1:
    destination = st.text_input("📍 Destination(s)", value="")
    days = st.number_input("📅 Number of Days", min_value=1, max_value=30, value=1)
with col2:
    budget = st.number_input("💰 Total Budget (INR)", min_value=1000, value=1000)
    members = st.number_input("👥 Members", min_value=1, max_value=10, value=1)

show_hotels = st.checkbox("🏨 Show Hotel Map")
show_transport = st.checkbox("🚕 Show Transportation Map")
show_attractions = st.checkbox("🎡 Show Attractions Map")

# Session state
if "plan" not in st.session_state:
    st.session_state.plan = ""

if st.button("✨ Generate Plan"):
    with st.spinner("Generating plan..."):
        time.sleep(1)
        st.session_state.plan = generate_travel_plan(destination, budget, int(days), int(members))

if st.button("🔄 Reset"):
    st.session_state.plan = ""
    st.write("✅ Reset complete! Please refresh the page if needed.")
    st.stop()  # Stops further execution safely

st.markdown("---")

# ------------------- DISPLAY -------------------

if st.session_state.plan:
    # Default location dict
    locations = {
        "Goa": [15.4909, 73.8278],
        "Manali": [32.2396, 77.1887],
        "Jaipur": [26.9124, 75.7873],
        "Delhi": [28.7041, 77.1025],
        "Agra": [27.1767, 78.0081],
        "Pondicherry": [11.9139, 79.8145],
        "Mumbai": [19.0760, 72.8777],
        "Kolkata": [22.5726, 88.3639],
        "Chennai": [13.0827, 80.2707],
    }
    first_dest = destination.split(",")[0].strip()
    lat, lon = locations.get(first_dest, [20.5937, 78.9629])
    budget_per_person_per_day = budget / days / members

    with st.expander("📝 AI Travel Plan", expanded=True):
        st.write(st.session_state.plan)

    with st.expander("🌤 Weather", expanded=True):
        st.success(get_weather(lat, lon))

    if show_hotels:
        with st.expander("🏨 Hotels", expanded=True):
            st_folium(hotel_map(lat, lon, budget_per_person_per_day), width=700, height=450)

    if show_transport:
        with st.expander("🚕 Transportation", expanded=True):
            st_folium(transport_map(lat, lon), width=700, height=450)

    if show_attractions:
        with st.expander("🎡 Attractions", expanded=True):
            st_folium(attractions_map(lat, lon), width=700, height=450)

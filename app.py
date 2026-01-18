import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster
import time
import random

# ------------------- BASIC SETUP -------------------
st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("🎓 AI Travel Planner for Students")

# ------------------- SESSION STATE INIT -------------------
defaults = {
    "destination": "",
    "days": 2,
    "budget": 3000,
    "members": 1,
    "plan": "",
    "show_hotels": False,
    "show_transport": False,
    "show_attractions": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------- RESET FUNCTION -------------------
def reset_app():
    for k, v in defaults.items():
        st.session_state[k] = v

# ------------------- UTILITY FUNCTIONS -------------------
@st.cache_data(show_spinner=False)
def overpass(query):
    try:
        time.sleep(1)
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            timeout=30
        )
        return r.json().get("elements", [])
    except Exception:
        return []

def get_lat_lon(city):
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
def get_real_hotels(lat, lon, limit=6):
    query = f"""
    [out:json];
    (
      node["tourism"="hotel"](around:5000,{lat},{lon});
      node["tourism"="hostel"](around:5000,{lat},{lon});
    );
    out;
    """
    els = overpass(query)
    return [e.get("tags", {}).get("name") for e in els if e.get("tags", {}).get("name")][:limit] or ["Local budget stays"]

@st.cache_data(show_spinner=False)
def get_real_attractions(lat, lon, limit=12):
    query = f"""
    [out:json];
    (
      node["tourism"="attraction"](around:5000,{lat},{lon});
      node["historic"="monument"](around:5000,{lat},{lon});
      node["leisure"="park"](around:5000,{lat},{lon});
    );
    out;
    """
    els = overpass(query)
    return [e.get("tags", {}).get("name") for e in els if e.get("tags", {}).get("name")][:limit] or ["Local exploration"]

@st.cache_data(show_spinner=False)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url, timeout=10).json()
        w = data.get("current_weather", {})
        return f"🌡 {w.get('temperature','N/A')}°C | 💨 Wind {w.get('windspeed','N/A')} km/h"
    except Exception:
        return "Weather unavailable"

# ------------------- MAP FUNCTIONS -------------------
def build_map(lat, lon, query, color, icon):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    cluster = MarkerCluster().add_to(m)
    for e in overpass(query):
        folium.Marker(
            [e["lat"], e["lon"]],
            popup=e.get("tags", {}).get("name", "Unknown"),
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(cluster)
    return m

def hotel_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json];node["tourism"~"hotel|hostel"](around:5000,{lat},{lon});out;',
        "green", "home"
    )

def transport_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json];node["amenity"="bus_station"](around:5000,{lat},{lon});out;',
        "blue", "road"
    )

def attraction_map(lat, lon):
    return build_map(
        lat, lon,
        f'[out:json];node["tourism"="attraction"](around:5000,{lat},{lon});out;',
        "orange", "star"
    )

# ------------------- PLAN GENERATOR -------------------
def generate_plan(dest, budget, days, members, lat, lon):
    hotels = get_real_hotels(lat, lon)
    places = get_real_attractions(lat, lon)
    per_day = int(budget / days / members)

    plan = f"📍 Destination: {dest}\n\n"
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
col1, col2 = st.columns(2)
with col1:
    st.session_state.destination = st.text_input("📍 Destination", value=st.session_state.destination)
    st.session_state.days = st.number_input("📅 Days", 1, 20, st.session_state.days)

with col2:
    st.session_state.budget = st.number_input("💰 Budget (₹)", 1000, step=500, value=st.session_state.budget)
    st.session_state.members = st.number_input("👥 Members", 1, 10, st.session_state.members)

st.session_state.show_hotels = st.checkbox("🏨 Show Hotels Map", value=st.session_state.show_hotels)
st.session_state.show_transport = st.checkbox("🚕 Show Transport Map", value=st.session_state.show_transport)
st.session_state.show_attractions = st.checkbox("🎡 Show Attractions Map", value=st.session_state.show_attractions)

colA, colB = st.columns(2)
with colA:
    if st.button("✨ Generate Plan"):
        if st.session_state.destination.strip():
            msg = st.info("⏳ Please wait, we are creating your travel plan...")
            time.sleep(random.randint(5, 10))
            lat, lon = get_lat_lon(st.session_state.destination)
            st.session_state.plan = generate_plan(
                st.session_state.destination,
                st.session_state.budget,
                st.session_state.days,
                st.session_state.members,
                lat, lon
            )
            msg.empty()
            st.success("✅ Travel plan generated successfully!")
        else:
            st.warning("Please enter a destination")

with colB:
    if st.button("🔄 Reset Planner"):
        reset_app()

st.divider()

# ------------------- OUTPUT -------------------
if st.session_state.plan:
    lat, lon = get_lat_lon(st.session_state.destination)

    st.subheader("📝 Travel Plan")
    st.text(st.session_state.plan)

    if st.session_state.show_hotels:
        st.subheader("🏨 Hotels Map")
        st_folium(hotel_map(lat, lon), width=800, height=450, key="hotels_map")

    if st.session_state.show_transport:
        st.subheader("🚕 Transport Map")
        st_folium(transport_map(lat, lon), width=800, height=450, key="transport_map")

    if st.session_state.show_attractions:
        st.subheader("🎡 Attractions Map")
        st_folium(attraction_map(lat, lon), width=800, height=450, key="attractions_map")

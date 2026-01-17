import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# PAGE CONFIG
st.set_page_config(page_title="AI Travel Planner", layout="wide")

# ---------------- AI TRAVEL PLAN ----------------
def generate_travel_plan(destination, total_budget, days, members):
    """
    Generates a structured day-by-day student travel plan with:
    - Hotel suggestion
    - Transportation
    - Food budget
    - Tips
    """

    budget_per_person_per_day = total_budget / days / members

    # Define hotel categories based on per person per day budget
    if budget_per_person_per_day < 1000:
        hotel_type = "Budget hostel/hotel"
        hotel_cost = 800 * members
    elif budget_per_person_per_day <= 3000:
        hotel_type = "Mid-range hotel"
        hotel_cost = 2000 * members
    else:
        hotel_type = "Luxury hotel"
        hotel_cost = 4000 * members

    # Transportation cost logic
    transport_cost_per_day = 300 * members  # local buses, scooty
    food_cost_per_day = budget_per_person_per_day * members * 0.3  # 30% for food

    # Generate day-wise plan
    plan_text = f"📍 Destination: {destination}\n\n"
    for day in range(1, days + 1):
        plan_text += f"🗓 Day {day}:\n"
        plan_text += f"- Stay at: {hotel_type} (₹{hotel_cost})\n"
        plan_text += f"- Transportation: Local buses or rented scooty (₹{transport_cost_per_day})\n"
        plan_text += f"- Food: Budget meals and local cafes (₹{int(food_cost_per_day)})\n"
        plan_text += f"- Activities: Explore local attractions, markets, and beaches\n"
        plan_text += "\n"

    # Summary
    total_food = int(food_cost_per_day * days)
    total_transport = transport_cost_per_day * days
    plan_text += f"💰 Estimated total cost:\n- Hotel: ₹{hotel_cost * days}\n- Transport: ₹{total_transport}\n- Food: ₹{total_food}\n"
    plan_text += f"Tips: Use public transport, eat local street food, and book budget hotels early.\n"

    return plan_text

# ---------------- WEATHER ----------------
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url, timeout=10).json()
        w = data.get("current_weather", {})
        return f"🌡 {w.get('temperature')}°C | 💨 {w.get('windspeed')} km/h"
    except:
        return "Weather unavailable"

# ---------------- OVERPASS API ----------------
def overpass(query):
    url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data=query, timeout=30)
        if response.status_code == 200 and response.text.strip():
            try:
                return response.json().get("elements", [])
            except ValueError:
                return []
        return []
    except Exception as e:
        return []

# ---------------- HOTEL MAP ----------------
def hotel_map(lat, lon, budget_per_day):
    m = folium.Map(location=[lat, lon], zoom_start=13)

    query = f"""
    [out:json];
    (
      node["tourism"="hotel"](around:3000,{lat},{lon});
      node["tourism"="hostel"](around:3000,{lat},{lon});
    );
    out;
    """

    hotels = overpass(query)

    for h in hotels:
        name = h.get("tags", {}).get("name", "Hotel")

        if budget_per_day < 1000:
            color, label = "green", "Budget"
        elif budget_per_day <= 3000:
            color, label = "blue", "Mid-range"
        else:
            color, label = "red", "Luxury"

        folium.Marker(
            [h["lat"], h["lon"]],
            popup=f"{name} ({label})",
            icon=folium.Icon(color=color, icon="home")
        ).add_to(m)

    return m

# ---------------- TRANSPORT MAP ----------------
def transport_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=13)

    query = f"""
    [out:json];
    (
      node["amenity"="bus_station"](around:5000,{lat},{lon});
      node["railway"="station"](around:5000,{lat},{lon});
      node["aeroway"="aerodrome"](around:5000,{lat},{lon});
    );
    out;
    """

    places = overpass(query)

    for p in places:
        name = p.get("tags", {}).get("name", "Transport")
        tags = p.get("tags", {})

        if tags.get("amenity") == "bus_station":
            icon, color = "bus", "green"
        elif tags.get("railway") == "station":
            icon, color = "train", "blue"
        else:
            icon, color = "plane", "red"

        folium.Marker(
            [p["lat"], p["lon"]],
            popup=name,
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)

    return m

# ---------------- UI ----------------
st.title("🎓 Free AI Travel Planner for Students")

destination = st.text_input("📍 Destination", "Goa")
budget = st.number_input("💰 Total Budget (INR)", min_value=1000, value=5000)
days = st.number_input("📅 Number of Days", min_value=1, value=3)
members = st.number_input("👥 Members", min_value=1, value=2)

show_hotels = st.checkbox("🏨 Show Hotel Map (Cheap → Luxury)")
show_transport = st.checkbox("🚕 Show Transportation Map")

# Session state for output
if "plan" not in st.session_state:
    st.session_state.plan = ""

if st.button("✨ Generate Plan"):
    st.session_state.plan = generate_travel_plan(
        destination, budget, days, members
    )

if st.session_state.plan:
    # Coordinates
    locations = {
        "Goa": [15.4909, 73.8278],
        "Manali": [32.2396, 77.1887],
        "Jaipur": [26.9124, 75.7873]
    }
    lat, lon = locations.get(destination, [20.5937, 78.9629])

    st.subheader("📝 AI Travel Plan")
    st.write(st.session_state.plan)

    st.subheader("🌤 Weather")
    st.success(get_weather(lat, lon))

    budget_per_day = budget / days

    if show_hotels:
        st.subheader("🏨 Hotels (Based on Budget)")
        try:
            st_folium(hotel_map(lat, lon, budget_per_day), width=700, height=450)
        except Exception as e:
            st.warning("Hotel map unavailable - API issue")

    if show_transport:
        st.subheader("🚕 Transportation Options")
        try:
            st_folium(transport_map(lat, lon), width=700, height=450)
        except Exception as e:
            st.warning("Transport map unavailable - API issue")
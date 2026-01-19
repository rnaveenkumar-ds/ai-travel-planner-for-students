import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster
import time
import random
from tenacity import retry, stop_after_attempt, wait_fixed
from itertools import cycle

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("🎓 AI Travel Planner for Students")

# ================= SESSION STATE =================
defaults = {
    "from_location": "",
    "destination": "",
    "days": 2,
    "budget": 3000,
    "members": 1,
    "plan": "",
    "show_route": False,
    "show_hotels": False,
    "show_transport": False,
    "show_attractions": False,
    "route": 0,
    "hotels": 0,
    "transport": 0,
    "attractions": 0
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================= RESET (FIXED) =================
def reset_app():
    # We delete keys instead of assigning them to avoid StreamlitAPIException
    for k in list(st.session_state.keys()):
        if k in defaults:
            del st.session_state[k]
    st.cache_data.clear()
    st.rerun()

# ================= API HELPERS =================
@st.cache_data(show_spinner=False)
def get_lat_lon(city):
    if not city.strip():
        return [20.5937, 78.9629]
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        r = requests.get(url, headers={"User-Agent": "ai-travel-planner-student-app"}, timeout=5).json()
        if r:
            return [float(r[0]["lat"]), float(r[0]["lon"])]
        return [20.5937, 78.9629]
    except:
        return [20.5937, 78.9629]

@st.cache_data(show_spinner=False)
@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
def overpass(query):
    try:
        time.sleep(0.5)
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers={"User-Agent": "ai-travel-planner-student-app"},
            timeout=30
        )
        return r.json().get("elements", [])
    except:
        return []

def get_wikidata_places(lat, lon, radius=50000, limit=10):
    query = f"""
    SELECT ?placeLabel WHERE {{
      SERVICE wikibase:around {{
        ?place wdt:P625 ?coord .
        bd:serviceParam wikibase:center "Point({lon} {lat})"^^geo:wktLiteral .
        bd:serviceParam wikibase:radius "{radius/1000}" .
      }}
      ?place wdt:P31/wdt:P279* ?type .
      FILTER(?type IN (wd:Q570116, wd:Q33506, wd:Q839954)) 
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"User-Agent": "ai-travel-planner-student-app"}
    try:
        r = requests.get(url, params={"query": query, "format": "json"}, headers=headers, timeout=10)
        data = r.json()
        places = [item["placeLabel"]["value"] for item in data.get("results", {}).get("bindings", [])]
        return places
    except:
        return []

@st.cache_data(show_spinner=False)
def get_real_places(lat, lon, limit=12):
    query = f"""
    [out:json][timeout:30];
    (
      node["tourism"="attraction"](around:50000,{lat},{lon});
      node["historic"~"monument|castle|ruins"](around:50000,{lat},{lon});
      node["leisure"="park"](around:50000,{lat},{lon});
      node["tourism"="museum"](around:50000,{lat},{lon});
      node["tourism"="gallery"](around:50000,{lat},{lon});
      node["amenity"="theatre"](around:50000,{lat},{lon});
    );
    out;
    """
    places = []
    for e in overpass(query):
        tags = e.get("tags", {})
        name = tags.get("name")
        
        if not name:
            if tags.get("tourism"):
                name = f"Local {tags['tourism'].replace('_', ' ').title()}"
            elif tags.get("historic"):
                name = f"Historic {tags['historic'].replace('_', ' ').title()}"
            elif tags.get("leisure"):
                name = f"City {tags['leisure'].replace('_', ' ').title()}"
        
        if name and name not in places:
            places.append(name)

    if len(places) < limit:
        wikidata_places = get_wikidata_places(lat, lon, limit=limit)
        for wp in wikidata_places:
            if wp not in places:
                places.append(wp)

    if not places:
        places = ["City Center"] 

    return places[:limit]

@st.cache_data(show_spinner=False)
def get_real_hotels(lat, lon, limit=3):
    query = f"""
    [out:json][timeout:30];
    (
      node["tourism"~"hotel|hostel"](around:50000,{lat},{lon});
    );
    out;
    """
    hotels = []
    for e in overpass(query):
        name = e.get("tags", {}).get("name")
        if name and name not in hotels:
            hotels.append(name)
    return hotels[:limit] if hotels else ["City Center Inn"]

@st.cache_data(show_spinner=False)
def get_food_places(lat, lon):
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="fast_food"](around:50000,{lat},{lon});
      node["amenity"="restaurant"](around:50000,{lat},{lon});
    );
    out;
    """
    budget_set = set()
    premium_set = set()
    
    for e in overpass(query):
        tags = e.get("tags", {})
        name = tags.get("name")
        if not name:
            name = "Street Food" if tags.get("amenity")=="fast_food" else "Local Restaurant"
        else:
            name = name.title() 

        if tags.get("amenity") == "fast_food":
            budget_set.add(name)
        elif tags.get("amenity") == "restaurant":
            premium_set.add(name)
            
    budget = list(budget_set)
    premium = list(premium_set)
    
    return budget[:2] if budget else ["Street Food"], premium[:1] if premium else ["Popular Restaurant"]

def build_map(lat, lon, query, color, icon, fallback_names=None):
    m = folium.Map(location=[lat, lon], zoom_start=12)
    cluster = MarkerCluster().add_to(m)
    elements = overpass(query)

    if elements:
        for e in elements:
            if "lat" in e and "lon" in e:
                name = e.get("tags", {}).get("name", "Unnamed Location")
                folium.Marker(
                    [e["lat"], e["lon"]],
                    tooltip=name,
                    popup=name,
                    icon=folium.Icon(color=color, icon=icon)
                ).add_to(cluster)
    elif fallback_names:
        for i, name in enumerate(fallback_names):
            folium.Marker(
                [lat + i * 0.01, lon + i * 0.01],
                tooltip=name,
                popup=name,
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(cluster)
    else:
        folium.Marker(
            [lat, lon],
            popup="⚠️ No specific data found. Showing city center.",
            icon=folium.Icon(color="red")
        ).add_to(m)

    return m

def hotel_map(lat, lon):
    return build_map(lat, lon,
        f'[out:json];node["tourism"~"hotel|hostel"](around:50000,{lat},{lon});out;',
        "green", "home", ["City Hotel"])

def transport_map(lat, lon):
    return build_map(lat, lon,
        f'[out:json];node["amenity"="bus_station"](around:50000,{lat},{lon});out;',
        "blue", "road", ["Bus Station"])

def attraction_map(lat, lon):
    return build_map(lat, lon,
        f'[out:json];node["tourism"="attraction"](around:50000,{lat},{lon});out;',
        "orange", "star", ["Tourist Spot"])

def route_map(flat, flon, tlat, tlon):
    m = folium.Map(location=[(flat + tlat) / 2, (flon + tlon) / 2], zoom_start=6)
    folium.Marker([flat, flon], popup="From", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker([tlat, tlon], popup="To", icon=folium.Icon(color="green")).add_to(m)
    folium.PolyLine([(flat, flon), (tlat, tlon)], color="blue", weight=2.5, opacity=1).add_to(m)
    return m

def generate_plan(frm, dest, days, budget, members):
    to_lat, to_lon = get_lat_lon(dest)
    
    places = get_real_places(to_lat, to_lon)
    
    if len(places) > 1:
        random.shuffle(places)
    
    if not places:
        places = ["City Center"] 

    place_cycle = cycle(places)

    hotels = get_real_hotels(to_lat, to_lon)
    budget_food, premium_food = get_food_places(to_lat, to_lon)
    per_day = int(budget / days / members)

    md_plan = f"""
# ✈️ Student Trip: {dest}

**📍 From:** {frm}  
**📅 Duration:** {days} Days  
**👥 Members:** {members}  
**💰 Total Budget:** ₹{budget}  
**📊 Budget Per Day:** ₹{per_day}/person  

---

"""

    for d in range(1, days + 1):
        hotel = hotels[(d-1) % len(hotels)]
        morning = next(place_cycle)
        afternoon = next(place_cycle)
        evening = next(place_cycle)

        md_plan += f"""
## 🗓 Day {d}
**🏨 Stay:** {hotel}

**🗺 Daily Itinerary:**
*   🌅 **Morning:** Start your day at **{morning}**.
*   🌞 **Afternoon:** Head over to **{afternoon}**.
*   🌆 **Evening:** Relax at **{evening}**.

**🍽️ Food & Dining:**
*   **Budget Eats:** {', '.join(budget_food)}
*   **Premium Dinner:** {', '.join(premium_food)}

---

"""

    md_plan += f"""
## 💡 Student Tips
*   🚌 **Transport:** Use local buses or metro to save money.
*   🆔 **Discounts:** Always carry your Student ID card for museum entries.
*   🍛 **Food:** Try street food for lunch; it's cheaper and authentic!
"""
    return md_plan

# ================= UI =================
st.info("ℹ️ This app uses free OpenStreetMap & Wikidata APIs. It may take a few seconds to fetch real location data.")

c1, c2, c3 = st.columns(3)
with c1:
    from_loc = st.text_input("📍 From (City)", st.session_state.from_location)
with c2:
    dest_loc = st.text_input("📍 To (Destination)", st.session_state.destination)
with c3:
    days_trip = st.number_input("📅 Days", 1, 15, st.session_state.days)

c4, c5 = st.columns(2)
with c4:
    budget_trip = st.number_input("💰 Total Budget (₹)", 1000, step=500, value=st.session_state.budget)
with c5:
    members_trip = st.number_input("👥 Members", 1, 10, st.session_state.members)

col_control_left, col_control_right = st.columns([1, 1])

with col_control_left:
    st.markdown("**🌟Select the features below to make your journey friendly! 🚀**")
    show_route = st.checkbox("🗺️ Show Route Map", key="show_route")
    show_hotels = st.checkbox("🏨 Show Hotels Map", key="show_hotels")
    show_transport = st.checkbox("🚕 Show Transport Map", key="show_transport")
    show_attractions = st.checkbox("🎡 Show Attractions Map", key="show_attractions")

with col_control_right:
    st.markdown("**⚡Actions:**")
    if st.button("✨ Generate Plan", use_container_width=True):
        if from_loc and dest_loc:
            st.session_state.from_location = from_loc
            st.session_state.destination = dest_loc
            st.session_state.days = days_trip
            st.session_state.budget = budget_trip
            st.session_state.members = members_trip
            
            with st.spinner("⏳ Fetching real data and generating your plan..."):
                time.sleep(1) 
                st.session_state.plan = generate_plan(
                    from_loc, dest_loc, days_trip, budget_trip, members_trip
                )
            st.success("✅ Plan generated successfully!")
        else:
            st.warning("⚠️ Please enter both 'From' and 'Destination' cities.")

    if st.button("🔄 Reset App", use_container_width=True):
        reset_app()

if st.session_state.plan:
    st.markdown("---")
    st.markdown(st.session_state.plan)
    st.markdown("---")

    to_lat, to_lon = get_lat_lon(st.session_state.destination)
    from_lat, from_lon = get_lat_lon(st.session_state.from_location)

    if show_route:
        st.subheader("🗺️ Route Map")
        st_folium(route_map(from_lat, from_lon, to_lat, to_lon), width=1000, height=450)

    if show_hotels:
        st.subheader("🏨 Nearby Hotels")
        st_folium(hotel_map(to_lat, to_lon), width=1000, height=450)

    if show_transport:
        st.subheader("🚕 Transport Hubs")
        st_folium(transport_map(to_lat, to_lon), width=1000, height=450)

    if show_attractions:
        st.subheader("🎡 Top Attractions")
        st_folium(attraction_map(to_lat, to_lon), width=1000, height=450)

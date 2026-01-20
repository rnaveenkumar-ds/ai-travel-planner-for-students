
# 🌍 AI Travel Planner for Students 🎓

An **AI-powered, student-friendly travel planning application** built with **Streamlit**, **OpenStreetMap**, and **Wikidata** that generates **real, budget-aware travel plans with interactive maps** — all using **free APIs (no billing required)**.

---

## 🚀 Features

✨ **Smart Day-wise Travel Plan**

* Morning, Afternoon & Evening activities
* Budget-aware suggestions
* Student-friendly itineraries

🗺️ **Interactive Maps**

* Destination map
* Attractions map
* Hotels map
* Transportation map

📍 **Real Place Names (No Dummy Data)**

* OpenStreetMap (OSM)
* Wikidata enrichment for accurate attractions, parks & museums

🍽️ **Food Recommendations**

* Budget-friendly local street food
* Popular premium restaurants

🎛️ **Customizable Actions**

* Toggle maps as needed
* Lightweight & fast UI

💯 **100% Free APIs**

* No OpenAI
* No Google Maps billing
* No paid AI services

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit** – UI & deployment
* **Folium** – Interactive maps
* **OpenStreetMap (OSM)** – Location data
* **Wikidata SPARQL** – Real-world place enrichment
* **Requests** – API calls

---

## 📸 Screenshots (Optional)

> Add screenshots or GIFs here for better visibility
> Example:

```
/assets/home.png
/assets/maps.gif
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App

```bash
streamlit run app.py
```

---

## 📦 requirements.txt

```txt
streamlit
folium
streamlit-folium
requests
geopy
tenacity
```

---

## 🧠 How It Works

1. User selects destination, budget, days, and group size
2. App fetches:

   * Locations from **OpenStreetMap**
   * Missing/real names from **Wikidata**
3. AI logic generates a **structured day-wise plan**
4. Maps are displayed interactively based on selected actions

---

## 🌟 Why This Project?

✔ Perfect for **students**
✔ Ideal for **hackathons & resumes**
✔ Uses **real-world data**
✔ Zero API cost
✔ Easy to extend

---

## 🔮 Future Scope

* 🤖 AI-based personalized recommendations
* 💬 Chat-style travel assistant
* 🧾 PDF itinerary download
* 🌐 Multi-language support
* 📱 Mobile-first UI improvements
* 🌦️ Weather-aware planning

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Open a pull request
---

## 🙌 Acknowledgements

* OpenStreetMap Contributors
* Wikidata Community
* Streamlit Team
✅ Conclusion

The AI Travel Planner for Students demonstrates how free, open-source data and smart AI logic can be combined to build a real-world, budget-friendly travel planning solution. By leveraging OpenStreetMap and Wikidata, the application avoids paid APIs while still delivering accurate locations, meaningful recommendations, and interactive maps.

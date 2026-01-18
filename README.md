# 🎓 AI Travel Planner for Students

A **Streamlit-based AI Travel Planner** that helps students create **budget-friendly, real, and day-wise travel plans** using **live map data**, **real hotels**, and **nearby attractions** — all without paid APIs.

---

## 🚀 Project Overview

Planning trips can be stressful for students due to limited budgets and lack of personalized guidance.
This project solves that problem by providing:

* 📍 **Real destination-based planning**
* 🗓 **Day-by-day itinerary**
* 🏨 **Real hotels & hostels**
* 🎡 **Nearby attractions**
* 🚕 **Public transport locations**
* 🗺 **Interactive maps**
* 🔄 **One-click reset**

Built with **Python + Streamlit + OpenStreetMap (Overpass API)** and runs smoothly in **VS Code**.

---

## ✨ Key Features

### 🧠 Smart Day-Wise Travel Plan

* Automatically divides the trip into **morning, afternoon, and evening**
* Suggests **real places to visit each day**
* Calculates **budget per day per person**

### 🏨 Real Hotels & Hostels

* Fetches **actual hotel and hostel names**
* Displayed on an **interactive map** with clustered markers

### 🎡 Tourist Attractions

* Monuments, parks, attractions, and marketplaces
* Based on **real OpenStreetMap data**

### 🚕 Public Transport Map

* Shows nearby **bus stations and transport hubs**
* Helps students plan **low-cost travel routes**

### 🗺 Interactive Maps

* Zoomable and clickable maps using **Folium**
* Clustered markers for cleaner visualization

### 🔄 Reset Planner

* One click to reset all inputs and results
* Useful for demos and repeated testing

---

## 🛠️ Tech Stack

| Technology                       | Purpose                  |
| -------------------------------- | ------------------------ |
| **Python**                       | Core logic               |
| **Streamlit**                    | Web UI                   |
| **Folium**                       | Interactive maps         |
| **OpenStreetMap (Overpass API)** | Real-world location data |
| **VS Code**                      | Development environment  |

---

## 📂 Project Structure

```
AI_Travel_Planner/
│
├── app.py          # Main Streamlit application
├── README.md       # Project documentation
├── requirements.txt
└── .venv/          # Virtual environment
```

---

## ⚙️ Installation & Setup (VS Code)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/AI_Travel_Planner.git
cd AI_Travel_Planner
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

### 3️⃣ Activate Environment

**Windows (PowerShell):**

```bash
.venv\Scripts\activate
```

> If script execution is blocked:

```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 4️⃣ Install Dependencies

```bash
pip install streamlit folium streamlit-folium requests
```

### 5️⃣ Run the App

```bash
streamlit run app.py
```

---

## 🧪 How to Use

1. Enter a **destination** (e.g., Manali)
2. Select **number of days**
3. Enter **total budget**
4. Choose **number of members**
5. Click **✨ Generate Plan**
6. Enable maps using checkboxes
7. Use **🔄 Reset Planner** to start over

---

## 📸 Output Includes

* 📄 **Detailed day-wise itinerary**
* 🏨 **Hotels map**
* 🚕 **Transport map**
* 🎡 **Attractions map**

---

## 🔒 API Information

✅ **No paid APIs used**
✅ Uses **free OpenStreetMap Overpass API**
✅ No API keys required

---

## 📈 Future Enhancements

* 🌐 Auto-detect any city worldwide
* 🧭 Route & distance optimization
* 📊 Budget charts and analytics
* 📱 Mobile UI optimization
* 🤖 ML-based preference learning
* 🏕 Category-based travel (adventure, culture, relaxation)

---

## 🙌 Acknowledgements

* OpenStreetMap Community
* Streamlit Team
<<<<<<< HEAD
* Folium Contributors
=======
* Folium Contributors
  
---

## 🔮 Future Scope

While the **AI Travel Planner for Students** is fully functional and helpful, there are several ways it can be **enhanced and expanded** in the future:

* 🌐 **Global Destination Support** – Automatically detect and plan trips for **any city worldwide**.
* 🧭 **Route & Distance Optimization** – Suggest **shortest routes** between attractions to save time and money.
* 📊 **Budget Analytics** – Provide **charts and graphs** for daily and overall spending.
* 🏕 **Category-Based Travel** – Personalized itineraries for **adventure, cultural, or relaxation trips**.
* 🤖 **AI-Powered Recommendations** – Use ML or LLMs to suggest **places, hotels, and activities** based on user preferences.
* 📱 **Mobile-Friendly UI** – Optimized interface for **smartphones and tablets**.
* 🌦 **Dynamic Weather Integration** – Incorporate **forecast-based activity suggestions**.
* 🚌 **Transport Routing** – Include **bus, train, or metro routes** with estimated travel times.

---

## 📝 Conclusion

The **AI Travel Planner for Students** is a **lightweight, interactive, and fully free tool** that simplifies trip planning for students. By integrating **real-world data, interactive maps, and personalized day-wise itineraries**, it allows users to:

* Save time and reduce stress while planning trips
* Optimize budget per person and per day
* Explore attractions, hotels, and transport options with ease
>>>>>>> a47fb5663b5560a5874c229b3dd62bdf700c0352

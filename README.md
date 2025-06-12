# 🌬️ Wind Turbine Manager

## 📌 Project Overview

**Wind Turbine Manager** is a web application designed to monitor a wind turbine park using modern APIs and technologies. It provides users with an intuitive interface for:

- Registering and logging into their accounts
- Adding wind turbines to a map (OpenStreetMap)
- Tracking turbine revision schedules and power output
- Viewing real-time wind speed and turbine performance (via Weather API)
- Accessing energy production and consumption data for Romania (via Electricity Map API)

All data is stored in a scalable MongoDB database, and the application is hosted on [Render.com](https://project-windturbinemanager.onrender.com/login/), making it accessible from anywhere.

---

## ⚙️ Technologies Used

- **Backend Framework:** Django (Python)
- **RESTful API:** Django Rest Framework
- **Database:** MongoDB (NoSQL)
- **Hosting Platform:** Render.com
- **External APIs:**
  - OpenStreetMap API (for map integration)
  - Weather API (for wind data)
  - Electricity Map API (for national energy data)

---

## ✅ Features

- 🔐 **User Management:** Register and log in securely
- 🗺️ **Map Integration:** Add and locate turbines on a real map
- 🌬️ **Real-Time Weather:** Display wind speed and instantaneous power for each turbine
- ⚡ **Energy Dashboard:** Visualize Romania’s energy production and consumption
- 🔁 **Turbine Maintenance:** Keep track of the last revision date for each unit
- 📦 **REST API:** Use custom endpoints for frontend/backend communication
- ☁️ **Cloud Hosting:** Accessible from any device, 24/7

---

## 🧭 Application Flow

1. User registers/logs in
2. Adds wind turbines to the map
3. Views turbine details, including:
   - Location
   - Last maintenance date
   - Current wind speed and power (via Weather API)
4. Accesses Romania’s electricity production and consumption data (Electricity Map API)
5. All information is stored and retrieved using a MongoDB backend
![image](https://github.com/user-attachments/assets/335e011b-00fb-43fa-911d-54fb6d9dcaa6)


---

## 📸 Screenshots & Diagrams

- **User Management Flow**
![image](https://github.com/user-attachments/assets/345bfd5e-4ba5-42ca-ab8d-e8b89a158e02)
- **API Implementation Diagram**
![image](https://github.com/user-attachments/assets/f476e6cd-0051-4d91-903d-64402c759620)
- **Login UI**
![image](https://github.com/user-attachments/assets/8501a2a5-01e4-455f-b833-a60f2238423b)
- **Register UI**
![image](https://github.com/user-attachments/assets/5a4d917e-1faa-44c7-81cb-ebc2e7c7c5f5)
- **Main Dashboard with Map**
![image](https://github.com/user-attachments/assets/6b5b6cc4-6f87-46fe-932b-d35617def9f2)
- **MongoDB Database View**
![image](https://github.com/user-attachments/assets/888bda6d-a1db-44c9-a480-f16d85a16b84)
- **API Endpoint Overview**
![image](https://github.com/user-attachments/assets/e52e3f8a-a0de-4dab-b557-256f6ed2a2bd)
- **Energy Data Dashboard from Electricity Map API**
![image](https://github.com/user-attachments/assets/27d17288-eb94-4e3c-8c84-3bcb3d210960)

---

## 🌍 Deployment

The app is deployed on [Render.com]([https://render.com](https://project-windturbinemanager.onrender.com/login/)).  
Once deployed, it can be accessed via the public URL provided in your Render dashboard.

---
## 🔌 API Endpoints (Examples)

- `GET /api/turbines/` – List all turbines
- `POST /api/turbines/` – Add a new turbine
- `GET /api/weather/<location>` – Get wind data
- `GET /api/electricity/romania` – Get national energy stats

---

## 🙌 Acknowledgments

- Django & Django Rest Framework
- OpenStreetMap
- Electricity Map API
- OpenWeather (or similar Weather API)
- Render.com for free student hosting

---



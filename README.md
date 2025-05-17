# 🛠️ Fixly Webskitters – Local Service Provider Backend (Django + DRF + JWT)

This is the backend for **Fixly Webskitters**, a local service booking platform built using **Django**, **Django REST Framework**, and **JWT authentication**. It supports **customer and service provider registration**, **login/logout with JWT**, **booking time slots**, and **user reviews** – all via secured REST APIs.

---

> 🚀 **Live Backend API**: [https://fixlywebskitters-production-ebff.up.railway.app](https://fixlywebskitters-production-ebff.up.railway.app)  
> 📬 **Postman Collection**: [View on Postman](https://documenter.getpostman.com/view/44342859/2sB2j7eVGw)  
> 🧑‍💻 **GitHub Repo**: [https://github.com/Mdaliraza1/fixly_webskitters](https://github.com/Mdaliraza1/fixly_webskitters)

---

## 📌 Key Features

- 🔐 JWT Authentication (Login, Logout, Token Refresh)
- 👤 Customer & Service Provider User Roles
- 📅 Secure Booking System (1-hour slots, 10 AM – 6 PM)
- 🔁 No Double Booking
- ⭐ Reviews and Ratings for Providers
- 📧 Regex Validation for Email and Mobile
- 🛠️ Admin Dashboard Support
- 🌍 Hosted on Railway

---

## ⚙️ Tech Stack

| Tech        | Description                   |
|-------------|-------------------------------|
| Django      | Backend Web Framework         |
| DRF         | Django REST Framework         |
| JWT         | Authentication (Token-based)  |
| PostgreSQL  | Relational Database           |
| Railway     | Cloud Deployment              |
| Postman     | API Testing & Documentation   |

---

## 📂 Project Structure

fixly_webskitters/
│
├── booking/ # Booking logic (slots, appointments)
├── registration/ # Custom User Model, login, register
├── services/ # Service categories
├── reviews/ # Reviews and ratings
├── authentication.py # Custom JWT handling
├── manage.py
└── README.md


---

## 🔐 Authentication Endpoints

| Method | Endpoint                  | Description                      |
|--------|---------------------------|----------------------------------|
| POST   | `/register/customer/` | Register new customer            |
| POST   | `/register/provider/` | Register new service provider    |
| POST   | `/login/`             | Login and get JWT token          |
| POST   | `/logout/`            | Logout and blacklist token       |
| POST   | `/token/refresh/`     | Refresh JWT token                |

---

## 📅 Booking Endpoints

| Method | Endpoint                                               | Description                             |
|--------|--------------------------------------------------------|-----------------------------------------|
| POST   | `/bookings/`                                       | Book a 1-hour slot                      |
| GET    | `/bookings/?user_type=customer`                    | Get bookings for customer               |
| GET    | `/bookings/?user_type=provider`                    | Get bookings for provider               |
| GET    | `/available-slots/?provider_id=&date=`             | Get available slots for given provider |

---

## ⭐ Reviews Endpoints

| Method | Endpoint                           | Description                      |
|--------|------------------------------------|----------------------------------|
| POST   | `/reviews/`                    | Post review (customer only)      |
| GET    | `/reviews/?provider_id=1`      | Get all reviews for provider     |

---

## 🧪 API Testing with Postman

Use the public Postman Collection below to test all APIs:

🔗 **Postman Link**: [Fixly Webskitters Collection](https://documenter.getpostman.com/view/44342859/2sB2j7eVGw)

### 🔑 Authorization

Set `Authorization` header:
Use login API to get the JWT `access_token`.
---
## 🖥️ Local Setup Instructions
### 1. Clone the Repository

```bash```

git clone https://github.com/Mdaliraza1/fixly_webskitters.git
cd fixly_webskitters
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

---

🚀 Deployment on Railway

The project is deployed live using Railway
🔗 Live URL: https://fixlywebskitters-production-ebff.up.railway.app
The API is publicly available.
Frontend (React/Bootstrap) can consume the live endpoints easily.
.env secrets are securely managed via Railway dashboard.

👨‍💻 Author
MD Ali Raza
📍 Python & Django Backend Developer
🔗 GitHub: @Mdaliraza1

# 🎓 Full-Stack Udemy Clone (LMS Platform)

A full-stack Learning Management System (LMS) built with **FastAPI**, **React (Vite)**, **PostgreSQL**, and **Cloudinary**. This platform features user authentication, media streaming, course curriculum management, student review systems, and an instructor financial engine with an 80/20 revenue split.

---

## ✨ Features

### 👤 Student Experience
* **Course Catalog & Filtering**: Search and filter courses across categories (Web Dev, Data Science, etc.).
* **Dummy Checkout Flow**: Interactive modal (`CheckoutModal.jsx`) for dummy credit card checkout with duplicate enrollment protection and instant redirection to "My Learning".
* **Video Classroom Player**: Video player supporting section navigation, lesson selection, and completion tracking.
* **Ratings & Reviews**: Enrolled students can leave 1-to-5 star reviews with comments.

### 👨‍🏫 Instructor Portal
* **Course & Curriculum Management**: Create courses, add sections, and upload lesson videos.
* **Direct Cloud Storage**: Cloudinary integration for video and thumbnail image uploads.
* **Financial Ledger & Analytics**: Track Gross Sales, Net Earnings (80% share), and Available Balance in real time.
* **Payout Request Simulator**: Request withdrawals to PayPal or bank accounts, updating account balances automatically.

---

## 🛠️ Tech Stack

* **Backend**: FastAPI (Python 3.10+), SQLAlchemy, Pydantic, PostgreSQL, Cloudinary SDK.
* **Frontend**: React (Vite), React Router v6, Axios, Modern CSS.
* **Authentication**: JWT (JSON Web Tokens), Passlib (Bcrypt hashing), OTP verification.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+ installed
* Node.js v18+ and npm installed
* PostgreSQL instance running

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
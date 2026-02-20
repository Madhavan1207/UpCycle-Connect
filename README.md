# ♻️ UpCycle Connect
### *AI-Driven Waste Management & Sustainable Exchange*

**UpCycle Connect** is a 2026-gen platform designed to bridge the gap between waste generation and creative reuse. It simplifies the process of "Waste-to-Wealth" by connecting eco-conscious users and providing real-time AI guidance on how to repurpose materials.

---

## 🎯 What exactly is this for?

The world generates billions of tons of waste annually, much of which can be repurposed. **UpCycle Connect** was built to:
1.  **Educate**: Use AI to tell users exactly what they can make with specific trash items.
2.  **Gamify**: Encourage recycling through an Impact Dashboard and Leaderboard.
3.  **Modernize**: Provide a sleek, glass-themed user experience that makes sustainability feel high-tech.

---

## ✨ Core Functionality

### 🤖 The AI Eco-Warrior (Powered by Groq)
Our integration with **Llama 3.3** allows users to input any item—from plastic bottles to old tires—and receive immediate, step-by-step upcycling instructions. 
* **Speed**: Responses are delivered in milliseconds via Groq's LPUs.
* **Intelligence**: Provides creative, DIY-friendly projects tailored to the material.

### 💎 Glassmorphism Interface
The UI uses a cutting-edge "Glass" aesthetic to ensure the platform feels clean and eco-friendly:
* **Pill-Shaped Inputs**: Optimized for focus and high readability.
* **Responsive Rows**: A custom-engineered registration flow with perfectly aligned input fields.
* **Dynamic Focus**: Interactive green glow effects that guide the user's eye.

### 📊 Sustainability Tracking
* **User Accounts**: Securely stores recycling history using SQLite and SQLAlchemy.
* **Security**: Multi-layer protection using `.env` files to prevent API key leaks.

---

## 🛠️ Built With

* **Python (Flask)**: The robust backend engine.
* **Groq LPU Inference**: Powering the lightning-fast AI Eco-Warrior.
* **Bootstrap 5 & Custom CSS**: For the high-fidelity Glassmorphism design.
* **SQLAlchemy**: Managing the "Eco-Warrior" database.

---

## 🚀 How to Run Locally

1. **Clone the Repo**
   ```bash
   git clone [https://github.com/Madhavan1207/UpCycle-Connect.git](https://github.com/Madhavan1207/UpCycle-Connect.git)
Setup Secrets
Create a .env file and add: GROQ_API_KEY=your_key.

Install & Launch

pip install -r requirements.txt
python app.py

**Developed by Madhavan — Innovating for a cleaner planet**

# 🌱 NGO Donation Automation System

## 📌 Project Overview

The **NGO Donation Automation System** is a full-stack solution designed to streamline donation management and donor communication for non-governmental organizations (NGOs). The system automates donor data collection, storage, and WhatsApp-based messaging, significantly reducing manual effort and improving operational efficiency.

This project is particularly useful for NGOs that handle frequent donations and need a simple, cost-effective way to manage donor interactions.

---

## 🚀 Features

* ✅ Automated WhatsApp thank-you messages after each donation
* 📢 Bulk broadcast messaging to donors
* 📊 Donation tracking using Excel
* 🔐 QR-based WhatsApp authentication
* 🌐 Simple and user-friendly web interface
* ⚡ Real-time data handling between frontend and backend

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask)
* **Messaging Service:** Node.js (WhatsApp Web API)
* **Database:** Excel (.xlsx file)

---

## ⚙️ System Architecture

```
Frontend (Web Form)
        ↓
Python Backend (API)
        ↓
Excel File (Data Storage)
        ↓
Node.js WhatsApp Service
        ↓
WhatsApp Messages Sent to Donors
```

---

## 📂 Project Structure

```
NGO-Donation-Automation-System/
│
├── app/                    # Backend logic
├── whatsapp-service/       # Node.js WhatsApp integration
├── data/                   # Excel storage for donations
├── static/                 # CSS, JS files
├── templates/              # HTML frontend
├── START.bat               # Script to start the project
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## ⚡ Installation & Setup

### 🔹 Prerequisites

* Python (3.x)
* Node.js
* Git

### 🔹 Steps to Run

1. **Clone the repository**

```
git clone <your-repo-link>
cd NGO-Donation-Automation-System
```

2. **Install Python dependencies**

```
pip install -r requirements.txt
```

3. **Setup WhatsApp Service**

```
cd whatsapp-service
npm install
```

4. **Run the project**

* Option 1: Double-click `START.bat`
* Option 2 (manual):

```
# Start backend
python app.py

# Start WhatsApp service
cd whatsapp-service
node index.js
```

5. **Scan QR Code**

* A QR code will appear in the terminal
* Scan it using WhatsApp on your phone

6. **Open in Browser**

```
http://localhost:5000
```

---

## 🎯 Use Case

This system helps NGOs:

* Reduce manual effort in donor communication
* Maintain structured donor records
* Instantly send personalized thank-you messages
* Improve donor engagement and trust

---

## 🔄 Workflow

1. User enters donation details on the website
2. Data is stored in an Excel file
3. Backend processes the request
4. WhatsApp service sends a thank-you message
5. Admin can send broadcast messages when needed

---

## 🔮 Future Scope

* 🚀 Replace Excel with MongoDB/MySQL
* 📊 Add analytics dashboard for NGOs
* ☁️ Deploy on cloud (AWS/Render)
* 👥 Multi-user/admin support
* 📱 Mobile-friendly UI

---

##  Screenshots
<img width="1889" height="933" alt="image" src="https://github.com/user-attachments/assets/6eb4c05a-6bd3-4130-ac2e-e11c3f15e062" />
<img width="1875" height="1013" alt="image" src="https://github.com/user-attachments/assets/5407c574-b67b-4993-9561-2d149b4e4416" />
<img width="1873" height="1013" alt="image" src="https://github.com/user-attachments/assets/7e6feb17-319f-4558-82bb-67b34e30a091" />


---

## 🤝 Contribution

Contributions are welcome! Feel free to fork this repository and submit a pull request.

---

## ⭐ Final Note

This project demonstrates how automation and simple technologies can significantly improve NGO operations by reducing manual workload and enhancing communication efficiency.
"# Donation-Automation-System" 

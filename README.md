# Metro Abashik Hotel Management System 🏨

A comprehensive web-based application designed to streamline hotel operations, including room management, booking handling, check-in/check-out workflows, and automated invoicing.

🔗 **Live Demo:** [metro-abashik-hotel.onrender.com](https://metro-abashik-hotel.onrender.com)

## 🚀 Features

* **Room Management:**
    * **CRUD Operations:** Admins can Add, Update, and Delete rooms.
    * Manage room categories, pricing, and availability.
* **Booking System:**
    * Seamless **Check-in** and **Check-out** processes.
    * Real-time room availability status.
    * Booking history for customers.
* **Billing & Invoicing:**
    * Automated bill calculation based on stay duration.
    * **PDF Invoice Generation:** Generates professional PDF receipts upon checkout.
* **Email Integration (SMTP):**
    * Automated email notifications for booking confirmations.
    * Sends digital invoices directly to the customer's email.
* **User Management:**
    * Secure authentication for Admins and Customers.
    * Dedicated Dashboards for managing profiles and bookings.

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Frontend:** HTML5, CSS3, JavaScript
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Tools:** `wkhtmltopdf` (for PDF generation), SMTP (Email)

## ⚙️ Prerequisites

Before running the project, ensure you have the following installed:

1.  **Python 3.10+**
2.  **wkhtmltopdf** (Required for generating PDF invoices)
    * *Linux (Arch):* `yay -S wkhtmltopdf-bin`
    * *Ubuntu/Debian:* `sudo apt-get install wkhtmltopdf`
    * *Windows:* Download installer from the official website.

## 📦 Installation Guide

Follow these steps to set up the project locally:

**1. Clone the Repository**
```bash
git clone [https://github.com/beingnayem/metro-abashik-hotel.git](https://github.com/beingnayem/metro-abashik-hotel.git)
cd metro-abashik-hotel

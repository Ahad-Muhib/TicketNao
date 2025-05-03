# TicketNao

A modern, minimal, and user-friendly bus ticket booking system built with Django.

## Features
- Search and book bus tickets online
- User registration, login, and profile management
- Admin dashboard for managing operators, buses, schedules, and bookings
- Responsive, clean, and accessible UI
- Minimal white theme with modern accent colors
- Alerts, prompts, and status badges for clear feedback

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- (Recommended) Virtual environment tool: `venv` or `virtualenv`

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ahad-Muhib/TicketNao.git
or download the zip-->extract.
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate   #On Mac: source venv/bin/activate 
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (admin):**(there's already an option with:
username: admin
password: admin123
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the app:**
   - User site: [http://localhost:8000/](http://localhost:8000/)
   - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## Usage
- Register as a user to book tickets.
- Admins can manage operators, buses, schedules, and bookings from the dashboard.
- The UI is fully responsive and works on all modern browsers.

## Project Structure
- `TravelBusBooker/` - Main Django project folder
- `travelbooker/` - Core app with models, views, templates, and static files
- `requirements.txt` - Python dependencies
- `manage.py` - Django management script

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

**TicketNao** — The best way to book bus tickets online in Bangladesh. Travel with comfort and safety. 

# Barber Booking App

This project simulates a real-world barbershop management system where customers can schedule appointments
and barbers can track bookings and analyze business activity.

A full-stack web application that allows customers to book barber appointments online, while enabling 
barbers to manage their schedules and view business statistics through an integrated dashboard.


## Features

- User registration and login with secure password hashing
- Customers can book appointments with specific barbers
- Barbers can view and manage their scheduled appointments
- Edit or cancel existing appointments
- Business dashboard displaying appointment and barber statistics
- SQLite database for persistent data storage
- Modular Flask architecture using Blueprints


  ## Tech Stack
  - Python
  - Flask
  - SQLite
  - HTML
  - CSS

 
  ## Screenshots

  ### Home Page
  ![Home Page](screenshots/home.png)

  ### Barbers
  ![Barbers](screenshots/barbers.png)

  ### Barber Profile
  ![Barber Profile](screenshots/barber_profile.png)

  ### Booking Form
  ![Booking Form](screenshots/booking_form.png)

  ### Appointments
  ![Appointments](screenshots/appointments.png)

  ### Dashboard
  ![Dashboard](screenshots/dashboard.png)

  ### Login
  ![Login](screenshots/login.png)

  ### Signup
  ![Signup](screenshots/signup.png)


## Project Structure
```
barber-booking-app/
├── app.py
├── auth.py
├── appointments.py
├── db.py
├── helpers.py
├── main.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── barbers.html
│   ├── barber_profile.html
│   ├── appointments.html
│   ├── edit.html
│   └── dashboard.html
│
├── static/
│   ├── styles.css
│   └── barbers/
│
└── database.db  (created automatically)
```

     
  ## Run Locally
  
  Clone the repository:

  git clone https://github.com/mabebeta/barber-booking-app.git

  Navigate into the project folder:

  cd barber-booking-app

  Run the application:

  python app.py

  Then open your browser and go to:

  http://127.0.0.1:5000


  ## Author
  Marcelo Berrio Betancur

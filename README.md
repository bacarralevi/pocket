# 💰 Budget Tracker

Pocket is a Django-based web app built using Python, HTML, CSS, and JavaScript. 
It allows users to log in, set budgets, record transactions, and view them with filter and sort options. 
The UI is clean and fully responsive across devices, including mobile. 
We used only basic web technologies (no advanced frameworks), 
and the project is structured using Django’s MVC pattern. 
A virtual environment (venv) is used for dependency management, 
and all frontend assets are organized under the static and templates folders.

## 📦 Installation Guide

### 🪟 For **Windows** Users:

1. **Install `venv` (if not already available):**

   `venv` is included by default with Python 3. Just make sure Python is installed.

2. Create a virtual environment:

  python -m venv venv

3. **Navigate to the project folder:**

   cd budgettracker

4. Activate the virtual environment:

  .\venv\Scripts\activate

You should see (venv) appear in your terminal.

5. Install Django:

  pip install django

6. Run the development server:

  python manage.py runserver

Or to make it accessible on your local network:

  python manage.py runserver 0.0.0.0:8000

-------------------------------------------------
###🍏 For macOS/Linux Users:
Install venv:

1. Usually included with Python 3. If not, install it via:

  sudo apt install python3-venv   # For Ubuntu/Debian

2. Navigate to the project folder:

  cd budgettracker
  
3. Create a virtual environment:

  python3 -m venv venv

4. Activate the virtual environment:

  source venv/bin/activate

5. Install Django:

  pip install django

6. Run the development server:

  python manage.py runserver

Or for LAN access:

  python manage.py runserver 0.0.0.0:8000

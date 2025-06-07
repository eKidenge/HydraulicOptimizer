# HydraulicOptimizer

**HydraulicOptimizer** is a Django-based web application designed to assist engineers, researchers, and field experts in optimizing hydraulic systems through data-driven analysis and user-friendly tools.

## 🚀 Features

- 🌊 Hydraulic parameter input and management
- 📊 Real-time computation and optimization of hydraulic models
- 📁 Data storage and retrieval using a robust backend
- 🧠 Integration-ready for machine learning-based predictive models
- 📉 Visualization of optimization results

## 🔧 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript (or any template engine used)
- **Database:** SQLite (default), easily configurable to PostgreSQL or MySQL
- **Version Control:** Git & GitHub

## 📁 Project Structure

HydraulicOptimizer/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── HydraulicOptimizer/
│   └── [Django project files]
├── optimization/
│   ├── admin.py
│   ├── models.py         # OptimizationResult model
│   ├── forms.py          # Input form for web UI
│   ├── views.py          # index & results views
│   ├── urls.py           # app routing
│   ├── optimizer.py      # EPANET & wntr-based logic
│   ├── templates/
│   │   └── optimization/
│   │       ├── index.html
│   │       └── results.html
│   ├── static/
│   │   └── optimization/style.css
│   └── management/
│       └── commands/run_optimization.py


## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/eKidenge/HydraulicOptimizer.git
   cd HydraulicOptimizer
Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

Install dependencies
pip install -r requirements.txt

Apply migrations
python manage.py migrate

Run the development server
python manage.py runserver

Open in browser: http://127.0.0.1:8000

🙋‍♂️ Author
Elisha Kidenge Odhiambo
GitHub: @eKidenge


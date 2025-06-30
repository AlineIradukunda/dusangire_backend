
**Dusangire Lunch – Backend**

**Overview**

The **Dusangire Lunch Backend** is a secure, RESTful API built with Django and Django REST Framework, serving as the core engine for managing contributions, distributions, and school data related to the Rwandan school feeding program. This backend connects with the React frontend, handles business logic, and interacts with a PostgreSQL database for persistent data storage.

It supports:

* Admin and superuser role-based access
* Data upload and management via API
* PDF and Excel report generation
* Secure user authentication
* Soft deletion workflows with approval logic

Built with powerful technologies:

* Django
* Django REST Framework
* PostgreSQL
* Django CORS Headers
* ReportLab & Pandas (for reporting)
* Docker (for deployment)

---

**Key Features**

*  **Role-based Authentication** for Admin and Superuser
*  **CRUD API Endpoints** for Schools, Transfers, Distributions, and Reports
*  **Excel Upload Support** using `pandas`
*  **Report Generation** in PDF & Excel formats
*  **Soft Deletion Workflow**: Admins can request delete; only superusers approve or permanently delete
*  **Filtered & Searchable Endpoints**
*  **PDF Report Builder** with total summaries and contributors’ details
*  **Dockerized Environment** for easy deployment

---

### **API Endpoints**

| Endpoint                    | Method    | Description                   |
| --------------------------- | --------- | ----------------------------- |
| `/api/schools/`             | GET, POST | List or create schools        |
| `/api/transfers/`           | GET, POST | List or add new contributions |
| `/api/distributions/`       | GET, POST | View or create distributions  |
| `/api/reports/`             | GET, POST | View or generate reports      |
| `/api/transfers/upload/`    | POST      | Upload transfer Excel files   |
| `/api/reports/generate/`    | POST      | Generate a new report         |
| `/api/transaction-summary/` | GET       | Get balance and summary info  |

---

**Project Structure**

```
dusangire_backend/
│
├── dusangire/                 # Django project core
│   ├── settings.py            # Project settings
│   ├── urls.py                # Global URL configuration
│
├── core/                      # Main app for APIs
│   ├── models.py              # School, TransferReceived, Distribution, Report models
│   ├── serializers.py         # DRF Serializers
│   ├── views.py               # API logic
│   ├── urls.py                # App-specific routes
│   ├── utils/                 # PDF generation, Excel parsing helpers
│
├── manage.py
├── Dockerfile
├── requirements.txt
```

---

**Running the Backend**

```bash
# Clone the repo
git clone https://github.com/your-username/dusangire-backend.git
cd dusangire-backend

# Set up virtual environment
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Migrate the database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

---

### **Run with Docker**

```bash
# Build and run the backend container
docker build -t dusangire-backend .
docker run -d -p 8000:8000 dusangire-backend
```

Access the API at:
**`http://localhost:8000/api/`**


# epidemic-management-system


##  Project Overview

The **Epidemic Management System** is a full-stack web application developed using **Flask, MySQL, HTML, CSS, and Bootstrap**.
It is designed to manage patients, disease outbreaks, healthcare resources, and analytical insights in a centralized database-driven system.

This project demonstrates core concepts of:

* Database Management Systems (DBMS)
* Full Stack Web Development
* Role-Based Access Control
* CRUD Operations
* Data Analysis using SQL joins

---

##  Features-->

###  Authentication & Security

* Secure login system using **bcrypt password hashing**
* Session-based authentication
* Role-based access control (Admin, Healthcare Worker, Analyst)

###  Patient Management

* Add new patients
* View patient records
* Update patient status
* Delete patient records
* Disease validation using foreign keys

###  Outbreak Management

* Add outbreak details (location, dates, cases, fatality rate)
* Update outbreak data (end date, cases, fatality rate)
* Delete outbreak records
* Disease-linked outbreak tracking

### Resource Management

* Add medical resources
* Allocate resources to outbreaks
* Update quantity and allocation
* Prevent over-allocation using validation logic

###  Analysis Dashboard

* Patients vs Outbreak insights
* Resource allocation reports
* Outbreak severity summary using SQL joins
* Restricted access for Admin & Analyst roles

---

##  Tech Stack

### Frontend

* HTML5
* CSS3
* Bootstrap 
* Jinja2 Templates (Flask)

### Backend

* Python (Flask Framework)
* MySQL Database
* Flask-MySQL Integration

### Security

* bcrypt (Password Hashing)
* Flask Sessions

---

##  Project Structure

```
epidemic-management-system/
│
├── app.py                # Main Flask application
├── db_config.py          # MySQL database configuration
├── requirements.txt      # Python dependencies
├── LICENSE               # Project license (MIT recommended)
├── README.md             # Project documentation
│
├── templates/            # HTML Templates (Frontend)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── patients.html
│   ├── outbreaks.html
│   ├── resources.html
│   ├── analysis.html
│   └── ...
│
├── static/               # CSS, JS, Images (if available)
│
└── database/
    └── schema.sql        # (Optional) Database schema file
```

---

##  Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

###  Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

###  Install Dependencies

```bash
pip install -r requirements.txt
```

###  Configure MySQL Database

* Create a MySQL database
* Update your `db_config.py` with:

  * Host
  * Username
  * Password
  * Database Name

Example:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'epidemic_db'
```

###  Run the Application

```bash
python app.py
```

App will run on:

```
http://localhost:5000
```

---

##  Database Tables Used

* Users
* Patients
* Diseases
* Resources
* Outbreaks
* Resource_Allocation

The system uses:

* Primary Keys
* Foreign Keys
* SQL Joins
* Constraints for data integrity

---

##  Default Seeded Users (Auto Created)

| Role              | Username | Password   |
| ----------------- | -------- | ---------- |
| Admin             | admin    | admin123   |
| Healthcare Worker | worker   | worker123  |
| Analyst           | analyst  | analyst123 |

---

##  Screens Included

* Login Page
* Dashboard
* Patient Management
* Resource Allocation
* Analysis Dashboard

*(You can add screenshots later for better GitHub profile impact)*

---

##  Academic Relevance

This project was developed as a **DBMS + Full Stack Academic Project** demonstrating:

* Real-world database design
* Backend API logic
* Frontend template rendering
* Secure authentication system
* Analytical SQL queries

---

##  Future Improvements

* Deploy on cloud (Render / AWS / Heroku)
* Add REST API support
* Graphical data visualization (charts)
* Email alerts for outbreaks
* Role-based dashboard UI

---

##  License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this project with proper attribution.

---

##  Author

**Anmol**
B.Tech Student |
GitHub: https://github.com/your-username

---

##  If you like this project

Give it a star on GitHub to support the work!

from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import init_mysql
import bcrypt
import os

app = Flask(__name__)
# Use a secure random secret key
app.secret_key = os.urandom(24)  

# Initialize MySQL connection
mysql = init_mysql(app)

# Utility Function to Hash Password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Seed Users (Run Once)
def seed_users():
    """Seed sample user data into the database."""
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:  # Only seed if table is empty
        users = [
            ("admin", "admin@example.com", "Admin", hash_password("admin123").decode('utf-8')),
            ("worker", "worker@example.com", "Healthcare Worker", hash_password("worker123").decode('utf-8')),
            ("analyst", "analyst@example.com", "Analyst", hash_password("analyst123").decode('utf-8')),
        ]
        for user in users:
            cursor.execute("""
                INSERT INTO Users (Name, Email, Role, Password)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE Name=Name;
            """, user)
        conn.commit()
    cursor.close()

# Initialize Database (Call seed_users)
with app.app_context():
    seed_users()

# Routes
@app.route('/')
def index():
    """Home page with a welcome message."""
    # Temporarily bypass login for testing
    session['username'] = 'User'  # Simulate a logged-in user
    session['role'] = 'Admin'  # Simulate a role
    return render_template('index.html', username=session.get('username'), role=session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT Password, Role FROM Users WHERE Name = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
            session['username'] = username
            session['role'] = user[1]  # Store role in session
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials.", "danger")
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out and redirect to login."""
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    """Add a new patient."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Role-based access: Only Admins and Healthcare Workers can add patients
    if session.get('role') not in ['Admin', 'Healthcare Worker']:
        cursor.close()
        flash("Access denied. Only Admins and Healthcare Workers can add patients.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        disease_id = request.form['disease_id']
        status = request.form['status']

        try:
            # Validate Disease ID
            cursor.execute("SELECT 1 FROM Diseases WHERE Disease_ID = %s", (disease_id,))
            if not cursor.fetchone():
                flash("Invalid Disease ID. Please select a valid disease.", "danger")
                return redirect(url_for('add_patient'))

            # Insert the new patient
            cursor.execute("""
                INSERT INTO Patients (Name, Age, Gender, Address, Disease_ID, Status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, age, gender, address, disease_id, status))
            conn.commit()
            flash("Patient added successfully!", "success")
            return redirect(url_for('view_patients'))
        except Exception as e:
            conn.rollback()
            flash(f"Error adding patient: {e}", "danger")
            return redirect(url_for('add_patient'))
        finally:
            cursor.close()

    # Fetch diseases for the dropdown
    cursor = conn.cursor()
    cursor.execute("SELECT Disease_ID, Disease_Name FROM Diseases")
    diseases = cursor.fetchall()
    cursor.close()

    return render_template('add_patient.html', diseases=diseases)

@app.route('/view-patients', methods=['GET', 'POST'])
def view_patients():
    """View all patients with options to update status and delete."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Handle status update
    if request.method == 'POST' and 'update_status' in request.form:
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can update status.", "danger")
            return redirect(url_for('index'))
        patient_id = request.form['patient_id']
        new_status = request.form['status']
        try:
            cursor.execute("UPDATE Patients SET Status = %s WHERE Patient_ID = %s", (new_status, patient_id))
            conn.commit()
            flash("Patient status updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating status: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_patients'))

    # Handle patient deletion
    if request.method == 'POST' and 'delete_patient' in request.form:
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can delete patients.", "danger")
            return redirect(url_for('index'))
        patient_id = request.form['patient_id']
        try:
            cursor.execute("DELETE FROM Patients WHERE Patient_ID = %s", (patient_id,))
            conn.commit()
            flash("Patient deleted successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error deleting patient: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_patients'))

    # Fetch all patients for display
    cursor = conn.cursor()
    cursor.execute("""
            SELECT p.Patient_ID, p.Name, p.Age, p.Gender, p.Address, d.Disease_Name, p.Status
            FROM Patients p
            JOIN Diseases d ON p.Disease_ID = d.Disease_ID
        """)
    patients = cursor.fetchall()
    cursor.close()

    return render_template('view_patients.html', patients=patients)

@app.route('/patients')
def patients():
    """View all patients."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, d.Disease_Name
        FROM Patients p
        JOIN Diseases d ON p.Disease_ID = d.Disease_ID
    """)
    patients = cursor.fetchall()
    cursor.close()

    return render_template('patients.html', patients=patients)

@app.route('/add-resource', methods=['GET', 'POST'])
def add_resource():
    """Add a new resource."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Role-based access: Only Admins and Healthcare Workers can add resources
    if session.get('role') not in ['Admin', 'Healthcare Worker']:
        cursor.close()
        flash("Access denied. Only Admins and Healthcare Workers can add resources.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        type = request.form['type']
        quantity = request.form['quantity']
        allocated = request.form.get('allocated', 0)  # Default to 0 if not provided

        try:
            # Validate inputs
            quantity = int(quantity)
            allocated = int(allocated)
            if quantity < 1:
                flash("Quantity must be at least 1.", "danger")
                return redirect(url_for('add_resource'))
            if allocated < 0:
                flash("Allocated quantity cannot be negative.", "danger")
                return redirect(url_for('add_resource'))
            if allocated > quantity:
                flash("Allocated quantity cannot exceed total quantity.", "danger")
                return redirect(url_for('add_resource'))

            # Insert the new resource
            cursor.execute("""
                INSERT INTO Resources (Type, Quantity, Allocated)
                VALUES (%s, %s, %s)
            """, (type, quantity, allocated))
            conn.commit()
            flash("Resource added successfully!", "success")
            return redirect(url_for('view_resources'))
        except Exception as e:
            conn.rollback()
            flash(f"Error adding resource: {e}", "danger")
            return redirect(url_for('add_resource'))
        finally:
            cursor.close()

    return render_template('add_resource.html')

@app.route('/resources')
def resources():
    """View all resources."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Resources")
    resources = cursor.fetchall()
    cursor.close()

    return render_template('resources.html', resources=resources)

@app.route('/view-resources', methods=['GET', 'POST'])
def view_resources():
    """View all resources with options to update quantity/allocated and delete."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Handle quantity update
    if request.method == 'POST' and 'update_quantity' in request.form:
        resource_id = request.form['resource_id']
        new_quantity = request.form['quantity']
        try:
            new_quantity = int(new_quantity)
            if new_quantity < 1:
                flash("Quantity must be at least 1.", "danger")
                return redirect(url_for('view_resources'))

            # Check if new quantity is less than the current allocated amount
            cursor.execute("SELECT Allocated FROM Resources WHERE Resource_ID = %s", (resource_id,))
            current_allocated = cursor.fetchone()[0]
            if new_quantity < current_allocated:
                flash("New quantity cannot be less than the currently allocated amount.", "danger")
                return redirect(url_for('view_resources'))

            cursor.execute("UPDATE Resources SET Quantity = %s WHERE Resource_ID = %s", (new_quantity, resource_id))
            conn.commit()
            flash("Resource quantity updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating quantity: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_resources'))

    # Handle allocated update
    if request.method == 'POST' and 'update_allocated' in request.form:
        if session.get('role') != 'Admin':
            cursor.close()
            flash("Access denied. Only Admins  can allocate resources.", "danger")
            return redirect(url_for('index'))
        resource_id = request.form['resource_id']
        new_allocated = request.form['allocated']
        try:
            new_allocated = int(new_allocated)
            if new_allocated < 0:
                flash("Allocated quantity cannot be negative.", "danger")
                return redirect(url_for('view_resources'))

            # Check if new allocated amount exceeds the current quantity
            cursor.execute("SELECT Quantity FROM Resources WHERE Resource_ID = %s", (resource_id,))
            current_quantity = cursor.fetchone()[0]
            if new_allocated > current_quantity:
                flash("Allocated quantity cannot exceed the total quantity.", "danger")
                return redirect(url_for('view_resources'))

            cursor.execute("UPDATE Resources SET Allocated = %s WHERE Resource_ID = %s", (new_allocated, resource_id))
            conn.commit()
            flash("Resource allocated amount updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating allocated amount: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_resources'))

    # Handle resource deletion
    if request.method == 'POST' and 'delete_resource' in request.form:
         # Role-based access: Only Admins and Healthcare Workers can view or modify resources
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can delete resources.", "danger")
            return redirect(url_for('index'))
        resource_id = request.form['resource_id']
        try:
            cursor.execute("DELETE FROM Resource_Allocation WHERE Resource_ID = %s", (resource_id,))
            cursor.execute("DELETE FROM Resources WHERE Resource_ID = %s", (resource_id,))
            conn.commit()
            flash("Resource deleted successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error deleting resource: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_resources'))

    # Fetch all resources for display
    cursor = conn.cursor()
    cursor.execute("SELECT Resource_ID, Type, Quantity, Allocated FROM Resources")
    resources = cursor.fetchall()
    cursor.close()

    return render_template('view_resources.html', resources=resources)

@app.route('/add-outbreak', methods=['GET', 'POST'])
def add_outbreak():
    """Add a new outbreak."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Role-based access: Only Admins and Healthcare Workers can add outbreaks
    if session.get('role') not in ['Admin', 'Healthcare Worker']:
        cursor.close()
        flash("Access denied. Only Admins and Healthcare Workers can add outbreaks.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        disease_id = request.form['disease_id']
        location = request.form['location']
        start_date = request.form['start_date']
        end_date = request.form.get('end_date') or None  # Use None if end_date is not provided
        number_of_cases = request.form.get('number_of_cases', 0)  # Default to 0 if not provided
        fatality_rate = request.form.get('fatality_rate', 0.00)  # Default to 0.00 if not provided

        try:
            # Validate Disease ID
            cursor.execute("SELECT 1 FROM Diseases WHERE Disease_ID = %s", (disease_id,))
            if not cursor.fetchone():
                flash("Invalid Disease ID. Please select a valid disease.", "danger")
                return redirect(url_for('add_outbreak'))

            # Validate dates
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                if end_date_obj < start_date_obj:
                    flash("End date cannot be earlier than start date.", "danger")
                    return redirect(url_for('add_outbreak'))

            # Validate number of cases and fatality rate
            number_of_cases = int(number_of_cases)
            fatality_rate = float(fatality_rate)
            if number_of_cases < 0:
                flash("Number of cases cannot be negative.", "danger")
                return redirect(url_for('add_outbreak'))
            if fatality_rate < 0 or fatality_rate > 100:
                flash("Fatality rate must be between 0 and 100.", "danger")
                return redirect(url_for('add_outbreak'))

            # Insert the new outbreak
            cursor.execute("""
                INSERT INTO Outbreaks (Disease_ID, Location, Start_Date, End_Date, Number_of_Cases, Fatality_Rate)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (disease_id, location, start_date, end_date, number_of_cases, fatality_rate))
            conn.commit()
            flash("Outbreak added successfully!", "success")
            return redirect(url_for('view_outbreaks'))
        except Exception as e:
            conn.rollback()
            flash(f"Error adding outbreak: {e}", "danger")
            return redirect(url_for('add_outbreak'))
        finally:
            cursor.close()

    # Fetch diseases for the dropdown
    cursor = conn.cursor()
    cursor.execute("SELECT Disease_ID, Disease_Name FROM Diseases")
    diseases = cursor.fetchall()
    cursor.close()

    return render_template('add_outbreak.html', diseases=diseases)

@app.route('/outbreaks')
def outbreaks():
    """View all outbreaks."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, d.Disease_Name
        FROM Outbreaks o
        JOIN Diseases d ON o.Disease_ID = d.Disease_ID
    """)
    outbreaks = cursor.fetchall()
    cursor.close()

    return render_template('outbreaks.html', outbreaks=outbreaks)

@app.route('/view-outbreaks', methods=['GET', 'POST'])
def view_outbreaks():
    """View all outbreaks with options to update end date, number of cases, and fatality rate."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()


    # Handle end date update
    if request.method == 'POST' and 'update_end_date' in request.form:
        # Role-based access: Only Admins and Healthcare Workers can view or modify outbreaks
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can  modify outbreaks.", "danger")
            return redirect(url_for('index'))
        outbreak_id = request.form['outbreak_id']
        new_end_date = request.form['end_date'] or None  # Use None if end_date is empty
        try:
            # Validate end date against start date
            if new_end_date:
                cursor.execute("SELECT Start_Date FROM Outbreaks WHERE Outbreak_ID = %s", (outbreak_id,))
                start_date = cursor.fetchone()[0]
                from datetime import datetime
                start_date_obj = datetime.strptime(str(start_date), '%Y-%m-%d')
                end_date_obj = datetime.strptime(new_end_date, '%Y-%m-%d')
                if end_date_obj < start_date_obj:
                    flash("End date cannot be earlier than start date.", "danger")
                    return redirect(url_for('view_outbreaks'))

            cursor.execute("UPDATE Outbreaks SET End_Date = %s WHERE Outbreak_ID = %s", (new_end_date, outbreak_id))
            conn.commit()
            flash("Outbreak end date updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating end date: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_outbreaks'))

    # Handle number of cases update
    if request.method == 'POST' and 'update_number_of_cases' in request.form:
        # Role-based access: Only Admins and Healthcare Workers can view or modify outbreaks
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can update the number of cases.", "danger")
            return redirect(url_for('index'))
        outbreak_id = request.form['outbreak_id']
        new_number_of_cases = request.form['number_of_cases']
        try:
            new_number_of_cases = int(new_number_of_cases)
            if new_number_of_cases < 0:
                flash("Number of cases cannot be negative.", "danger")
                return redirect(url_for('view_outbreaks'))

            cursor.execute("UPDATE Outbreaks SET Number_of_Cases = %s WHERE Outbreak_ID = %s", (new_number_of_cases, outbreak_id))
            conn.commit()
            flash("Number of cases updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating number of cases: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_outbreaks'))

    # Handle fatality rate update
    if request.method == 'POST' and 'update_fatality_rate' in request.form:
        # Role-based access: Only Admins and Healthcare Workers can view or modify outbreaks
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can update FR.", "danger")
            return redirect(url_for('index'))
        outbreak_id = request.form['outbreak_id']
        new_fatality_rate = request.form['fatality_rate']
        try:
            new_fatality_rate = float(new_fatality_rate)
            if new_fatality_rate < 0 or new_fatality_rate > 100:
                flash("Fatality rate must be between 0 and 100.", "danger")
                return redirect(url_for('view_outbreaks'))

            cursor.execute("UPDATE Outbreaks SET Fatality_Rate = %s WHERE Outbreak_ID = %s", (new_fatality_rate, outbreak_id))
            conn.commit()
            flash("Fatality rate updated successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating fatality rate: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_outbreaks'))

    # Handle outbreak deletion
    if request.method == 'POST' and 'delete_outbreak' in request.form:
        # Role-based access: Only Admins and Healthcare Workers can view or modify outbreaks
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can delete outbreaks.", "danger")
            return redirect(url_for('index'))
        outbreak_id = request.form['outbreak_id']
        try:
            cursor.execute("DELETE FROM Resource_Allocation WHERE Outbreak_ID = %s", (outbreak_id,))
            cursor.execute("DELETE FROM Outbreaks WHERE Outbreak_ID = %s", (outbreak_id,))
            conn.commit()
            flash("Outbreak deleted successfully!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error deleting outbreak: {e}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('view_outbreaks'))

    # Fetch all outbreaks for display
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.Outbreak_ID, o.Disease_ID, o.Location, o.Start_Date, o.End_Date, o.Number_of_Cases, o.Fatality_Rate, d.Disease_Name
        FROM Outbreaks o
        JOIN Diseases d ON o.Disease_ID = d.Disease_ID
    """)
    outbreaks = cursor.fetchall()
    cursor.close()

    return render_template('view_outbreaks.html', outbreaks=outbreaks)

@app.route('/resource_allocation', methods=['GET', 'POST'])
def resource_allocation():
    """Allocate resources to outbreaks."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    if request.method == 'POST':
        if session.get('role') not in ['Admin', 'Healthcare Worker']:
            cursor.close()
            flash("Access denied. Only Admins and Healthcare Workers can allocate resources.", "danger")
            return redirect(url_for('index'))
        resource_id = request.form['resource_id']
        outbreak_id = request.form['outbreak_id']
        quantity_allocated = request.form['quantity_allocated']

        try:
            cursor.execute("SELECT Quantity, Allocated FROM Resources WHERE Resource_ID = %s", (resource_id,))
            resource = cursor.fetchone()
            if not resource:
                flash("Invalid resource ID.", "danger")
                return redirect(url_for('resource_allocation'))

            cursor.execute("SELECT 1 FROM Outbreaks WHERE Outbreak_ID = %s", (outbreak_id,))
            if not cursor.fetchone():
                flash("Invalid outbreak ID.", "danger")
                return redirect(url_for('resource_allocation'))

            available = resource[0] - resource[1]
            if int(quantity_allocated) > available:
                flash("Not enough resources available.", "danger")
                return redirect(url_for('resource_allocation'))

            cursor.execute("""
                INSERT INTO Resource_Allocation (Resource_ID, Outbreak_ID, Quantity_Allocated)
                VALUES (%s, %s, %s)
            """, (resource_id, outbreak_id, quantity_allocated))

            cursor.execute("""
                UPDATE Resources
                SET Allocated = Allocated + %s
                WHERE Resource_ID = %s
            """, (quantity_allocated, resource_id))

            cursor.execute("""
                UPDATE Resources
                SET Quantity = Quantity - %s
                WHERE Resource_ID = %s
            """, (quantity_allocated, resource_id))

            conn.commit()
            flash("Resource allocated successfully!", "success")
            return redirect(url_for('resource_allocation'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}", "danger")
            return redirect(url_for('resource_allocation'))
        finally:
            cursor.close()

    # Fetch resources and outbreaks for the form
    cursor = conn.cursor()
    cursor.execute("SELECT Resource_ID, Type FROM Resources")
    resources = cursor.fetchall()
    cursor.execute("SELECT Outbreak_ID, Location FROM Outbreaks")
    outbreaks = cursor.fetchall()

    # Fetch existing allocations for the table
    cursor.execute("""
        SELECT ra.Resource_ID, r.Type AS Resource_Type, ra.Outbreak_ID, o.Location AS Outbreak_Location, ra.Quantity_Allocated
        FROM Resource_Allocation ra
        JOIN Resources r ON ra.Resource_ID = r.Resource_ID
        JOIN Outbreaks o ON ra.Outbreak_ID = o.Outbreak_ID
    """)
    allocations = []
    for row in cursor.fetchall():
        allocations.append({
            'resource_id': row[0],
            'resource_type': row[1],
            'outbreak_id': row[2],
            'outbreak_location': row[3],
            'quantity_allocated': row[4]
        })
    cursor.close()

    return render_template('resource_allocation.html', resources=resources, outbreaks=outbreaks, allocations=allocations)

@app.route('/report-disease', methods=['GET', 'POST'])
def report_disease():
    """Report a new disease."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()


    if request.method == 'POST':
        disease_name = request.form['disease_name']
        symptoms = request.form['symptoms']
        mortality_rate = request.form['mortality_rate']

        try:
            # Validate mortality rate
            mortality_rate = float(mortality_rate)
            if mortality_rate < 0 or mortality_rate > 100:
                flash("Mortality rate must be between 0 and 100.", "danger")
                return redirect(url_for('report_disease'))

            # Insert the new disease
            cursor.execute("""
                INSERT INTO Diseases (Disease_Name, Symptoms, Mortality_Rate)
                VALUES (%s, %s, %s)
            """, (disease_name, symptoms, mortality_rate))
            conn.commit()
            flash("Disease reported successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            flash(f"Error reporting disease: {e}", "danger")
            return redirect(url_for('report_disease'))
        finally:
            cursor.close()

    return render_template('report_disease.html')

@app.route('/analysis')
def analysis():
    """Display analysis of patients, outbreaks, and resource allocations."""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connection
    cursor = conn.cursor()

    # Role-based access: Only Admins and Analysts can access the analysis page
    if session.get('role') not in ['Admin', 'Analyst']:
        cursor.close()
        flash("Access denied. Only Admins and Analysts can access the analysis page.", "danger")
        return redirect(url_for('index'))

    try:
        # 1. Patients and Outbreaks: Join Patients, Outbreaks, and Diseases
        cursor.execute("""
            SELECT p.Name, d.Disease_Name, o.Location, o.Start_Date
            FROM Patients p
            JOIN Diseases d ON p.Disease_ID = d.Disease_ID
            JOIN Outbreaks o ON o.Disease_ID = d.Disease_ID
            ORDER BY o.Start_Date DESC
        """)
        patients_outbreaks = cursor.fetchall()

        # 2. Resources Allocated to Outbreaks: Join Resource_Allocation, Resources, and Outbreaks
        cursor.execute("""
            SELECT r.Type, o.Location, ra.Quantity_Allocated
            FROM Resource_Allocation ra
            JOIN Resources r ON ra.Resource_ID = r.Resource_ID
            JOIN Outbreaks o ON ra.Outbreak_ID = o.Outbreak_ID
            ORDER BY o.Location
        """)
        resources_allocations = cursor.fetchall()

        # 3. Outbreak Severity Summary: Summarize Outbreaks data
        cursor.execute("""
            SELECT o.Location, d.Disease_Name, o.Number_of_Cases, o.Fatality_Rate
            FROM Outbreaks o
            JOIN Diseases d ON o.Disease_ID = d.Disease_ID
            ORDER BY o.Number_of_Cases DESC
        """)
        outbreak_summary = cursor.fetchall()

    except Exception as e:
        flash(f"Error fetching analysis data: {e}", "danger")
        patients_outbreaks = []
        resources_allocations = []
        outbreak_summary = []
    finally:
        cursor.close()

    return render_template('analysis.html', 
                          patients_outbreaks=patients_outbreaks,
                          resources_allocations=resources_allocations,
                          outbreak_summary=outbreak_summary)

# Main Driver
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
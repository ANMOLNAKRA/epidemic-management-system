def get_all_patients(mysql):
    """Fetch all patients from the database."""
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT * FROM Patients"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def add_patient(mysql, name, age, disease):
    """Add a new patient to the database."""
    conn = mysql.connection
    cursor = conn.cursor()
    query = "INSERT INTO Patients (Name, Age, Disease_ID) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, age, disease))
    conn.commit()
    cursor.close()

import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime

# Function to create a MySQL connection
def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database="VaccinationRecord"
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

# Function to execute a single query
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# Function to convert date format from MM/DD/YYYY to YYYY-MM-DD
def convert_date(date_str):
    return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')

# Function to insert data from CSV file into a table with date conversion
def insert_data_from_csv(connection, table_name, csv_file, columns, date_columns=[]):
    cursor = connection.cursor()
    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                for col in date_columns:
                    row[col] = convert_date(row[col])
                placeholders = ', '.join(['%s'] * len(row))
                sql = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(sql, row)
        connection.commit()
        print(f"Data inserted successfully into {table_name}")
    except Error as e:
        print(f"The error '{e}' occurred")

# Database connection details
host_name = "localhost"
user_name = "root"
# enter password for MySQLWorkbench
user_password = ""

# Connect to MySQL server
connection = create_connection(host_name, user_name, user_password)

# Create database if it doesn't exist
# execute_query(connection, "DROP database IF EXISTS VaccinationRecord;")
# execute_query(connection, "CREATE DATABASE IF NOT EXISTS VaccinationRecord;")
# execute_query(connection, "USE VaccinationRecord;")

# Create tables
patients_table = """
CREATE TABLE IF NOT EXISTS Patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    street_address VARCHAR(255),
    address2 VARCHAR(255),
    date_of_birth DATE
);
"""
execute_query(connection, patients_table)

companies_table = """
CREATE TABLE IF NOT EXISTS Companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    headquarters_location VARCHAR(255),
    contact_info VARCHAR(255)
);
"""
execute_query(connection, companies_table)

pharmacies_table = """
CREATE TABLE IF NOT EXISTS Pharmacies (
    pharmacy_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    street_address VARCHAR(255),
    address2 VARCHAR(255)
);
"""
execute_query(connection, pharmacies_table)


caregivers_table = """
CREATE TABLE IF NOT EXISTS Caregivers (
    caregiver_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    street_address VARCHAR(255),
    address2 VARCHAR(255),
    available_time_slot VARCHAR(255),
    pharmacy_id INT,
    FOREIGN KEY (pharmacy_id) REFERENCES Pharmacies(pharmacy_id)
);
"""
execute_query(connection, caregivers_table)

vaccinations_table = """
CREATE TABLE IF NOT EXISTS Vaccinations (
    vaccine_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    company_id INT,
    type VARCHAR(255),
    doses_required INT,
    storage_requirements VARCHAR(255),
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)
);
"""
execute_query(connection, vaccinations_table)

# Test
execute_query(connection, "DROP TABLE IF EXISTS Inventory;")
inventory_table = """
CREATE TABLE IF NOT EXISTS Inventory (
    pharmacy_id INT,
    company_id INT,
    vaccine_id INT,
    quantity_available INT,
    quantity_administered INT,
    PRIMARY KEY (pharmacy_id, company_id, vaccine_id),
    FOREIGN KEY (pharmacy_id) REFERENCES Pharmacies(pharmacy_id),
    FOREIGN KEY (company_id) REFERENCES Companies(company_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccinations(vaccine_id)
);
"""
execute_query(connection, inventory_table)

vaccination_records_table = """
CREATE TABLE IF NOT EXISTS VaccinationRecords (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    vaccine_id INT,
    caregiver_id INT,
    pharmacy_id INT,
    administration_date DATE,
    dose_number INT,
    lot_number VARCHAR(255),
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccinations(vaccine_id),
    FOREIGN KEY (caregiver_id) REFERENCES Caregivers(caregiver_id),
    FOREIGN KEY (pharmacy_id) REFERENCES Pharmacies(pharmacy_id)
);
"""
execute_query(connection, vaccination_records_table)

vaccination_appointments_table = """
CREATE TABLE IF NOT EXISTS VaccinationAppointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    caregiver_id INT,
    vaccine_id INT,
    appointment_date DATE,
    status VARCHAR(255),
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (caregiver_id) REFERENCES Caregivers(caregiver_id),
    FOREIGN KEY (vaccine_id) REFERENCES Vaccinations(vaccine_id)
);
"""
execute_query(connection, vaccination_appointments_table)

# Insert data into tables from CSV files with date conversion
insert_data_from_csv(connection, 'Patients', './data/Patient.csv',
                     ['patient_id', 'first_name', 'last_name', 'email', 'phone', 'street_address', 'address2', 'date_of_birth'],
                     date_columns=[7])

insert_data_from_csv(connection, 'Companies', './data/company.csv',
                     ['company_id', 'name', 'headquarters_location', 'contact_info'])

insert_data_from_csv(connection, 'Pharmacies', './data/pharmacy.csv',
                     ['pharmacy_id', 'name', 'email', 'phone', 'street_address', 'address2'])

insert_data_from_csv(connection, 'Caregivers', './data/caregiver.csv',
                     ['caregiver_id', 'first_name', 'last_name', 'email', 'phone', 'street_address', 'address2', 'available_time_slot', 'pharmacy_id'])

insert_data_from_csv(connection, 'Vaccinations', './data/vaccination.csv',
                     ['vaccine_id', 'name', 'company_id', 'type', 'doses_required', 'storage_requirements'])

insert_data_from_csv(connection, 'Inventory', './data/inventory.csv',
                     ['pharmacy_id', 'company_id', 'vaccine_id', 'quantity_available', 'quantity_administered'])

insert_data_from_csv(connection, 'VaccinationRecords', './data/VaccinationRecord.csv',
                     ['record_id', 'patient_id', 'vaccine_id', 'caregiver_id', 'pharmacy_id', 'administration_date', 'dose_number', 'lot_number'],
                     date_columns=[5])

insert_data_from_csv(connection, 'VaccinationAppointments', './data/appointment.csv',
                     ['appointment_id', 'patient_id', 'caregiver_id', 'vaccine_id', 'appointment_date', 'status'],
                     date_columns=[4])

# Close the connection
connection.close()

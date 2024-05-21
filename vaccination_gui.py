import mysql.connector
import PySimpleGUI as sg


# Database connection details
host_name = "localhost"
user_name = "root"
user_password = "7543XDBxcy" # enter password for MySQLWorkbench
# Create a MySQL connection
connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database="VaccinationRecord"
        )
# create cursor object
cursorObject = connection.cursor()

# # ----- Full layout -----
layout = [
    [sg.Text("Vaccination System", size=(30, 1), font=("Helvetica", 25), justification='center', pad=(0,20))],
    [sg.Text("Welcome to the Vaccination System Database. This application allows you to query vaccination data.", pad=(0,20))],
    [
        sg.Column([
            [sg.Text("Available Queries:")],
            [sg.Radio("Find all patients who have received <vaccine name>", "QUERY", key="Q1", enable_events=True)],
            [sg.Radio("Retrieve vaccination history for <patient name>", "QUERY", key="Q2", enable_events=True)],
            [sg.Radio("Find patients due for their 2nd dose or booster shot of a vaccine", "QUERY", key="Q3", enable_events=True)],
            #[sg.Radio("List all vaccines that require ultra-cold storage", "QUERY", key="Q5", enable_events=True)],
            [sg.Radio("Determine the quantity of vaccines needed to reorder for each pharmacy", "QUERY", key="Q6", enable_events=True)],
            [sg.Radio("Show upcoming vaccination appointments by date", "QUERY", key="Q7", enable_events=True)],
            [sg.Radio("Find the total number of vaccines administered by each Vaccination Caregiver", "QUERY", key="Q8", enable_events=True)],
            [sg.Radio("Find the total number of different types of vaccines administered by each Vaccination Caregiver", "QUERY", key="Q9", enable_events=True)],
            [sg.Radio("Find all vaccines from a <company name> that are out of stock at pharmacies", "QUERY", key="Q10", enable_events=True)],
            [sg.Radio("Find upcoming vaccination appointments that have is scheduled by the <patient name>", "QUERY", key="Q11", enable_events=True)],
            [sg.Radio("Find the dose amount of each vaccination has been used by all patients", "QUERY", key="Q12", enable_events=True)],
            [sg.Text("Enter additional input if required in `<...>`:")],
            [sg.InputText(key="INPUT", size=(30, 1))],
            [sg.Button("Run Query"), sg.Button("Exit")]
        ]),
        sg.VSeperator(),
        sg.Column([
            [sg.Text("Results:")],
            [sg.Multiline(size=(80, 20), key="RESULT")]
        ])
    ]
]

# Create the window
window = sg.Window("Vaccination System", layout)

# Function to simulate query execution
def execute_query(query, intro_line):
    res_content = intro_line
    cursorObject.execute(query)
    result = cursorObject.fetchall()
    for res in result:
        delimiter = ' ' if len(res) == 1 else ', '
        for col in res:
            res_content = res_content + str(col) + delimiter
        res_content = res_content + '\n'
    return res_content
    


# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "Run Query":
        intro_line = ""
        selected_query = ""
        input_value = values["INPUT"]
        if values["Q1"]: # e.g., COVID-19 Vaccine D
            intro_line = f"Patients who received {input_value} vaccine: \n"
            selected_query = " SELECT DISTINCT CONCAT(p.first_name, ' ', p.last_name) AS FullName"\
                " FROM Patients p "\
                " JOIN VaccinationRecords vr ON p.patient_id = vr.patient_id "\
                " JOIN Vaccinations v ON vr.vaccine_id = v.vaccine_id "\
                f" WHERE v.name = '{input_value}';"
        elif values["Q2"]: # e.g., Jojo Heazel
            first_name = input_value.split(' ')[0]
            last_name = input_value.split(' ')[1]
            intro_line = f"Vaccination history for patient {input_value}: \n[record_id, vaccine, caregiver, pharmacy, administration_date, dose_number, lot_number]\n"
            selected_query = " SELECT vr.record_id, v.name AS VaccineName, CONCAT(c.first_name, ' ', c.last_name) AS CaregiverName, pm.name AS PharmacyName, vr.administration_date, vr.dose_number, vr.lot_number" \
                " FROM Patients p " \
                " JOIN VaccinationRecords vr ON p.patient_id = vr.patient_id " \
                " JOIN Vaccinations v ON vr.vaccine_id = v.vaccine_id " \
                " JOIN Caregivers c ON vr.caregiver_id = c.caregiver_id " \
                " JOIN Pharmacies pm ON VR.pharmacy_id = pm.pharmacy_id " \
                f" WHERE p.first_name = '{first_name}' AND p.last_name = '{last_name}' " \
                " ORDER BY vr.administration_date;"
        elif values["Q3"]: 
            intro_line = "Find patients due for their 2nd dose or booster shot of a vaccine: \n [name, phone, email, vaccine, LastDoseDate]\n"
            selected_query = " SELECT CONCAT(p.first_name, ' ', p.last_name) AS FullName, p.phone, p.email, v.name, MAX(vr.administration_date) AS LastDoseDate" \
                " FROM Patients p " \
                " JOIN VaccinationRecords vr ON p.patient_id = vr.patient_id " \
                " JOIN Vaccinations v ON vr.vaccine_id = v.vaccine_id " \
                " GROUP BY p.patient_id, vr.vaccine_id, v.doses_required " \
                " HAVING COUNT(vr.record_id) < v.doses_required;"
        
        # elif values["Q5"]:
        #     intro_line = "List of vaccines that require ultra-cold storage: \n"
        #     selected_query = "SELECT name FROM Vaccinations WHERE storage_requirements = 'Ultra-cold';"

        elif values["Q6"]:
            intro_line = "Quantity of vaccines needed to reorder for each pharmacy: \n [Pharmacy, Vaccine, QuantityAvailable, QuantityAdministered]\n"
            selected_query = "SELECT pm.name AS PharmacyName, v.name AS VaccineName, im.quantity_available, im.quantity_administered " \
                             "FROM Inventory im " \
                             "JOIN Pharmacies pm ON im.pharmacy_id = pm.pharmacy_id " \
                             "JOIN Vaccinations v ON im.vaccine_id = v.vaccine_id " \
                             "WHERE im.quantity_available < im.quantity_administered;"

        elif values["Q7"]:
            intro_line = "Upcoming vaccination appointments by date: \n [AppointmentDate, Patient, Vaccine]\n"
            selected_query = "SELECT va.appointment_date, CONCAT(p.first_name, ' ', p.last_name) AS PatientName, v.name AS VaccineName " \
                             "FROM VaccinationAppointments va " \
                             "JOIN Patients p ON va.patient_id = p.patient_id " \
                             "JOIN Vaccinations v ON va.vaccine_id = v.vaccine_id " \
                             "WHERE va.status = 1 " \
                             "ORDER BY va.appointment_date;"


        elif values["Q8"]:
            intro_line = "Total number of vaccines administered by each Vaccination Caregiver: \n [Caregiver, TotalVaccinesAdministered]\n"
            selected_query = "SELECT CONCAT(c.first_name, ' ', c.last_name) AS CaregiverName, COUNT(vr.record_id) AS TotalVaccinesAdministered " \
                             "FROM Caregivers c " \
                             "JOIN VaccinationRecords vr ON c.caregiver_id = vr.caregiver_id " \
                             "GROUP BY c.caregiver_id;"

        elif values["Q9"]:
            intro_line = "Total number of different types of vaccines administered by each Vaccination Caregiver: \n [Caregiver, TotalTypesOfVaccines]\n"
            selected_query = "SELECT CONCAT(c.first_name, ' ', c.last_name) AS CaregiverName, COUNT(DISTINCT vr.vaccine_id) AS TotalTypesOfVaccines " \
                             "FROM Caregivers c " \
                             "JOIN VaccinationRecords vr ON c.caregiver_id = vr.caregiver_id " \
                             "GROUP BY c.caregiver_id;"
                             
        elif values["Q10"]:
            company_name = input_value
            intro_line = "Retrieve a list of all vaccines manufactured by a company that are currently out of stock at pharmacies: \n [VaccineName, PharmacyName]\n"
            selected_query = f"""
                            SELECT v.name AS VaccineName, p.name AS PharmacyName
                            FROM Vaccinations v
                            JOIN Inventory i ON v.vaccine_id = i.vaccine_id
                            JOIN Companies c ON i.company_id = c.company_id
                            JOIN Pharmacies p ON i.pharmacy_id = p.pharmacy_id
                            WHERE
                                i.quantity_available < i.quantity_administered
                                AND c.name = '{company_name}';
                            """
        elif values["Q11"]:
            first_name = input_value.split(' ')[0]
            last_name = input_value.split(' ')[1]
            intro_line = f"Scheduled appointment for patient {input_value}: \n[vaccine, appointment_date, pharmacy_name]\n"
            selected_query =f"""
                            SELECT v.name AS VaccineName, a.appointment_date AS AppointmentDate, ph.name AS PharmacyName
                            FROM VaccinationAppointments a
                            JOIN Vaccinations v ON a.vaccine_id = v.vaccine_id
                            JOIN Caregivers c ON a.caregiver_id = c.caregiver_id
                            JOIN Pharmacies ph ON c.pharmacy_id = ph.pharmacy_id
                            JOIN Patients p ON a.patient_id = p.patient_id
                            WHERE 
                                a.status = 1
                                AND p.first_name = '{first_name}'
                                AND p.last_name = '{last_name}';
                            """
        elif values["Q12"]:
            intro_line = f"The amount of each vaccination has been used: \n[vaccine, appointment_date, pharmacy_name]\n"
            selected_query =f"""
                            SELECT v.name AS VaccineName, SUM(vr.dose_number) AS TotalDosesAdministered
                            FROM VaccinationRecords vr
                            JOIN Vaccinations v ON vr.vaccine_id = v.vaccine_id
                            GROUP BY v.name;
                            """
        result = execute_query(selected_query, intro_line)
        window["RESULT"].update(result)

    # Show or hide input field based on selected query
    if values["Q1"] or values["Q2"] or values["Q10"] or values["Q11"]:
        window["INPUT"].update(visible=True)
        window["INPUT"].update(value="")
    elif values["Q3"] or values["Q6"] or values["Q7"] or values["Q8"] or values["Q9"] or values["Q12"]:
        window["INPUT"].update(visible=False)
        window["INPUT"].update(value="")

window.close()

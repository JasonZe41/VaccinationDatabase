import mysql.connector
import PySimpleGUI as sg


# Database connection details
host_name = "localhost"
user_name = "root"
user_password = "" # enter password for MySQLWorkbench
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

        result = execute_query(selected_query, intro_line)
        window["RESULT"].update(result)

    # Show or hide input field based on selected query
    if values["Q1"] or values["Q2"]:
        window["INPUT"].update(visible=True)
        window["INPUT"].update(value="")
    elif values["Q3"]:
        window["INPUT"].update(visible=False)
        window["INPUT"].update(value="")

window.close()

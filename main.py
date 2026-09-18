from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/")
def home():
    return {"message":"Welcome to my app"}

@app.get("/appointment/{appointment_id}")
def get_appointment(appointment_id):
    connection = sqlite3.Connection("appointments.db")
    cursor = connection.cursor()
    data = cursor.execute("""
                      select * from appointments where id=?
                      """,("APT001",))
    details = data.fetchall()
    apponitment_details = details[0]
    return {"Patient Name":apponitment_details[1], "Doctor Name":apponitment_details[4], "Appointment Time":apponitment_details[5]}
    
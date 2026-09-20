from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from fastapi.responses import JSONResponse
import random
import string
import os
import psycopg2

@app.get("/test-db")
def test_db():
    connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    connection.close()
    return {"message": "PostgreSQL connected successfully"}

def generate_appointment_code():
    return f"APT-{random.randint(1000, 9999)}"

def connectdb():
    connection = sqlite3.Connection("appointments.db")
    cursor = connection.cursor()
    return [cursor, connection]

class DocSlot(BaseModel):
    doc_id: Annotated[str, Field(description="Provide the doctor's Id")]
    date: Annotated[str,Field(description="Provide date of booking in format YYYY-MM-DD example 2026-09-25")]
    slot: Annotated[str,Field(description="Provide the slot that user selected example 9AM-9:20AM etc")]

    
app = FastAPI()

@app.get("/")
def home():
    return {"message":"Welcome to my app"}

@app.get("/appointment/{appointment_id}")
def get_appointment(appointment_id: str):
    appointment_id = appointment_id.replace("-", "")
    data = cursor.execute("""
                      select * from appointments where id=?
                      """,(appointment_id,))
    details = data.fetchall()
    apponitment_details = details[0]
    return {"Patient Name":apponitment_details[1], "Doctor Name":apponitment_details[4], "Appointment Time":apponitment_details[5]}

@app.get("/all_doctor")
def get_docs():
    cursor = connectdb()
    cursor = cursor[0]
    data = cursor.execute("""
                   select * from DocDetails
                   """)
    doc_data = data.fetchall()
    return doc_data

@app.post("/book_appointment")
def book_appointment(request: DocSlot):
    request_data = request.model_dump()
    req_doc_id = request_data["doc_id"]
    req_date = request_data["date"]
    req_slot = request_data["slot"]
    appointment_id = generate_appointment_code()
    # response = {"doc_id":doc_id,"date": date,"slot": slot}
    # return response
    connection = sqlite3.Connection("appointments.db")
    cursor = connection.cursor()
    cursor.execute(f"""
                   update DocSlots set "{req_slot}" = ? where date = ? and doc_id = ?
                   """,(appointment_id,req_date,req_doc_id))
    connection.commit()
    connection.close()
    print("DB location:", os.path.abspath("appointments.db"))
    return JSONResponse(status_code=200, content=f"Appointment booked successfully with appointment ID as {appointment_id}")
    
    
    
    


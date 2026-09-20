from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from fastapi.responses import JSONResponse
import random
import string
import os
import psycopg2
from datetime import date

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/dbconnection_check")
def dbcheck():
    connection = psycopg2.connect(DATABASE_URL)
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
    req_date: Annotated[date,Field(description="Provide date of booking in format YYYY-MM-DD example 2026-09-25")]
    slot: Annotated[str,Field(description="Provide the slot that user selected example 9AM-9:20AM etc")]

    


@app.get("/")
def home():
    return {"message":"Welcome to my app"}

@app.get("/appointment/{appointment_id}")
def get_appointment(appointment_id: str):
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    appointment_id = appointment_id.replace("-", "")
    cursor.execute("""
               select * from appointments where id = %s
               """,("APT-1001",))
    details = cursor.fetchall()
    apponitment_details = details[0]
    cursor.close()
    return {"Patient Name":apponitment_details[1], "Doctor Name":apponitment_details[4], "Appointment Time":apponitment_details[5]}

@app.get("/all_doctor")
def get_docs():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("""
                   select * from "DocDetails"
                   """)
    doc_data = cursor.fetchall()
    cursor.close()
    return doc_data

@app.post("/book_appointment")
def book_appointment(request: DocSlot):
    request_data = request.model_dump()
    req_doc_id = request_data["doc_id"]
    req_date = request_data["req_date"]
    req_slot = request_data["slot"]
    appointment_id = generate_appointment_code()
    # response = {"doc_id":doc_id,"date": date,"slot": slot}
    # return response
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute(f"""
                   update "DocSlots" set "{req_slot}" = %s where date = %s and doc_id = %s
                   """,(appointment_id,req_date,req_doc_id))
    connection.commit()
    print("Rows updated:", cursor.rowcount)
    print("doc_id:", req_doc_id)
    print("req_date:", req_date, type(req_date))
    connection.close()
    # print("DB location:", os.path.abspath("appointments.db"))
    return JSONResponse(status_code=200, content=f"Appointment booked successfully with appointment ID as {appointment_id}")
    
    
    
    


import os
import uuid
from datetime import datetime

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DB_CONNECTION_STRING = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

engine = create_engine(
    DB_CONNECTION_STRING,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem",
        }
    },
)


def __init__(self, user_id):
    USER_ID = user_id


def get_results(sqlQuery):
    with engine.connect() as conn:
        results = conn.execute(text(sqlQuery)).mappings()
        rows = []
        for row in results.all():
            rows.append(row)

    return rows


def get_user(user_id):
    return get_results(f"select * from users where users.id = '{user_id}' ")


def get_user_by_username(username):
    return get_results(f"select * from users where users.username = '{username}' ")


def update_user_password(user_id, password_hash):
    with engine.connect() as conn:
        query = text(
            f"""UPDATE users
                SET userPassword = :userPassword
                WHERE id = :userID
            """
        )

        query_params = {
            "userPassword": password_hash,
            "userID": user_id,
        }

        conn.execute(
            statement=query,
            parameters=query_params,
        )


def add_new_user(data, password_hash):
    with engine.connect() as conn:
        query = text(
            """INSERT INTO users (id, username, userPassword, firstName, lastName, email)
                VALUES (:userID, :username, :userPassword, :firstName, :lastName, :email)"""
        )

        query_params = {
            "userID": str(uuid.uuid4()),
            "username": data["username"],
            "userPassword": password_hash,
            "firstName": data["first_name"],
            "lastName": data["last_name"],
            "email": data["email"],
        }

        conn.execute(
            statement=query,
            parameters=query_params,
        )


def get_timesheets(user_id):
    return get_results(
        f"""select *  
            from timesheets
            inner join (select hospitalName, hospitals.hospitalID  from hospitals) hospitals
            on timesheets.hospitalID = hospitals.hospitalID
            left join (select invoiceCode, invoiceStatus, invoiceStatusDate from invoices) invoices
            on timesheets.invoiceCode = invoices.invoiceCode
            where userID = '{user_id}'
            order by timesheets.dateWorked
        """
    )


def get_timesheet(user_id, timesheet_id):
    return get_results(
        f"""select *  
            from timesheets
            inner join (select hospitalName, hospitals.hospitalID  from hospitals) hospitals
            on timesheets.hospitalID = hospitals.hospitalID
            left join (select invoiceCode, invoiceStatus, invoiceStatusDate from invoices) invoices
            on timesheets.invoiceCode = invoices.invoiceCode
            where userID = '{user_id}' and timesheets.timesheetID = {timesheet_id}
            order by timesheets.dateWorked
        """
    )


def get_unbilled_timesheets(user_id, hospital_id):
    return get_results(
        f"""select *  
            from timesheets
            inner join (select hospitalName, hospitals.hospitalID from hospitals) hospitals
            on timesheets.hospitalID = hospitals.hospitalID
            left join (select invoiceCode, invoiceStatus, invoiceStatusDate from invoices) invoices
            on timesheets.invoiceCode = invoices.invoiceCode
            where userID = '{user_id}' and hospitals.hospitalID = {hospital_id} and timesheets.invoiceCode is null
            order by timesheets.dateWorked
        """
    )


def get_max_invoice_number(user_id, hospital_id):
    return get_results(
        f"""select max(invoices.invoiceNumber) as max_invoice
            from invoices
            where invoices.invoiceHospitalID = {hospital_id} and invoices.invoiceUserID = '{user_id}'
        """
    )


def get_user_hospitals(user_id):
    return get_results(
        f"""select *
            from hospitals
            inner join user_hospitals
            on hospitals.hospitalID = user_hospitals.hospitalId
            where user_hospitals.userId = '{user_id}'
            order by hospitals.hospitalName;"""
    )


def get_hospital(user_id, hospital_id):
    return get_results(
        f"""select *
            from hospitals
            inner join user_hospitals
            on hospitals.hospitalID = user_hospitals.hospitalId
            where user_hospitals.userId = '{user_id}' and hospitals.hospitalID = {hospital_id}
            order by hospitals.hospitalName;
        """
    )


def get_invoices(user_id):
    return get_results(
        f"""
            select * 
            from invoices
            inner join (select hospitalName, hospitalID from hospitals) hospitals
            on invoices.invoiceHospitalID = hospitals.hospitalID
            where invoiceUserID = '{user_id}'
        """
    )


def get_invoice(user_id, invoice_code):
    return get_results(
        f"""
            select * 
            from invoices
            inner join (select hospitalName, hospitalID from hospitals) hospitals
            on invoices.invoiceHospitalID = hospitals.hospitalID
            where invoiceUserID = '{user_id}' and invoiceCode = '{invoice_code}'
        """
    )


def get_invoice_items(user_id, invoice_code):
    return get_results(
        f"""select *  
            from timesheets
            inner join (select hospitalName, hospitals.hospitalID  from hospitals) hospitals
            on timesheets.hospitalID = hospitals.hospitalID
            left join (select invoiceCode, invoiceStatus, invoiceStatusDate from invoices) invoices
            on timesheets.invoiceCode = invoices.invoiceCode
            where userID = '{user_id}' and timesheets.invoiceCode = '{invoice_code}'
            order by timesheets.dateWorked
        """
    )


def create_invoice(user_id, timesheet_ids, invoice_code, max_invoice_number):
    timesheets = []
    for timesheet_id in timesheet_ids:
        timesheets.append(get_timesheet(user_id, timesheet_id))

    invoice_total = 0
    for timesheet in timesheets:
        invoice_total += float(timesheet[0]["dailyAmount"])

    hospital_id = timesheets[0][0]["hospitalID"]

    with engine.connect() as conn:
        query = text(
            """ INSERT INTO invoices
                SET invoiceCode = :invoiceCode,
                    invoiceNumber = :invoiceNumber,
                    invoiceStatus = :invoiceStatus,
                    invoiceStatusDate = :invoiceStatusDate,
                    invoiceTotal = :invoiceTotal,
                    invoiceUserID = :invoiceUserID,
                    invoiceHospitalID = :invoiceHospitalID
            """
        )

        query_params = {
            "invoiceCode": invoice_code,
            "invoiceNumber": max_invoice_number,
            "invoiceStatus": "Pending",
            "invoiceStatusDate": datetime.today(),
            "invoiceTotal": invoice_total,
            "invoiceUserID": user_id,
            "invoiceHospitalID": hospital_id,
        }

        conn.execute(
            statement=query,
            parameters=query_params,
        )

        for timesheet_id in timesheet_ids:
            query = text(
                f"""UPDATE timesheets
                    SET invoiceCode = :invoiceCode
                    WHERE timesheetID =  :timesheetID
                """
            )

            query_params = {
                "invoiceCode": invoice_code,
                "timesheetID": timesheet_id,
            }

            conn.execute(
                statement=query,
                parameters=query_params,
            )


def update_invoice_status(user_id, invoice_code, invoice_status):
    with engine.connect() as conn:
        query = text(
            f"""UPDATE invoices
                SET invoiceStatus = :invoiceStatus,
                    invoiceStatusDate = :invoiceStatusDate
                WHERE invoiceCode = :invoiceCode and invoiceUserID = :invoiceUserID
            """
        )

        query_params = {
            "invoiceStatus": invoice_status,
            "invoiceStatusDate": datetime.now(),
            "invoiceCode": invoice_code,
            "invoiceUserID": user_id,
        }

        conn.execute(
            statement=query,
            parameters=query_params,
        )


def add_time_to_database(user_id, data):
    time_in = data["date_worked"] + " " + data["clock_in"]
    time_out = data["date_worked"] + " " + data["clock_out"]

    time_worked_in_seconds = (
        datetime.strptime(time_out, "%Y-%m-%d %H:%M").timestamp()
        - datetime.strptime(time_in, "%Y-%m-%d %H:%M").timestamp()
    )

    daily_amount = float(data["rate_amount"])  # Per shift amount by default
    if data["rate_type"].lower() == "hourly":
        daily_amount = (time_worked_in_seconds) / 3600 * float(data["rate_amount"])
    daily_amount = round(daily_amount, 2)

    with engine.connect() as conn:
        query = text(
            """INSERT INTO timesheets (userID, hospitalID, clockInTime, clockOutTime, timeWorkedInSeconds, dateWorked, rateAmount, rateType, dailyAmount)
                VALUES (:userID, :hospitalID, :clockInTime, :clockOutTime, :timeWorkedInSeconds, :dateWorked, :rateAmount, :rateType, :dailyAmount)"""
        )
        query_params = {
            "userID": user_id,
            "hospitalID": int(data["hospital_id"]),
            "clockInTime": time_in,
            "clockOutTime": time_out,
            "timeWorkedInSeconds": time_worked_in_seconds,
            "dateWorked": data["date_worked"],
            "rateAmount": float(data["rate_amount"]),
            "rateType": data["rate_type"].capitalize(),
            "dailyAmount": daily_amount,
        }

        conn.execute(
            statement=query,
            parameters=query_params,
        )


def add_hospital_to_database(user_id, data):
    with engine.connect() as conn:
        query = text(
            """INSERT INTO hospitals (hospitalName, hospitalCode, hospitalAddress, hospitalCity, hospitalState, hospitalZip, hospitalPhone, hospitalEmail)
                VALUES (:hospitalName, :hospitalCode, :hospitalAddress, :hospitalCity, :hospitalState, :hospitalZip, :hospitalPhone, :hospitalEmail)"""
        )
        query_params = {
            "hospitalName": data["hospital_name"],
            "hospitalCode": data["hospital_code"].upper(),
            "hospitalAddress": data["hospital_address"],
            "hospitalCity": data["hospital_city"],
            "hospitalState": data["hospital_state"],
            "hospitalZip": str(data["hospital_zip"]),
            "hospitalPhone": data["hospital_phone"],
            "hospitalEmail": data["hospital_email"],
        }

        hospital_id = conn.execute(
            statement=query,
            parameters=query_params,
        ).lastrowid

        query = text(
            """INSERT INTO user_hospitals (userID, hospitalID)
                VALUES (:userID, :hospitalID)"""
        )
        query_params = {
            "userID": user_id,
            "hospitalID": hospital_id,
        }

        conn.execute(
            statement=query,
            parameters=query_params,
        )

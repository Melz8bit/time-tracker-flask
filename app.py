from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
from datetime import datetime, date
from jinja2 import Template

import database
import locale
import os

app = Flask(__name__)
app.secret_key = os.getenv("APP_KEY")

date_template = Template("{{ date.strftime('%I:%M %p')}}")

USER_ID = "318b423c-1da8-4d07-b3e6-e1321562a90a"


@app.route("/")
def home():
    users = database.get_user(USER_ID)
    timesheets = database.get_timesheets(USER_ID)
    hospitals = database.get_user_hospitals(USER_ID)
    invoices = database.get_invoices(USER_ID)

    return render_template(
        "main.html",
        users=users,
        timesheets=timesheets[-10:],
        hospitals=hospitals,
        invoices=invoices,
    )


@app.route("/time/add", methods=["GET", "POST"])
def save_time():
    if request.method == "POST":
        data = request.form
        database.add_time_to_database(USER_ID, data)
        flash("Shift has been recorded")
        return redirect(url_for("home"))

    user_hospitals = database.get_user_hospitals(USER_ID)
    return render_template(
        "add_time_form.html",
        user_hospitals=user_hospitals,
    )


@app.route("/timesheets")
def show_all_timesheets():
    return render_template(
        "timesheets.html",
        timesheets=database.get_timesheets(USER_ID),
    )


@app.route("/hospital/add", methods=["GET", "POST"])
def save_hospital():
    if request.method == "POST":
        data = request.form
        database.add_hospital_to_database(USER_ID, data)
        flash("Hospital has been added")
        return redirect(url_for("home"))

    user_hospitals = database.get_user_hospitals(USER_ID)
    return render_template(
        "add_hospital_form.html",
        user_hospitals=user_hospitals,
    )


@app.route("/invoice/create", methods=["GET", "POST"])
def create_invoice():
    if request.method == "POST":
        invoice_code = request.form.get("invoice_code")
        timesheet_ids = request.form.getlist("timesheet_id")
        max_invoice_number = request.form.get("max_invoice_number")
        database.create_invoice(
            USER_ID, timesheet_ids, invoice_code, max_invoice_number
        )
        flash("Invoice has been created")
        return redirect(url_for("home"))

    if request.args:
        hospital_id = request.args.get("hospital_id")
        timesheets = database.get_unbilled_timesheets(
            USER_ID,
            hospital_id,
        )
        user_hospitals = database.get_hospital(USER_ID, hospital_id)

        max_invoice_number = database.get_max_invoice_number(USER_ID, hospital_id)[0][
            "max_invoice"
        ]
        if not max_invoice_number:
            max_invoice_number = 0

        invoice_code = user_hospitals[0]["hospitalCode"] + str.zfill(
            str(max_invoice_number + 1), 4
        )

        print(f"{user_hospitals=}")
        print(f"{timesheets=}")
        print(f"{invoice_code=}")
        print(f"{max_invoice_number=}")

        return render_template(
            "create_invoice_form.html",
            user_hospitals=user_hospitals,
            timesheets=timesheets,
            invoice_code=invoice_code,
            max_invoice_number=(1 if max_invoice_number == 0 else max_invoice_number),
            request_method="POST",
        )

    user_hospitals = database.get_user_hospitals(USER_ID)
    return render_template(
        "create_invoice_form.html",
        user_hospitals=user_hospitals,
    )


@app.route("/hospitals")
def show_all_hospitals():
    return render_template(
        "hospitals.html",
        hospitals=database.get_user_hospitals(USER_ID),
    )


@app.route("/invoices", methods=["GET", "POST"])
def show_all_invoices():
    if request.method == "POST":
        invoice_status = request.form.get("invoice_status")
        invoice_code = request.form.get("invoice_code")

        database.update_invoice_status(USER_ID, invoice_code, invoice_status)

        flash("Invoice status has been updated")
        return redirect(url_for("show_all_invoices"))

    return render_template(
        "invoices.html",
        hospitals=database.get_user_hospitals(USER_ID),
        invoices=database.get_invoices(USER_ID),
        timesheets=database.get_timesheets(USER_ID),
    )


@app.route("/invoice/print")
def print_invoice():
    user_info = database.get_user(USER_ID)[0]

    hospital_info = database.get_hospital(
        USER_ID,
        request.args.get("hospital_id"),
    )[0]

    invoice_items = database.get_invoice_items(
        USER_ID,
        request.args.get("invoice_code"),
    )

    invoice_info = database.get_invoice(
        USER_ID,
        request.args.get("invoice_code"),
    )[0]

    return render_template(
        "invoice_print_form.html",
        user_info=user_info,
        hospital_info=hospital_info,
        invoice_items=invoice_items,
        invoice_info=invoice_info,
        today_date=date.today().strftime("%m/%d/%Y"),
    )


@app.template_filter()
def format_currency(value):
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    if not value:
        return locale.currency(0, symbol=True, grouping=True)

    return locale.currency(value, symbol=True, grouping=True)


@app.template_filter()
def format_phone_number(value):
    return format(int(value[:-1]), ",").replace(",", "-") + value[-1]


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

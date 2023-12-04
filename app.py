import locale
import os
import uuid
from datetime import date, datetime
from dotenv import load_dotenv

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    login_required,
    current_user,
    login_user,
    logout_user,
)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length
from jinja2 import Template
from werkzeug.security import generate_password_hash, check_password_hash

import database
from database import db_connect, create_session

from models import users

from sqlalchemy import select, null

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_KEY")

engine, connection = db_connect()
session = create_session(engine)

date_template = Template("{{ date.strftime('%I:%M %p')}}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USER_ID = ""


class RegisterForm(FlaskForm):
    first_name = StringField("First name:", validators=[DataRequired()])
    last_name = StringField("Last name:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired()])
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField(
        "Password:",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
        ],
    )
    password2 = PasswordField("Confirm password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Login")


@login_manager.user_loader
def load_user(user_id):
    user_id_query = (
        select(users.Users).select_from(users.Users).filter(users.Users.id == user_id)
    )
    return session.execute(user_id_query).first()[0]


@app.route("/")
@login_required
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


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        form.username.data = ""
        form.password.data = ""

        password_query = (
            select(users.Users.userPassword)
            .select_from(users.Users)
            .filter(users.Users.username == username)
        )
        user_db_password = session.execute(password_query).first()
        if user_db_password:
            if check_password_hash(user_db_password[0], password):
                user_id_query = (
                    select(users.Users)
                    .select_from(users.Users)
                    .filter(users.Users.username == username)
                )
                user = session.execute(user_id_query).first()[0]

                login_user(user)

                global USER_ID
                USER_ID = session.execute(user_id_query).first()[0].id

                # flash("Login successful")
                return redirect(url_for("home"))
            else:
                flash("Incorrect username or password!")
        else:
            flash("User does not exist!")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register_user():
    first_name = None
    last_name = None
    email = None
    username = None
    password = None
    password2 = None
    form = RegisterForm()

    # Validate Form
    if form.validate_on_submit():
        user_query = (
            select(users.Users.email)
            .select_from(users.Users)
            .filter(users.Users.email == form.email.data)
        )
        result = session.execute(user_query).first()

        if not result:
            password_hash = generate_password_hash(form.password.data)
            user = users.Users(
                id=str(uuid.uuid4()),
                username=form.username.data,
                firstName=form.first_name.data,
                lastName=form.last_name.data,
                email=form.email.data,
                userPassword=password_hash,
                userRole="Standard",
            )
            session.add(user)
            session.commit()
            flash("User added")
            return render_template(
                "login.html",
                form=form,
            )
        else:
            session.rollback()

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data

        form.first_name.data = ""
        form.last_name.data = ""
        form.email.data = ""
        form.username.data = ""
        form.password.data = ""

    return render_template(
        "register.html",
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        password=password,
        form=form,
    )


@app.route("/time/add", methods=["GET", "POST"])
@login_required
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
@login_required
def show_all_timesheets():
    return render_template(
        "timesheets.html",
        timesheets=database.get_timesheets(USER_ID),
    )


@app.route("/hospital/add", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
def show_all_hospitals():
    return render_template(
        "hospitals.html",
        hospitals=database.get_user_hospitals(USER_ID),
    )


@app.route("/invoices", methods=["GET", "POST"])
@login_required
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
@login_required
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
    # locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    value = format(value, ",.2f")

    if not value:
        return "$0.00"
        # return locale.currency(0, symbol=True, grouping=True)

    return "$" + str(value)
    # return locale.currency(value, symbol=True, grouping=True)


@app.template_filter()
def format_phone_number(value):
    return format(int(value[:-1]), ",").replace(",", "-") + value[-1]


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

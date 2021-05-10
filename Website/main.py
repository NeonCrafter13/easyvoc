# Pre Installed Imports
import os
from flask import Flask, templating, request, escape, session, redirect, make_response
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_mail import Mail, Message
import json
from threading import Thread
from dotenv import load_dotenv
# self written included Imports
from db import userdb, taskdb, requestdb
import tokenVal
# Blueprints Imports
from admin import admin

load_dotenv(dotenv_path=".envvar")

RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_USE_TLS = int(os.getenv("MAIL_USE_TLS"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

app = Flask(__name__)
app.config.from_object(__name__)

app.register_blueprint(admin, url_prefix="/admin")

app.secret_key = os.getenv("flask_key")
app.static_folder = 'static'
mail = Mail(app)
mail.connect()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_password_reset_email(user):
    token = tokenVal.get_reset_password_token(user)
    msg = Message(
        subject='easyvoc | Zurücksetzen ihres Passwortes',
        sender="easyvoc",
        recipients=[user], body=templating.render_template(
            'email/reset_password.txt',
            user=user,
            token=token
        ),
        html=templating.render_template(
            'email/reset_password.html',
            user=user,
            token=token
        )
    )
    Thread(target=send_async_email, args=(app, msg)).start()

def send_authentication_email(user):
    token = tokenVal.get_authentication_token(user)
    msg = Message(
        subject='easyvoc | Authentifizierung ihres Accounts',
        sender="easyvoc",
        recipients=[user[3]],
        body=templating.render_template(
            'email/authentication.txt',
            user=user, token=token
        ),
        html=templating.render_template(
            'email/authentication.html',
            user=user,
            token=token
        )
    )
    Thread(target=send_async_email, args=(app, msg)).start()


class RegisterForm(FlaskForm):
    recaptcha = RecaptchaField()

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Passwort Zurücksetzung beantragen')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Passwort ändern')

@app.route("/datenschutz", methods=["GET"])
def datenschutz():
    return templating.render_template("datenschutz.html")

@app.route("/send_authentication_email", methods=["GET"])
def show_authentication_email():
    user = None
    if "name" in session:
        user = session["name"]
        information = userdb.Get_User(user)
        if not information:
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um diese Aktion durchzuführen"
    if information[7] == 1:
        return "Sie sind schon Email-verifiziert"
    send_authentication_email(information)
    return redirect("/check_email")

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if user:
        return redirect("/")

    user = tokenVal.verify_reset_password_token(token)
    if not user:
        return redirect('/')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        userdb.Change_Pwd_without_oldpwd(user[1], form.password.data)
        return redirect('/login?success=Passwort erfolgreich geändert')
    return templating.render_template('reset_password.html', form=form)

@app.route("/autheticate/<token>", methods=["GET"])
def autheticate(token):
    user = tokenVal.verify_authentication_token(token)
    if user is None:
        return "Ihr token ist abgelaufen oder nicht existent. Beantragen sie ein neues token unter Account."
    userdb.SetAuthentication(user[1])
    return templating.render_template("autheticate.html")

@app.route('/reset_password_request', methods=['GET', "POST"])
def reset_password_request():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if user:
        return redirect("/")
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = userdb.Get_User_Email(form.email.data)
        if user:
            if user[7] == 1:
                send_password_reset_email(user[3])
        return redirect('/check_email')

    return templating.render_template(
        'reset_password_request.html',
        title='Reset Password',
        form=form
    )


@app.route("/check_email", methods=["GET"])
def view_check_email():
    return templating.render_template("/check_email.html")


@app.route("/", methods=["POST", "GET"])
def main():
    a = None
    name = ""
    permcreate = None
    if request.method == "POST":
        name = request.form["username"]
        pwd = request.form["pwd"]
        if userdb.Login(name, pwd):
            session["name"] = request.form["username"]
        else:
            return redirect("/login?error=1")

    if "name" in session:
        info = userdb.Get_User(session["name"])
        if not info:
            return "error"
        if info[4] == 1:
            permcreate = True
            user = escape(session["name"])
    else:
        user = None

    return templating.render_template(
        "home.html",
        username=user,
        permcreate=permcreate
    )


@app.route("/account")
def acount():
    try:
        error = request.args["error"]
    except:
        error = None
    try:
        success = request.args["success"]
    except:
        success = None
    user = None
    information = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None

    if user:
        information = userdb.Get_User(user)

    return templating.render_template(
        "account.html", user=escape(user),
        information=information, error=error,
        success=success
    )


@app.route("/delete_account", methods=["POST"])
def delete_account():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen für diese Aktion eingeloggt sein"

    option = request.form["options"]
    userdb.Delete_Account(user)
    if option == "delete":
        taskdb.DeleteTask(user)
    if option == "anonym":
        taskdb.AnonymTask(user)

    return redirect("/logout")


@app.route("/changepwd", methods=["POST"])
def changepwd():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None

    if not user:
        return "error"

    old_pwd = request.form["old_pwd"]
    new_pwd1 = request.form["new_pwd1"]
    new_pwd2 = request.form["new_pwd2"]

    if new_pwd1 != new_pwd2:
        return redirect("/account?error=Passwörter stimmen nicht über ein")

    a = userdb.Change_Pwd(user, old_pwd, new_pwd1)
    if a == False:
        return redirect("/account?error=Altes Passwort nicht richtig")

    return redirect("/account?success=Sie haben ihr Passwort erfolgreich geändert")


@app.route("/change_email", methods=["POST"])
def change_email():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "error"

    email = request.form["email"]
    pwd = request.form["pwd"]
    a = userdb.Change_Email(user, email, pwd)
    if a is True:
        return redirect("/account?success=Email erfolgreich geändert")
    else:
        return redirect(f"/account?error={ a }")
    return "error"


@app.route("/report", methods=["POST"])
def report():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "error"

    type = request.form.get("type")
    if type == "task":
        name = request.form.get("task")
        reason = request.form.get("reason_task")
    elif type == "voc":
        name = request.form.get("voc")
        reason = request.form.get("reason_voc")    
    else:
        return "Error", 400

    requestdb.CreateReport(user, type, name, reason)
    return templating.render_template("report.html")


@app.route("/permcreate_request", methods=["POST"])
def permcreate_request():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "error"

    why = request.form["why"]
    if requestdb.CreatePermCreateRequest(user, why) == True:
        return redirect("/account?success=Anfrage erfolgreich gesendet")
    else:
        return redirect("/account?error=Error")


@app.route("/searchtask", methods=["GET"])
def search_task():
    name = request.args.get("name")
    Englisch = None
    Spanisch = None
    Englisch = request.cookies.get("Englisch")
    Spanisch = request.cookies.get("Spanisch")

    tasks = taskdb.search(name)
    return templating.render_template(
        "search.html",
        tasks=tasks,
        Englisch=Englisch,
        Spanisch=Spanisch
    )


@app.route("/selecttask")
def SelectTask():
    Englisch = None
    Spanisch = None
    Englisch = request.cookies.get("Englisch")
    Spanisch = request.cookies.get("Spanisch")

    tasks = taskdb.GetallTasks()
    return templating.render_template(
        "selecttask.html",
        tasks=tasks,
        Englisch=Englisch,
        Spanisch=Spanisch
    )


@app.route("/settings", methods=["POST"])
def settings():
    if request.method == "POST":
        try:
            Englisch = request.form["Englisch"]
        except:
            Englisch = "off"
        try:
            Spanisch = request.form["Spanisch"]
        except:
            Spanisch = "off"

    resp = make_response(redirect("/selecttask"))
    resp.set_cookie("Englisch", Englisch)
    resp.set_cookie("Spanisch", Spanisch)
    return resp


@app.route("/logout")
def logout():
    session.clear()
    # session.pop("name", None)
    return redirect("/")


@app.route("/dotask", methods=["GET"])
def dotask():
    user = None
    task = request.args.get("name")
    task = taskdb.GetTask(task)

    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
        else:
            if not task == None:
                vocs = list(task[1])
                for i in range(0,len(vocs)):
                    session[str(i)] = vocs[i]

    Settings = [request.cookies.get("Englisch"), request.cookies.get("Spanisch")]
    return templating.render_template(
        "dotask.html",
        Settings=Settings,
        User=escape(user),
        Task=task
    )


@app.route("/result", methods=["POST"])
def result():
    user = None
    data = None
    vocs = []
    for i in range(0, 26):
        if str(i) in session:
            vocs.append(session[str(i)])

    Settings = [request.cookies.get("Englisch"), request.cookies.get("Spanisch")]

    Final = []

    data = request.form
    check = False
    if data is None:
        return "Error"

    for i in vocs:
        correct1 = None
        correct2 = None
        if Settings[0] == "on":
            if i + "_1" in data:
                Eingabe = data[i + "_1"]
                correct = taskdb.GetVoc(i)[1]
                correct1 = [Eingabe, correct]
                check = True
        if Settings[1] == "on":
            if i + "_2" in data:
                Eingabe = data[i + "_2"]
                correct = taskdb.GetVoc(i)[2]
                correct2 = [Eingabe, correct]
                check = True
        if not check:
            return "Error"
        Final.append([i, correct1, correct2])

    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    return templating.render_template(
        "result.html",
        user=user,
        data=Final,
        settings=Settings
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    success = None
    if request.method == "POST":
        form = RegisterForm()
        if not form.validate_on_submit():
            return redirect("/register?error=Sie müssen das recaptcha ausfüllen!")
        name = request.form["username"]
        pwd1 = request.form["pwd1"]
        pwd2 = request.form["pwd2"]
        email = request.form["email"]
        if name != "" or pwd1 != "" or pwd2 != "" or email != "":
            if pwd1 == pwd2:
                a = userdb.Create_User(name, pwd1, email)
                if a == None:
                    return redirect("/register")
                if type(a) == str:
                    return redirect("/register?error=" + a)
                error = None
                send_authentication_email(userdb.Get_User(name))
                success = "Account erstellt und Email zur Bestätigung geschickt!"

            else:
                return redirect("/register?error=Zweites Passwort entsprach nicht dem ersten!")
        else:
            return redirect("/register?error=Alle Felder müssen ausgefüllt werden!")
    else:
        error = request.args.get("error")
        if not error == "1":
            error = None
    if success is None:
        success = request.args.get("success")
    return templating.render_template("login.html", error=error, success=success)


@app.route("/register", methods=["GET"])
def Register(form=None):
    if form is None:
        form = RegisterForm()
    error = request.args.get("error")
    if error == "":
        error = None
    return templating.render_template("register.html", error=error, form=form)


@app.route("/createtask", methods=["GET"])
def createtask():
    error = request.args.get("error")
    username = None
    permcreate = False
    if "name" in session:
        username = session["name"]
        user = userdb.Get_User(username)
        if not user:
            username = None
    if username is not None:
        if user[4] == 1:
            permcreate = True
        else:
            permcreate = False

    return templating.render_template(
        "createtask.html",
        user=escape(username),
        permcreate=permcreate,
        error=error
    )


@app.route("/backcreatetask", methods=["POST"])
def backcreatetask():
    user = None
    final = []
    vocs = []
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if user:
        i = 0
        name = request.form["name"]
        desc = request.form["description"]
        author = user
        image = request.form["image"]

        if image == "":
            image = "None"

        while True:
            i = i + 1
            try:
                a = request.form[str(i)]
                if a != "":
                    vocs.append(a)
            except:
                break
        if not taskdb.CreateTask(name, desc, author, vocs, image):
            return redirect("/createtask?error=Aufgabe mit diesem Namen schon vorhanden!")

        for i in vocs:
            a = taskdb.GetVoc(i)
            if a != None:
                Englisch = a[1]
                Spanisch = a[2]
                final.append([i, Englisch, Spanisch])
            else:
                final.append([i, [None], [None]])

    resp = make_response(templating.render_template("backcreatetask.html", user=escape(user), data=final))
    resp.set_cookie("vocs", json.dumps(vocs))

    return resp

@app.route("/backcreatetask2", methods=["POST"])
def backcreatetask2():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None

    if user:
        a = request.cookies["vocs"]
        try:
            a = json.loads(a)
        except:
            return "error"
        for i in a:
            try:
                Englisch = request.form[i + "Englisch"]
            except:
                Englisch = None
            try:
                Spanisch = request.form[i + "Spanisch"]
            except:
                Spanisch = None
            if Englisch is not None and Spanisch is not None:
                taskdb.AddVoc(i, Englisch, Spanisch)
    else:
        return "Please log in to do this action"

    return templating.render_template("backcreatetask2.html")


if __name__ == '__main__':
    app.run(port=80, threaded=True, host="0.0.0.0")

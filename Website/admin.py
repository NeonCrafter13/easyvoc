from flask import Blueprint, templating, session, escape, request

from db import userdb, requestdb, taskdb

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

@admin.route("/")
def overview():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None

    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"

    userinformation = userdb.Get_User(user)
    if userinformation[6] == 1:
        securitylevel = 1
    elif userinformation[6] == 2:
        securitylevel = 2
    else:
        securitylevel = 0

    return templating.render_template("admin/admin.html", user=escape(user), securitylevel=securitylevel)

@admin.route("/request_permcreate")
def show_requests_permcreate():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"
    userinformation = userdb.Get_User(user)
    if userinformation[6] == 0:
        return "Sie haben dafür keine Rechte"
    data = requestdb.GetAllPermcreate()
    return templating.render_template("admin/request_permcreate.html", data=data)

@admin.route("/accept_request_permcreate", methods=["POST"])
def accept_request_permcreate():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"

    userinformation = userdb.Get_User(user)
    if userinformation[6] == 0:
        return "Sie haben dafür keine Rechte"

    id = request.form["id"]
    r = requestdb.GetRequestsPermCreate(id)
    if r == None:
        return "Konnte die Anfrage nicht finden"
    userdb.SetPermCreate(r[1])
    requestdb.DeleteRequestPermCreate(id)
    return templating.render_template("/admin/accept_request_permcreate.html")

@admin.route("/refuse_request_permcreate", methods=["POST"])
def refuse_request_permcreate():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"
    userinformation = userdb.Get_User(user)
    if userinformation[6] == 0:
        return "Sie haben dafür keine Rechte"

    try:
        id = request.form["id"]
    except:
        return "error"
    requestdb.DeleteRequestPermCreate(id)
    return templating.render_template("admin/refuse_request_permcreate.html")


@admin.route("/reports", methods=["GET"])
def show_reports():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"

    userinformation = userdb.Get_User(user)
    if userinformation[6] == 0:
        return "Sie haben dafür keine Rechte"

    data = requestdb.GetAllReports()
    return templating.render_template("admin/reports.html", data=data)

@admin.route("/accept_report", methods=["POST"])
def accept_report():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"
    userinformation = userdb.Get_User(user)
    if userinformation[6] == 0:
        return "Sie haben dafür keine Rechte"

    id = request.form["id"]
    options = request.form["options"]
    if options == "nothing":
        requestdb.DeleteReport(id)
    elif options == "delete":
        information = requestdb.GetReport(id)
        if information == None:
            return "error"
        elif information[2] == "voc":
            taskdb.DeleteVoc(information[3])
            requestdb.DeleteReport(id)
        elif information[2] == "task":
            taskdb.DeleteTaskName(information[3])
            requestdb.DeleteReport(id)
        else:
            return "error"
    elif options == "delete+":
        information = requestdb.GetReport(id)
        if information == None:
            return "error"
        elif information[2] == "voc":
            taskdb.DeleteVoc(information[3])
            requestdb.DeleteReport(id)
        elif information[2] == "task":
            author = taskdb.GetTaskAuthor(information[3])
            taskdb.DeleteTaskName(information[3])
            userdb.Delete_Account(author)
            requestdb.DeleteReport(id)
        else:
            return "error"
    return templating.render_template("admin/accept_report.html")

@admin.route("/refuse_report", methods=["POST"])
def refuse_report():
    user = None
    if "name" in session:
        user = session["name"]
        if not userdb.Get_User(user):
            user = None
    if not user:
        return "Sie müssen eingeloggt sein um die Admin-page zu benutzen"
    userinformation = userdb.Get_User(user)
    if userinformation[6] == 0:
        return "Sie haben dafür keine Rechte"

    try:
        id = request.form["id"]
    except:
        return "error"
    requestdb.DeleteReport(id)
    return templating.render_template("admin/refuse_report.html")

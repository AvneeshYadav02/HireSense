def dashboard():
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from functools import wraps
from flask import abort

employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


def employee_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "employee":
            abort(403)
        return f(*args, **kwargs)
    return decorated


@employee_bp.route("/")
@employee_required
def dashboard():
    return render_template("employee/dashboard.html")

def dashboard():
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from functools import wraps
from flask import abort

manager_bp = Blueprint("manager", __name__, url_prefix="/manager")


def manager_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "manager":
            abort(403)
        return f(*args, **kwargs)
    return decorated


@manager_bp.route("/")
@manager_required
def dashboard():
    return render_template("manager/dashboard.html")

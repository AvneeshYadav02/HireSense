from flask import Blueprint, render_template
from flask_login import current_user, login_required

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

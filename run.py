import os
from app import create_app, db
from app.models import User

port = int(os.environ.get("PORT", 5010))
app = create_app(port)


def seed_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@hiresense.local",
                role="admin",
            )
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "Admin@1234"))
            db.session.add(admin)
            db.session.commit()


seed_admin()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false") == "true")

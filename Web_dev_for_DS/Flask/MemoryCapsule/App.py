import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///capsule.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB upload limit
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_for_prod")

db = SQLAlchemy(app)

# Models  - defining models before creating tables
class Capsule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    unlock_at = db.Column(db.DateTime, nullable=False)  # stored in UTC
    owner = db.Column(db.String(120), nullable=True)  # optional
    recipient_email = db.Column(db.String(120), nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    image_name = db.Column(db.String(260), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)  # small images only

    def is_unlocked(self):
        now_ist = datetime.now(IST)
        ua = self.unlock_at

        if ua is None:
            return False

        # Ensure stored value is IST-aware
        if ua.tzinfo is None:
            ua = ua.replace(tzinfo=IST)

        return now_ist >= ua

    def status(self):
        if self.opened_at:
            return "opened"
        if self.is_unlocked():
            return "unlocked"
        return "locked"


# Create tables (run once, after models are defined)

with app.app_context():
    db.create_all()


# Helpers

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}
def allowed_filename(filename):
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in ALLOWED_EXT

def parse_ist_datetime(s):
    """
    Parse HTML datetime-local (naive) as IST.
    Returns an IST-aware datetime.
    """
    try:
        # Parse naive datetime from HTML form
        dt = datetime.fromisoformat(s)
        # Attach IST timezone
        return dt.replace(tzinfo=IST)
    except Exception:
        return None



# Routes (same as before)

@app.route("/")
def index():
    capsules = Capsule.query.order_by(Capsule.created_at.desc()).all()
    return render_template("index.html", capsules=capsules)

@app.route("/capsule/new", methods=["GET", "POST"])
def new_capsule():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body = (request.form.get("body") or "").strip()
        unlock_raw = request.form.get("unlock_at")
        owner = (request.form.get("owner") or "").strip() or None
        recipient = (request.form.get("recipient") or "").strip() or None

        errors = []
        if not title:
            errors.append("Give this capsule a short title.")
        if not body:
            errors.append("Write something for future-you; empty capsules are sad.")
        if not unlock_raw:
            errors.append("Pick a date/time when the capsule should open.")
        else:
            unlock_dt = parse_ist_datetime(unlock_raw)
            if not unlock_dt:
                errors.append("Could not read the unlock time. Use the control provided.")
            else:
                now = datetime.now(timezone.utc)
                if unlock_dt <= now:
                    errors.append("Unlock time must be in the future.")
        img = request.files.get("image")
        img_name = None
        img_data = None
        if img and img.filename:
            if not allowed_filename(img.filename):
                errors.append("Image type not allowed. Use PNG/JPG/GIF.")
            else:
                img_name = secure_filename(img.filename)
                img_data = img.read()
                if len(img_data) > app.config["MAX_CONTENT_LENGTH"]:
                    errors.append("Image too large. Keep it under 2 MB.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("new_capsule.html", form=request.form)

        c = Capsule(
            title=title,
            body=body,
            unlock_at=unlock_dt,
            owner=owner,
            recipient_email=recipient,
            image_name=img_name,
            image_data=img_data,
        )
        db.session.add(c)
        db.session.commit()
        flash("Capsule tucked away. It will open when the time comes.", "success")
        return redirect(url_for("index"))

    return render_template("new_capsule.html")

@app.route("/capsule/<int:cid>")
def view_capsule(cid):
    c = Capsule.query.get_or_404(cid)
    return render_template("view_capsule.html", cap=c)

@app.route("/capsule/<int:cid>/open", methods=["POST"])
def open_capsule(cid):
    c = Capsule.query.get_or_404(cid)
    if not c.is_unlocked():
        flash("Not yet time to open this capsule.", "danger")
        return redirect(url_for("view_capsule", cid=cid))
    if not c.opened_at:
        c.opened_at = datetime.now(timezone.utc)
        db.session.commit()
    flash("Opened. Hope future-you was kind to past-you.", "info")
    return redirect(url_for("view_capsule", cid=cid))

@app.route("/capsule/<int:cid>/delete", methods=["POST"])
def delete_capsule(cid):
    c = Capsule.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash("Capsule deleted.", "warning")
    return redirect(url_for("index"))

@app.route("/capsule/<int:cid>/image")
def capsule_image(cid):
    c = Capsule.query.get_or_404(cid)
    if not c.image_data:
        abort(404)
    return send_file(BytesIO(c.image_data), download_name=c.image_name, as_attachment=False)

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Upload too large. Keep images under 2 MB.", "danger")
    return redirect(request.referrer or url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

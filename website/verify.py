import pyotp
import qrcode
import io
from flask import Blueprint, render_template, redirect, request, jsonify, flash, url_for, Response, session, send_file, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db


verify = Blueprint("verify", __name__)

@verify.route("/auth", methods=["GET", "POST"])
@login_required
def google_auth():
    user = User.query.filter_by(id=current_user.id).first()
    
    if request.method == "POST":
        code = request.form.get("code")
        totp = pyotp.TOTP(user.google_verify)
        if totp.verify(code):
            session["auth"] = True
            flash("2FA successfull! Logged in!", category="success")
            return redirect(url_for("views.account", session_id=user.account, _external=True))
        else:
            flash("Wrong 2FA code", category="error")
            return redirect(url_for('verify.google_auth'))  

    if user.google_verify:
        return render_template("2fa.html", user=current_user, firsttime=False)
    else:
        secret = pyotp.random_base32()
        user.google_verify = secret
        db.session.commit()  
        return render_template("2fa.html", user=current_user, firsttime=True)



@verify.route("/qrcode/<username>")
def qrcode_png(username):
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return "Benutzer nicht gefunden", 404
    secret = user.google_verify
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name=f"SmartLock {username}")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@verify.route("/auth_again")
@login_required
def auth_again():
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return "Benutzer nicht gefunden", 404


    if not user.google_verify:
        secret = pyotp.random_base32()
        user.google_verify = secret
        db.session.commit()
    else:
        secret = user.google_verify

    # QR-Code erzeugen
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user.username, issuer_name=f"SmartLock {user.username}")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # Bild in Base64 umwandeln
    import base64
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    html = f"""
    <h2>2FA Setup für {user.username}</h2>
    <p>Once you have scanned the QR, please click <a href="/auth">here</a>.</p>
    <img src="data:image/png;base64,{img_base64}" alt="QR Code">
    <p>Secret: <input type="text" value="{secret}" readonly>
    <button onclick="navigator.clipboard.writeText('{secret}')">Copy</button></p>
    """

    return html

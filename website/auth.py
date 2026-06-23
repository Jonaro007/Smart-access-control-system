import random
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from .models import User, Device, Logs, AccessCode, CodeApproval, AccessRequest
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
auth = Blueprint("auth", __name__)
from flask_login import login_user, login_required, logout_user, current_user
import secrets, string
import server
import time
from datetime import datetime
from sqlalchemy import or_
from functools import wraps
import mail_handler

def verify_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        
        if session.get("auth") == True:
            flash("Bitte bestätige deine 2FA zuerst", "error")
            return redirect(url_for('verify.google_auth'))  
        
        return f(*args, **kwargs)
    return decorated_function


@auth.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == "POST":
        email = request.form.get('email')
        password1 = request.form.get('password')

        MAX_VERSUCHE = 5
        SPERRE_SEKUNDEN = 600

        session.setdefault("fails", 0)
        session.setdefault("lock_until", 0)

        jetzt = time.time()

        if jetzt < session["lock_until"]:
            flash("Zu viele Login-Versuche. Bitte versuche es später erneut.", category="error")
            return render_template("login.html", user=current_user)
        
        user = User.query.filter(
            or_(User.email == email, User.username == email)
        ).first()
        
        if user:
            if check_password_hash(user.password, password1):  
                flash("Erfolgreich eingeloggt!", category="success")
                session["fails"] = 0
                session["lock_until"] = 0
                if user.email:
                    mail_handler.send_email(
                        recipient=user.email,
                        reason="Login erkannt",
                        extra_info=f"Login time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        userfirstname=user.firstname
                    )
                login_user(user, remember=True)
                return redirect(url_for('views.home')) 
            else:
                flash("Email oder Passwort ist falsch.", category="error")
                session["fails"] += 1

                if session["fails"] >= MAX_VERSUCHE:
                    session["lock_until"] = jetzt + SPERRE_SEKUNDEN
                    session["fails"] = 0
                    flash("Zu viele Login-Versuche. Bitte versuche es später erneut.", category="error")
                    mail_handler.send_email(
                    recipient=user.email,
                    reason="Versuchter Zugriff auf ihr Konto",
                    userfirstname=user.firstname
                    )
                    return render_template("login.html", user=current_user)
        else:
            flash("Email oder Passwort ist falsch.", category="error")

    return render_template("login.html", user=current_user)

@auth.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        passwordconfirm = request.form.get("passwordconfirm")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email existiert bereits", category="error")
        elif len(email) < 4:
            flash("Email ist zu kurz", category="error")
        elif len(firstname) < 2:
            flash('Vorname muss länger als 2 Zeichen sein',category='error')
        elif password != passwordconfirm:
            flash('Passwörter stimmen nicht überein',category='error')
        elif len(password) < 7:
            flash('Passwort muss mindestens 7 Zeichen lang sein',category='error')
        else:
            characters = string.ascii_letters + string.digits + '-_.~'

            secure_string = ''.join(secrets.choice(characters) for _ in range(64))
            door_code = ''.join(secrets.choice(characters) for _ in range(256))
            new_user = User(email=email, username=f"{firstname.lower()}.{name.lower()}" ,firstname=firstname, password=generate_password_hash(password, method='pbkdf2:sha256'), name=name, account=secure_string, door=door_code)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Konto erfolgreich erstellt!',category='success')
            flash('Du musst deinen Smart Lock mit unserem System verknüpfen',category='info')
            return redirect(url_for("views.home"))
    return render_template("signup.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout erfolgreich',category='success')
    session.clear()
    return redirect(url_for('auth.login')) 
    



@auth.route("/esp32/connect", methods=["POST"])
def esp_connect():
    data = request.json
    onetime = data.get("code")
    ip = data.get("ip")

    device = Device.query.filter_by(onetime=onetime).first()
    if device:
        device.ip = ip
        db.session.commit()
        print("Device-IP aktualisiert")
        return jsonify({"status": "ok", "type": "device", "message": "IP updated"}), 200
    
    new_device = Device(onetime=onetime, ip=ip)
    db.session.add(new_device)
    db.session.commit()
    print("Neues Device angelegt")

    new_device = Device(onetime=onetime, ip=ip)
    db.session.add(new_device)
    db.session.commit()
  
    user = User.query.filter_by(onetime=onetime).all()
    if user:
        for u in user:
            u.ip = ip
        db.session.commit()
        print("User-IP aktualisiert")
        return jsonify({"status": "ok", "type": "user", "message": "IP updated"}), 200

  
    return jsonify({"status": "ok", "type": "device", "message": "new device created"}), 201


@auth.route("/set_status/door", methods=["POST"])
@login_required
def set_door():
    door = User.query.filter_by(id=current_user.id).first()

    if not door:
        return jsonify({"status": "error", "message": "Door-Status nicht gefunden"}), 404
    
    if not door.ip:
        device = Device.query.filter_by(onetime=current_user.onetime).first()
        if device:
            door.ip = device.ip
            db.session.commit()
            return jsonify({"status": "error", "message": "Lock ist neu verbunden. Probiere erneut"}), 404
        return jsonify({"status": "error", "message": "Deine Lock ist nicht eingerichtet"}), 404
    
    online = server.check_if_online(door.ip)
    if not online: 
        return jsonify({"status": "error", "message": "Deine Lock ist nicht verbunden"}), 404




    # Status toggeln
    if door.status:  
        server.send_to_client(door.ip, "lock")
        door.status = False
        log_msg = "Locked"
    else:  
        server.send_to_client(door.ip, "unlock")
        door.status = True
        log_msg = "Unlocked"

    # Log erstellen
    new_log = Logs(
        nachrichten=log_msg,
        user_id=current_user.id,
        author=current_user.firstname,
        account=current_user.account
    )

    db.session.add(new_log)
    db.session.commit()

    # Status korrekt für JS zurückgeben
    return jsonify({
        "status": "locked" if not door.status else "unlocked",
        "message": f"Status: {log_msg}"
    })


@auth.route("/check_if_online")
@login_required
def is_online():
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        print("nou")
        return jsonify({"message": "User nicht gefunden"}), 404
        

    if not user.ip:
        print("no c")
        return jsonify({"message": "User hat keine Lock verbunden"}), 404

    online = server.check_if_online(user.ip)

    if online:
        return jsonify({"message": "Online"}), 200
    else:
        return jsonify({"message": "Offline"}), 200


def toggle_door_for_user(user: User):
    if not user:
        return {"status": "error", "message": "Door-Status nicht gefunden"}
    if not user.ip:
        return {"status": "error", "message": "Deine Lock ist nicht eingerichtet"}

    online = server.check_if_online(user.ip)
    if not online:
        return {"status": "error", "message": "Deine Lock ist nicht verbunden"}

    # Status toggeln
    if user.status:
        server.send_to_client(user.ip, "lock")
        user.status = False
        log_msg = "Locked"
    else:
        server.send_to_client(user.ip, "unlock")
        user.status = True
        log_msg = "Unlocked"

    # Log erstellen
    new_log = Logs(
        nachrichten=log_msg,
        user_id=user.id,
        author=user.firstname,
        account=current_user.account
    )
    db.session.add(new_log)
    db.session.add(user)
    db.session.commit()

    return {"status": "locked" if not user.status else "unlocked", "message": log_msg}




@auth.route('/save_fingerprint', methods=['POST'])
def save_fingerprint():
    entered_code = request.form.get('wert', '').strip()
    fingerprint = request.form.get('fingerprint', '').strip()
    client_ip = request.form.get('client_ip', '').strip()
    housenumber = request.form.get('housenumber', '').strip()

    
    if not entered_code or not fingerprint:
        flash("Fehlender Code oder Fingerprint.", "error")
        return redirect(url_for('views.home'))

    access_code = AccessCode.query.filter_by(code=entered_code, housenumber=housenumber).first()

    if not access_code:
        flash("Ungültiger Access-Code.", "error")
        return redirect(url_for('views.home'))

    if access_code.duration and access_code.duration < datetime.utcnow():
        flash("Access-Code ist abgelaufen.", "error")
        return redirect(url_for('views.home'))

    owner = access_code.user

    code_approval = CodeApproval.query.filter_by(
        access_code_id=access_code.id,
        fingerprint=fingerprint
    ).first()

   
    if code_approval and code_approval.approved:

        result = toggle_door_for_user(owner)

        if result["status"] == "error":
            flash(result["message"], "error")
        else:
            flash(f"Door {result['message']}", "success")

            db.session.add(Logs(
                nachrichten="Opened the door",
                author=f"access code '{entered_code}' '{client_ip}'",
                user_id=owner.id,
                account=owner.account   # NICHT current_user!
            ))
            db.session.commit()
        return redirect(url_for('views.home'))

   
    existing_request = AccessRequest.query.filter_by(
        user_id=owner.id,
        code_approval_id=code_approval.id if code_approval else None
    ).first()

    if existing_request:
        flash("Es wurde bereits eine Zugriffsanfrage gestellt. Bitte warten.", "info")
        return redirect(url_for('views.home'))

   
    if not code_approval:
        mail_handler.send_email(
            recipient=owner.email,
            reason="Anfrage zur Benutzung eines Access Codes",
            userfirstname=owner.firstname,
            extra_info=f"""
            Code <strong>{entered_code}</strong> wurde von der IP <strong>{client_ip}</strong> versucht zu verwenden.<br>
            Bitte überprüfen Sie die Anfrage in Ihrem Account.
            """
        )

        code_approval = CodeApproval(
            access_code_id=access_code.id,
            fingerprint=fingerprint,
            ip=client_ip,
            approved=False
        )
        db.session.add(code_approval)
        db.session.commit()

    access_request = AccessRequest(
        user_id=owner.id,
        code_approval_id=code_approval.id,
        request=f"IP <strong>{client_ip}</strong> möchte den Access-Code <strong>{entered_code}</strong> verwenden:"
    )
    db.session.add(access_request)
    db.session.commit()

    flash(
        "Zugriffsanfrage wurde gesendet. Bitte warten Sie auf die Genehmigung.",
        "info"
    )
    return redirect(url_for('views.home'))



@verify_required
@login_required
@auth.route('/check_access_codes_zugriffsrecht', methods=['GET'])
def check_access_codes_zugriffsrecht():

    if current_user.role not in ["Owner", "Admin"]:
        return "Nicht berechtigt", 403

    access_codes = AccessCode.query.filter_by(user_id=current_user.id).all()

    ips = []
    for code in access_codes:
        approvals = CodeApproval.query.filter_by(access_code_id=code.id).all()
        for approval in approvals:
            ips.append({
                "approval_id": approval.id,   
                "access_code": code.code,
                "ip": approval.ip,
                "approved": approval.approved
            })

    return render_template(
        "check_access_code.html",
        user=current_user,
        ips=ips
    )



@auth.route('/revoke_access', methods=['POST'])
@login_required
def revoke_access():

    revoke_ids = request.form.getlist('revoke_ids')

    if not revoke_ids:
        flash("Keine Zugriffe ausgewählt.", "info")
        return redirect(url_for('auth.check_access_codes_zugriffsrecht'))

    approvals = CodeApproval.query.filter(
        CodeApproval.id.in_(revoke_ids)
    ).all()

    for approval in approvals:
        db.session.delete(approval)

    db.session.commit()

    flash(f"{len(approvals)} Zugriffe wurden gelöscht.", "success")
    return redirect(url_for('auth.check_access_codes_zugriffsrecht'))


@login_required
@verify_required
@auth.route("/account-settings", methods=["POST"])
def account_settings():

    user = User.query.filter_by(id=current_user.id).first()

    if request.form.get("username"):
        user.username = request.form.get("username")

    if request.form.get("email"):
        user.email = request.form.get("email")

    if request.form.get("password"):
        user.set_password(request.form.get("password"))

    if request.form.get("onetime"):
        user.onetime = request.form.get("onetime")
        user.ip = None  

    if request.form.get("firstname"):
        user.firstname = request.form.get("firstname")

    if request.form.get("name"):
        user.name = request.form.get("name")

    db.session.commit()

    flash("Kontoeinstellungen erfolgreich aktualisiert!", "success")
    return redirect(url_for("views.home"))



@auth.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    pass

@auth.route("/reset_password", methods=["GET"])
def reset_password():
    return render_template("passwort_reset.html", user=current_user)


@auth.route("/reset_password/send_code", methods=["POST"])
def reset_password_send_code():
    data = request.get_json()
    email = data.get("email")
    user = User.query.filter_by(email=email).first()

    if user:
        code = ''.join(random.choices('0123456789', k=6))
        session["anfrage_code"] = code
        mail_handler.send_email(
            recipient=user.email,
            reason="Email Anfragecode",
            userfirstname=user.firstname,
            extra_info=code
        )
        return jsonify({"success": True, "message": "Code gesendet"}), 200
    else:
        return jsonify({"success": False, "message": "Email not found"}), 404

@auth.route("/reset_password/commit", methods=["POST"])
def reset_password_post():
    data = request.get_json()
    email = data.get("email")
    twoFaCode = data.get("twoFaCode")
    newPassword = data.get("newPassword")
    confirmPassword = data.get("confirmPassword")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "Email not found"}), 404

    if twoFaCode != session.get("anfrage_code"):
        return jsonify({"success": False, "message": "Invalid code"}), 400

    if newPassword != confirmPassword:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    user.password = generate_password_hash(newPassword, method='pbkdf2:sha256')
    db.session.commit()
    mail_handler.send_email(
        recipient=user.email,
        reason="Ihr Passwort wurde geändert",
        userfirstname=user.firstname
    )
    session.pop("anfrage_code", None)
    return jsonify({"success": True, "message": "Password wurde erfolgreich geändert!"}), 200


@auth.route("/tour-abgeschlossen", methods=["POST"])
def tour_abgeschlossen():
    user = User.query.filter_by(id=current_user.id).first()
    if user.show_tour == False:
        user.show_tour = True
    else:
        user.show_tour = False
    
    db.session.commit()
    return jsonify({"success": True, "message": "Tour abgeschlossen"}), 200
    

@auth.route("/delete_logs", methods=["POST"])
def delete_logs():
    user = User.query.filter_by(id=current_user.id).first()
    Logs.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({"success": True, "message": "Tour abgeschlossen"}), 200
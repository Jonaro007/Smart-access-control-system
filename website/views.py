import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta


from flask import Blueprint, render_template, redirect, request, jsonify, flash, url_for, Response
from .models import Logs, User, Device, AccessCode, CodeApproval, AccessRequest
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import string, random, secrets
from sqlalchemy import func

views = Blueprint("views", __name__)
from flask_login import login_user, login_required, logout_user, current_user

from .decorator import verify_required  

@views.route('/')
def home():
    return render_template("home.html", user=current_user)


@views.route('/account/<session_id>', methods=['POST', 'GET'])
@verify_required
@login_required
def account(session_id):
    if current_user.account != session_id:
        return "Zugriff verweigert", 403
    
    if not current_user.email:
        flash('Bitte richte deine E-Mail-Adresse ein', category='error')
    
    if request.method == 'POST':
        form_name = request.form.get('form_name')
        
        if form_name == 'onetime_form':
            onetimecode = request.form.get("onetimecode")

            if not onetimecode or len(onetimecode) != 8:
                flash('Dein Code muss 8 Zeichen lang sein.', category='error')
                return redirect(request.url)

            device = Device.query.filter_by(onetime=onetimecode).first()
            user = User.query.get(current_user.id)
            user.onetime = onetimecode

            if device:
                user.ip = device.ip
                flash('Account erfolgreich mit deinem Smart Lock verknüpft.', category='success')
            else:
                flash('Code gespeichert', category='success')
                flash('Stelle sicher, dass dein Smart Lock mit dem Internet verbunden ist.', category='info')

            db.session.commit()
            return redirect(request.url)
        elif form_name == 'modal_form':
            pass

    logs = Logs.query.filter_by(account=current_user.account).order_by(Logs.date.desc()).all()

    access_requests = AccessRequest.query.filter_by(user_id=current_user.id).all()
    last_access_code = Logs.query.filter(
    Logs.account == current_user.account,
    Logs.author.startswith("access code")
).order_by(Logs.date.desc()).first()

    anzahl_access_codes = AccessCode.query.filter_by(account=current_user.account).count()


    return render_template(
    "dashboard.html",
    user=current_user,
    logs=logs,
    access_requests=access_requests,
    last_access_code=last_access_code,
    anzahl_access_codes=anzahl_access_codes,
)


   
@views.route('/account/users/<session>', methods=['POST', 'GET'])
@login_required
def users(session):
    user = User.query.filter_by(id=current_user.id).first()
    if current_user.account != session:
        return "Zugriff verweigert", 403
    if current_user.role not in ["Owner", "Admin"]:
        return "Nicht berechtigt", 403

    if request.method == "POST":
        form_name = request.form.get("form_name")
        
        # Benutzer löschen
        if form_name == "delete_user":
            delete_id = request.form.get("delete_code")
            user_to_delete = User.query.filter_by(id=delete_id, account=current_user.account).first()
            if user_to_delete:
                db.session.delete(user_to_delete)
                db.session.commit()
                flash('User gelöscht', category='success')
            else:
                flash('User nicht gefunden oder nicht deiner.', category='error')
            return redirect(request.url)

        # Benutzer erstellen
        elif form_name == "create_user":
            password = request.form.get("password", "")
            if len(password) < 7:
                flash('Passwort muss mindestens 7 Zeichen lang sein', category='error')
                return redirect(request.url)
            
            number = random.randint(100, 999)
            if not user.onetime:
                flash("Bitte verknüpfe deinen Smart Lock mit unserem System, bevor du einen User hinzufügst", category="error")
                return redirect(request.url)

            new_user = User(
                username=f"user{number}@{user.firstname.lower()}",
                firstname=f"USER{number}",
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                role="User",
                onetime=user.onetime,
                ip=user.ip,
                name="USER",
                account=user.account,
                door=user.door
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Konto erfolgreich erstellt!', category='success')
            return redirect(request.url)

    # GET-Request oder nach POST-Redirect
    access_useres = User.query.filter_by(account=current_user.account).all()
    logs = Logs.query.filter_by(account=current_user.account).order_by(Logs.date.desc()).all()

    return render_template(
        "users.html",
        user=current_user,
        account=user,
        access_useres=access_useres,
        logs=logs
    )




@views.route('/account/access_codes/<session>', methods=['POST', 'GET'])
@verify_required
@login_required
def access_codes(session):
    if current_user.account != session:
        return "Zugriff verweigert", 403
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            code = request.form.get("code")
            housenumber = request.form.get("housenumber")
            desc = request.form.get("description")
            duration = request.form.get("duration")
            expires_at = request.form.get("expires_at") or None

            if expires_at:
                expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                expires = expires.replace(second=0, microsecond=0)
            else:
                expires = None

            new_code = AccessCode(
                code=code,
                housenumber=housenumber,
                description=desc,
                duration=expires,
                user_id=current_user.id,
                account=current_user.account
            )
            db.session.add(new_code)
            db.session.commit()
            return redirect(request.url)
        
        elif action == "delete":
            delete_id = request.form.get("delete_code")
            code_to_delete = AccessCode.query.filter_by(id=delete_id, user_id=current_user.id).first()
            if code_to_delete:
                db.session.delete(code_to_delete)
                db.session.commit()
            else:
                flash("Code nicht gefunden oder nicht deiner.", "error")
            return redirect(request.url)

    # Liste aller Codes des Users abrufen
    accessCode = AccessCode.query.filter_by(account=current_user.account).all()
    return render_template("access_codes.html", user=current_user, access_codes=accessCode, date=datetime.utcnow())



@views.route("/api/logs", methods=["GET"])
@login_required
def get_logs():
    logs = Logs.query.filter_by(user_id=current_user.id).order_by(Logs.date.desc()).all()

    
    log_list = []  # Liste **außerhalb** der Schleife erstellen
    for log in logs:
        log_list.append({
            "date": log.date.isoformat(),
            "author": log.author,
            "nachrichten": log.nachrichten
        })

    print("[DEBUG] Retrieved logs:")
    print(log_list)
    return jsonify(log_list)


@views.route('/handle_request', methods=['POST'])
@login_required
def handle_request():
    if current_user.role != "Owner":
        return "Nicht berechtigt", 403
    data = request.json
    request_id = data.get('request_id')
    action = data.get('action')  

    if not request_id or not action:
        return jsonify({"status": "error", "message": "Missing request ID or action"}), 400

    access_request = AccessRequest.query.get(request_id)  
    if not access_request:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    if action == 'approve':
        if access_request.code_approval:  
            code_approval = access_request.code_approval
            code_approval.approved = True
            code_approval.approver_user_id = current_user.id
            db.session.commit()

        # AccessRequest löschen
        db.session.delete(access_request)
        db.session.commit()
        flash(f"Anfrage {request_id} genehmigt", "success")
        return jsonify({"status": "success", "message": f"Request {request_id} approved"})
        

    elif action == 'deny':
        if access_request.code_approval:
            db.session.delete(access_request.code_approval)
        db.session.delete(access_request)
        db.session.commit()

        flash(f"Anfrage {request_id} abgelehnt", "success")
        return jsonify({"status": "success", "message": f"Request {request_id} denied"})
    

    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400



@views.route('/set_role', methods=['POST'])
@login_required
def set_role():
    if current_user.role not in ["Owner", "Admin"]:
        return "Nicht berechtigt", 403
    data = request.json
    username = data.get('username')
    role = data.get('action')  



    if not username or not role:
        return jsonify({"status": "error", "message": "Missing username or role"}), 400
    
    user = User.query.filter_by(username=username).first()
    if user.role == "Owner":
        return "Nicht berechtigt", 403
    user.role = role
    db.session.commit()

    return jsonify({"status": "success", "message": f"{username} auf {role} gesetzt"})

@views.route('/logs_plot.png')
@login_required
def logs_plot():

    data = (
        db.session.query(Logs.author, func.count(Logs.id))
        .filter(Logs.account == current_user.account)
        .group_by(Logs.author)
        .all()
    )

    authors = [row[0] for row in data]
    counts = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(authors, counts, color='skyblue')
    ax.set_title("Log-Einträge pro Benutzer")
    ax.set_xlabel("Benutzer")
    ax.set_ylabel("Anzahl Logs")
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    output = io.BytesIO()
    plt.savefig(output, format='png', bbox_inches='tight')
    plt.close(fig)
    output.seek(0)

    return Response(output.getvalue(), mimetype='image/png')



@views.route('/account/logs/<session>', methods=['GET'])
@verify_required
@login_required
def account_logs(session):
    if current_user.account != session:
        return "Zugriff verweigert", 403
    
    logs = Logs.query.filter_by(account=current_user.account).order_by(Logs.date.desc()).all()
    return render_template("logs.html", user=current_user, logs=logs)



@views.route('/anleitung', methods=['GET'])
def anleitung():
    return render_template("anleitung.html", user=current_user)

@views.route('/produkt', methods=['GET'])
def produkt():
    return render_template("produkt.html", user=current_user)

@views.route('/shortcut', methods=['GET'])
def shortcut():
    return render_template("shortcut.html", user=current_user)
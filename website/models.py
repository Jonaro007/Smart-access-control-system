from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(150), nullable=False)
    firstname = db.Column(db.String(150))
    name = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=False ,nullable=False)
    onetime = db.Column(db.String(64), unique=False)
    ip = db.Column(db.String(64))
    account = db.Column(db.String(64), nullable=False)
    door = db.Column(db.String(256), unique=False, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(20), default="Owner")
    google_verify = db.Column(db.String(64), unique=True, nullable=True)
    show_tour = db.Column(db.Boolean, default=False, nullable=False)

    # Beziehungen
    logs = db.relationship('Logs', back_populates='user')
    access_codes = db.relationship('AccessCode', back_populates='user')


class Logs(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    nachrichten = db.Column(db.String(15000))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    author = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    account = db.Column(db.String(64), nullable=False) 

    # Beziehung zurück zum User
    user = db.relationship('User', back_populates='logs')



class AccessCode(db.Model):
    __tablename__ = "access_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15000))
    duration = db.Column(db.DateTime, nullable=True)  
    description = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='access_codes')
    account = db.Column(db.String(64), nullable=False) 
    housenumber = db.Column(db.String(64), nullable=False)



class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    onetime = db.Column(db.String(64), unique=True, nullable=False)
    ip = db.Column(db.String(64))



class CodeApproval(db.Model):
    __tablename__ = "code_approvals"

    id = db.Column(db.Integer, primary_key=True)
    access_code_id = db.Column(db.Integer, db.ForeignKey('access_codes.id'), nullable=False)
    fingerprint = db.Column(db.String(256), nullable=False)
    ip = db.Column(db.String(64))
    approved = db.Column(db.Boolean, default=False, nullable=False)
    approver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    access_code = db.relationship('AccessCode', backref=db.backref('approvals', cascade="all, delete-orphan"))
    approver_user = db.relationship('User', foreign_keys=[approver_user_id])


class AccessRequest(db.Model):
    __tablename__ = "access_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    code_approval_id = db.Column(db.Integer, db.ForeignKey('code_approvals.id'), nullable=True)
    request = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('access_requests', cascade="all, delete-orphan"))
    code_approval = db.relationship('CodeApproval', foreign_keys=[code_approval_id], backref=db.backref('access_request', uselist=False))


# Smart Access Control System

Ein intelligentes Zutrittskontrollsystem mit ESP32-basierter Türsteuerung, Web-Dashboard, Benutzerverwaltung und mehrstufigem Sicherheitskonzept.

Dieses Projekt wurde im Rahmen einer schulischen Projektarbeit entwickelt und verbindet Webentwicklung, Embedded Systems und IT-Sicherheit zu einer praxisnahen IoT-Anwendung.

> Hinweis: Es handelt sich um einen funktionsfähigen Prototypen. Einzelne Komponenten wurden bewusst vereinfacht umgesetzt, um den Fokus auf Architektur, Integration und Sicherheitskonzepte zu legen.

---

## Funktionen

- Benutzerregistrierung und Login
- Rollenbasierte Benutzerverwaltung
- Administrativer Freigabeprozess für neue Benutzer
- Web-Dashboard zur Verwaltung
- E-Mail-Benachrichtigungen für Nutzeraktionen
- Zwei-Faktor-Authentifizierung (Google Authenticator)
- Steuerung eines physischen Türschlosses über ESP32
- Echtzeitkommunikation zwischen Server und Hardware
- Geräteverifizierung über Challenge-Response-Verfahren
- Passwort-Hashing zur sicheren Speicherung
- Protokollierung von Zugriffen

---

## Verwendete Technologien

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- WebSockets
- HTTP API

### Frontend
- HTML
- CSS
- JavaScript

### Embedded System
- ESP32
- 360° Servomotor

### Sicherheit
- SHA-256 Hashing
- TOTP (Google Authenticator)
- AES-basierte Challenge-Response-Authentifizierung

---

## Systemarchitektur

Das System besteht aus drei Hauptkomponenten:

### Webanwendung
Benutzeroberfläche zur Registrierung, Anmeldung und Verwaltung von Zugriffsrechten.

### Backend
Verarbeitung von Authentifizierung, Geschäftslogik, Datenbankzugriff und Kommunikation mit dem ESP32.

### Hardware (ESP32)
Steuert den physischen Schließmechanismus und empfängt autorisierte Befehle vom Server.

---

## Projektstruktur

```text
.
├── main.py
├── server.py
├── mail_handler.py
├── website/
│   ├── __init__.py
│   ├── auth.py
│   ├── verify.py
│   ├── views.py
│   ├── models.py
│   ├── decorators.py
│   ├── templates/
│   └── static/
└── requirements.txt

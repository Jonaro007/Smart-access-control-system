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

###Installation
1. Repository klonen
   
`git clone <repository-url>`

`cd smart-access-control-system`

2. Abhängigkeiten installieren

`pip install -r requirements.txt`

3. Umgebung konfigurieren

**Erstelle eine .env Datei im Root-Verzeichnis:**
```
SECRET_KEY=your_secret_key

MAIL=your_email@gmail.com
PSW=your_app_password
```
Starten des Projekts
`python main.py`

Der Server startet automatisch und stellt die Verbindung zum ESP32-System her.

---

### Hardware
Für den Nachbau werden mindestens folgende Komponenten benötigt:

- ESP32 Mikrocontroller
- 360° Servomotor
- Stromversorgung


### Das System implementiert mehrere Sicherheitsmechanismen:

- Passwort-Hashing (SHA-256)
- Zwei-Faktor-Authentifizierung (TOTP)
- Geräteauthentifizierung mittels Challenge-Response (AES)
- Rollenbasierte Zugriffskontrolle
### Bekannte Einschränkungen

Dieses Projekt wurde als schulische Arbeit entwickelt. Für produktive Nutzung wären zusätzliche Maßnahmen erforderlich, insbesondere in den Bereichen Skalierbarkeit, Härtung der Sicherheitsarchitektur und Fehlerbehandlung.

### Dokumentation

Eine ausführliche technische Dokumentation befindet sich im Repository bzw. im Ordner docs/.

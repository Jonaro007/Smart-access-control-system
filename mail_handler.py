
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()


def create_mail_app(app):
    global mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
    app.config['MAIL_PASSWORD'] = os.getenv('PSW')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL')

    mail = Mail(app)

def send_email(recipient, reason=None, extra_info="", userfirstname=""):
  
    html_templates = {

    "Login erkannt": f"""
    <!DOCTYPE html>
    <html lang="de">
    <body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center">
            <table width="600" style="background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,0.08);">
              
              <tr>
                <td style="background:#0d6efd;padding:30px;color:#ffffff;text-align:center;">
                  <h1 style="margin:0;font-size:26px;">Anmeldung erkannt</h1>
                </td>
              </tr>

              <tr>
                <td style="padding:30px;color:#333;">
                  <p style="font-size:16px;">Hallo {userfirstname},</p>

                  <p style="font-size:16px;">
                    wir haben eine erfolgreiche Anmeldung bei Ihrem Konto festgestellt.
                  </p>

                  {f"<p style='font-size:14px;color:#555;'>{extra_info}</p>" if extra_info else ""}

                  <p style="font-size:16px;">
                    Falls Sie diese Anmeldung <strong>nicht selbst durchgeführt</strong> haben,
                    empfehlen wir Ihnen dringend, Ihr Konto sofort abzusichern.
                  </p>

                  <div style="text-align:center;margin:30px 0;">
                    <a href="https://your-website.com/security"
                       style="background:#0d6efd;color:#ffffff;padding:14px 28px;
                              text-decoration:none;border-radius:6px;font-weight:bold;">
                      Sicherheit überprüfen
                    </a>
                  </div>

                  <p style="font-size:14px;color:#777;">
                    Diese E-Mail wurde automatisch aus Sicherheitsgründen versendet.
                  </p>
                </td>
              </tr>

              <tr>
                <td style="background:#f1f3f5;padding:20px;text-align:center;font-size:12px;color:#999;">
                  © 2026 SmartLock Inc ·
                  <a href="https://your-website.com" style="color:#0d6efd;text-decoration:none;">Website</a>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """,

    "Versuchter Zugriff auf ihr Konto": f"""
    <!DOCTYPE html>
    <html lang="de">
    <body style="margin:0;padding:0;background-color:#fff3f3;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%">
        <tr>
          <td align="center">
            <table width="600" style="background:#ffffff;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,0.1);">

              <tr>
                <td style="background:#dc3545;padding:30px;color:#ffffff;text-align:center;">
                  <h1 style="margin:0;">Sicherheitswarnung</h1>
                </td>
              </tr>

              <tr>
                <td style="padding:30px;color:#333;">
                  <p style="font-size:16px;">Hallo {userfirstname},</p>

                  <p style="font-size:16px;">
                    es wurde ein <strong>unbefugter Zugriffsversuch</strong> auf Ihr Konto festgestellt.
                  </p>

                  <p style="font-size:16px;">
                    Bitte überprüfen Sie Ihre Kontoaktivitäten und ändern Sie falls nötig Ihr Passwort.
                  </p>

                  <div style="text-align:center;margin:30px 0;">
                    <a href="https://your-website.com/reset-password"
                       style="background:#dc3545;color:#ffffff;padding:14px 28px;
                              text-decoration:none;border-radius:6px;font-weight:bold;">
                      Konto absichern
                    </a>
                  </div>
                </td>
              </tr>

              <tr>
                <td style="background:#f8f9fa;padding:20px;text-align:center;font-size:12px;color:#999;">
                  SmartLock Sicherheitsteam
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """,

    "Ihr Passwort wurde geändert": f"""
    <!DOCTYPE html>
    <html lang="de">
    <body style="margin:0;padding:0;background-color:#eef2f7;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%">
        <tr>
          <td align="center">
            <table width="600" style="background:#ffffff;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,0.08);">

              <tr>
                <td style="background:#17a2b8;padding:30px;color:#ffffff;text-align:center;">
                  <h1>Passwort geändert</h1>
                </td>
              </tr>

              <tr>
                <td style="padding:30px;color:#333;">
                  <p style="font-size:16px;">Hallo,</p>

                  <p style="font-size:16px;">
                    ihr Passwort wurde erfolgreich geändert.
                  </p>

                  <p style="font-size:14px;color:#777;">
                    Falls Sie diese nicht gestellt haben, wenden Sie sich umbedingt an den Support.
                  </p>

                  <div style="text-align:center;margin:30px 0;">
                    <a href="https://your-website.com/reset-password"
                       style="background:#0d6efd;color:#ffffff;padding:14px 28px;
                              text-decoration:none;border-radius:6px;font-weight:bold;">
                      Support kontaktieren
                    </a>
                  </div>

                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """,

    "Anfrage zur Benutzung eines Access Codes": f"""
    <!DOCTYPE html>
    <html lang="de">
    <body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%">
        <tr>
          <td align="center">
            <table width="600" style="background:#ffffff;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,0.08);">

              <tr>
                <td style="background:#17a2b8;padding:30px;color:#ffffff;text-align:center;">
                  <h1>Zugangscode</h1>
                </td>
              </tr>

              <tr>
                <td style="padding:30px;color:#333;">
                  <p style="font-size:16px;">Hallo, {userfirstname}</p>

                  <p style="font-size:16px;">
                    Einer ihrer Access-Codes wurde soeben versucht zu verwenden.
                  </p>

                  {f"<p style='font-size:20px;font-weight:bold;text-align:center;letter-spacing:2px;'>{extra_info}</p>" if extra_info else ""}

                  <div style="text-align:center;margin:30px 0;">
                    <a href="https://your-website.com/security"
                       style="background:#0d6efd;color:#ffffff;padding:14px 28px;
                              text-decoration:none;border-radius:6px;font-weight:bold;">
                        Konto überprüfen
                    </a>
                  </div>

                </td>
              </tr>
                </td>
              </tr>

              <tr>
                <td style="background:#f1f3f5;padding:20px;text-align:center;font-size:12px;color:#999;">
                  © 2026 SmartLock Inc ·
                  <a href="https://your-website.com" style="color:#0d6efd;text-decoration:none;">Website</a>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """,
    f"Email Anfragecode": f"""
    <!DOCTYPE html>
    <html lang="de">
    <body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center">
            <table width="600" style="background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,0.08);">
              
              <tr>
                <td style="background:#0d6efd;padding:30px;color:#ffffff;text-align:center;">
                  <h1 style="margin:0;font-size:26px;">Anfragecode</h1>
                </td>
              </tr>

              <tr>
                <td style="padding:30px;color:#333;">
                  <p style="font-size:16px;">Hallo {userfirstname},</p>

                  <p style="font-size:16px;">
                    hier ist Ihr Zugangscode für ihr Konto:
                  </p>

                  {f"<strong><p style='font-size:20px;color:#555;'>{extra_info}</p></strong>" if extra_info else "<strong>an error has occurred</strong>"}

                  <p style="font-size:16px; margin-top:30px;">
                    Falls Sie diese Anfrage <strong>nicht von Ihnen kommt</strong>,
                    ändern sie dringends Ihr Passwort, um unbefugten Zugriff zu verhindern.
                  </p>

                  <div style="text-align:center;margin:30px 0;">
                    <a href="https://your-website.com/security"
                       style="background:#0d6efd;color:#ffffff;padding:14px 28px;
                              text-decoration:none;border-radius:6px;font-weight:bold;">
                      Konto verwalten
                    </a>
                  </div>

                  <p style="font-size:14px;color:#777;">
                    Diese E-Mail wurde automatisch versendet.
                  </p>
                </td>
              </tr>

              <tr>
                <td style="background:#f1f3f5;padding:20px;text-align:center;font-size:12px;color:#999;">
                  © 2026 SmartLock Inc ·
                  <a href="https://your-website.com" style="color:#0d6efd;text-decoration:none;">Website</a>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
}



    if reason not in html_templates:
        raise ValueError(f"Unknown reason: {reason}")

    msg = Message(
        subject=reason,
        recipients=[recipient],
        html=html_templates[reason]
    )
    mail.send(msg)
    print(f"Sent {reason} email to {recipient}")
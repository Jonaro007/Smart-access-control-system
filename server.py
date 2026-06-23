import random
import socket
import string
import threading
import requests
import json
import time
from Crypto.Cipher import AES





FLASK_URL = "http://127.0.0.1:5000/esp32/connect"
HOST = "0.0.0.0"
PORT = 8081
HEARTBEAT_INTERVAL = 8  

key = b"1234567890abcdef"

# Aktive Clients
# { ip: { "conn": socket, "last_seen": timestamp } }
clients = {}

#
#  Formiert für die AES auf 16-Byte-Blöcke
def pad(data):
    while len(data) % 16 != 0:
        data += b" "
    return data

def sicherheitssystem(conn):
    # code senden
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    conn.sendall(pad(code.encode())) 
    print("[Sicherheit] Starte authentifizierung")
    # verschlüsselte antwort empfangen
    data = conn.recv(1024)
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(data)

        antwort = decrypted.decode().strip()
    except Exception as e:
        return False
    return antwort == code


def send_to_client(ip, message):
    if ip not in clients:
        print(f"[SOCKET] Client {ip} nicht online")
        return False

    try:
        conn = clients[ip]["conn"]
        conn.sendall(message.encode() + b"\n")
        print(f"[SOCKET] Gesendet an {ip}: {message}")
        return True
    except Exception as e:
        print(f"[SOCKET-FEHLER] {ip}: {e}")
        return False



def send_to_flask(data):
    try:
        r = requests.post(FLASK_URL, json=data)
        print(f"[Sicherheit] Authentifizierung erolgreich")
        print(f"[FLASK] {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[FLASK-FEHLER] {e}")


def register_client(ip, conn):
    clients[ip] = {
        "conn": conn,
        "last_seen": time.time()
    }


def remove_client(ip):
    if ip in clients:
        try:
            clients[ip]["conn"].close()
        except:
            pass
        del clients[ip]
        print(f"[CLIENT] {ip} entfernt")


def check_if_online(ip):
    return ip in clients

def client_is_offline(ip):
    return time.time() - clients[ip]["last_seen"] > HEARTBEAT_INTERVAL




def handle_client(conn, addr):
    ip = addr[0]
    print(f"[VERBUNDEN] {ip}")

    try:

        if not sicherheitssystem(conn):
            print(f"[SICHERHEIT] Authentifizierung fehlgeschlagen für {ip}")
            conn.close()
            return

        raw = conn.recv(1024).decode().strip()
        if not raw:
            return

        data = json.loads(raw)
        data["ip"] = ip

        send_to_flask(data)
        register_client(ip, conn)

        conn.sendall(b"OK\n")


        while True:
            conn.settimeout(0.2)

            try:
                msg = conn.recv(1024)

                if not msg:
                    print(f"[TRENNUNG] {ip}")
                    break

                text = msg.decode().strip()
                clients[ip]["last_seen"] = time.time()

                if text == "ping":
                    
                    clients[ip]["last_seen"] = time.time()
                    continue


                print(f"[{ip}] {text}")

                if text == "unlock":
                    print(f"[AKTION] Tueroeffnen")
                elif text == "lock":
                    print(f"[AKTION] Tuerschliessen")

            except socket.timeout:
                if client_is_offline(ip):
                    print(f"[OFFLINE] {ip}")
                    break

    except Exception as e:
        print(f"[FEHLER] {ip}: {e}")

    finally:
        remove_client(ip)




def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[SERVER] Laeuft auf Port {PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()




from website import create_app
import threading
import server
import os
from server import start_server

app = create_app()

if __name__ == '__main__':
    # Prüfen, ob wir im Hauptprozess des Flask-Reloaders sind
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        socket_thread = threading.Thread(target=start_server, daemon=True)
        socket_thread.start()
        print("[INFO] Socket-Server-Thread gestartet.")

    # Flask starten
    app.run(host="0.0.0.0", port=5000, debug=False)

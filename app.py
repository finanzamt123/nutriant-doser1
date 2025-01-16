from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import sqlite3
import os

# Flask-Anwendung initialisieren
app = Flask(__name__)

# GPIO-Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Beispiel-Pin-Setup (anpassen an Schaltplan)
SENSOR_PINS = {
    "ph": 17,
    "ec": 27,
    "temperature": 4,
    "water_level": 22,
    "relay1": 23,
    "relay2": 24,
    "relay3": 25
}

for pin in SENSOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# Datenbankpfad
DB_PATH = os.path.join(os.getcwd(), "data", "sensor_data.db")

# Sicherstellen, dass das Datenverzeichnis existiert
if not os.path.exists("data"):
    os.makedirs("data")

# Datenbank initialisieren
if not os.path.exists(DB_PATH):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ph REAL,
            ec REAL,
            temperature REAL,
            water_level TEXT
        )
        """)
        conn.commit()

# Routen der Webanwendung
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sensors", methods=["GET"])
def get_sensor_data():
    # Beispiel-Datenabruf (Dummy-Daten)
    data = {
        "ph": 7.2,
        "ec": 1.5,
        "temperature": 22.5,
        "water_level": "Normal"
    }
    return jsonify(data)

@app.route("/api/relays", methods=["POST"])
def control_relays():
    relay = request.json.get("relay")
    state = request.json.get("state")

    if relay in SENSOR_PINS and state in ["on", "off"]:
        GPIO.output(SENSOR_PINS[relay], GPIO.HIGH if state == "on" else GPIO.LOW)
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "error", "message": "Invalid request"}), 400

@app.route("/api/download", methods=["GET"])
def download_data():
    # Daten aus der Datenbank abrufen
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_data")
        rows = cursor.fetchall()

    # CSV-Datei erstellen
    csv_data = "id,timestamp,ph,ec,temperature,water_level\n"
    for row in rows:
        csv_data += ",".join(map(str, row)) + "\n"

    # CSV-Daten als Antwort zurückgeben
    return (csv_data, 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=sensor_data.csv"
    })

# Startpunkt der Anwendung
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

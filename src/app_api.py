from flask import Flask, request, jsonify
import serial

app = Flask(__name__)

# Schnittstellenkonfiguration
port = "/dev/ttyS0"
baudrate = 9600
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
timeout = 1

# Globale Variable
last_received_message = "status"

commands_map = {
    "lamp1_on": "set=1,on",
    "lamp2_on": "set=2,on",
    "lamp3_on": "set=3,on",
    "lamp1_blink": "set=1,blink",
    "lamp2_blink": "set=2,blink",
    "lamp3_blink": "set=3,blink",
    "lamp1_flash": "set=1,flash",
    "lamp2_flash": "set=2,flash",
    "lamp3_flash": "set=3,flash",
    "lamp1_off": "set=1,off",
    "lamp2_off": "set=2,off",
    "lamp3_off": "set=3,off",
    "all_on": "set_all=1,1,1,",
    "all_blink": "set_all=2,2,2,",
    "all_flash": "set_all=3,3,3,",
    "all_off": "set_all=0,0,0,",
    "status": "status",
    "reset": "reset",
    "version": "version"
}



# Route für das Senden von Befehlen
@app.route('/send_command', methods=['POST'])
def send_command_route():
    command = request.json.get('command')
    print(command)
    if not command:
        return jsonify({"error": "Kein Befehl angegeben"}), 400

    last_received_message = commands_map.get(command)
    print(last_received_message)
    if not last_received_message:
        return jsonify({"error": "Ungültiger Befehl"}), 400

    try:
        # Nachricht an serielle Schnitslle
        full_cmd = last_received_message + "\r\n"
        ser.write(full_cmd.encode())
        print(f"Befehl '{last_received_message}' gesendet.")

        # Antwort
        response = ser.readline().decode().strip()

        if response:
            print(f"Erhaltene Antwort: {response}")
            answer = last_received_message + "= " + response
            print(f"Die Rückgabe ist: {answer}")
        else:
            print("Keine Antwort erhalten")
            answer = last_received_message + ": Keine Antwort erhalten"

    except serial.SerialException as e:
        return jsonify({"error": f"Fehler bei der Kommunikation mit der seriellen Schnittstelle: {str(e)}"}), 500

    return jsonify(answer)

# Serielle Schnittstelle initialisieren
try:
    ser = serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
    if not ser.isOpen():
        print("Konnte keine Verbindung öffnen.")
        exit()
    else:
        print("Verbindung erfolgreich geöffnet.")
except serial.SerialException as e:
    print(f"Fehler beim Öffnen der seriellen Schnittstelle: {str(e)}")
    exit()


if __name__ == '__main__':
    app.run(host='192.168.1.22', port=5000, debug=True)

from flask import Flask, request
import paho.mqtt.client as mqtt
import json, serial, time

app = Flask(__name__)

# Schnittstellenkonfiguration for rs232
port = "/dev/ttyS0"
baudrate = 9600
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
timeout = 1

# Globale Variablen
last_received_message = "status"
ser = None

# MQTT-Client initialisieren
client = mqtt.Client()



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

# Verbindung zu mqtt
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Verbunden mit MQTT Broker, Result code:", str(rc))
        client.subscribe("topic/lampe", qos=1)
    else:
        print("Verbindung fehlgeschlagen, Result code:", str(rc))

def on_disconnect(client, userdata, rc):
    print("Verbindung zum MQTT Broker getrennt")



def on_message(client, userdata, msg):
    global last_received_message
    payload = msg.payload.decode('utf-8')
    print("Received payload:", payload)
    serial_command = commands_map.get(payload)
    if not serial_command:
        print("Invalid command")
        return

    last_received_message = serial_command
    print("Received message:", last_received_message)

    # Befehl an die serielle Schnittstelle senden
    try:
        full_cmd = last_received_message+"\r\n"
        ser.write(full_cmd.encode())
        print(f"Befehl '{last_received_message}' gesendet.")

        # Antwort
        response = ser.readline().decode().strip()
    except serial.SerialException as e:
        print(f"Fehler bei der Kommunikation mit der seriellen Schnittstelle: {e}")
        return

    if response:
        print(f"Erhaltene Antwort: {response}")
        answer = last_received_message + "= " + response
        # Antwort über MQTT senden
        print(f"Die Rückgabe ist: {answer}")
        client.publish("topic/lampe/recive", answer)
    else:
        print("Keine Antwort erhalten.")
        client.publish("topic/lampe/recive", "Keine Antwort erhalten")


def initialize_serial_connection():
    global ser
    try:
        ser = serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
        if not ser.isOpen():
            print("Konnte keine Verbindung öffnen.")
            exit()
        else:
            print("Verbindung zur seriellen Schnittstelle erfolgreich geöffnet.")
            return ser
    except serial.SerialException as e:
        print(f"Konnte keine Verbindung öffnen: {e}")
        exit()


def initialize_mqtt_client():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        client.connect("localhost", 1883, 60)
        print("Verbindung zum MQTT Broker erfolgreich hergestellt.")
        return client
    except Exception as e:
        print(f"Fehler bei der Verbindung mit dem MQTT Broker: {e}")
        exit()


def main():
    ser = initialize_serial_connection()
    client = initialize_mqtt_client()

    client.loop_start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        ser.close()


if __name__ == "__main__":
    main()

import json
from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt

# MQTT CONFIG
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USER = "mqttuser"
MQTT_PASSWORD = "mqttpassword"

app = Flask(__name__)
socketio = SocketIO(app)

topics = {}

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code:", rc)
    client.subscribe("#")  # subscribe to all topics


def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="ignore")

    try:
        parsed = json.loads(payload)
    except:
        parsed = payload

    topics[msg.topic] = parsed

    socketio.emit("mqtt_update", {
        "topic": msg.topic,
        "payload": parsed
    })


# MQTT CLIENT
mqtt_client = mqtt.Client()

# authentication
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
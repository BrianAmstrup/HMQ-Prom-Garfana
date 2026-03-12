import json
import time
from collections import defaultdict, deque
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USER = "mqttuser"
MQTT_PASS = "mqttpassword"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

history = defaultdict(lambda: deque(maxlen=30))
rates = defaultdict(lambda: deque(maxlen=50))


def build_tree():

    tree = {}

    for topic in history.keys():

        parts = topic.split("/")
        node = tree

        for p in parts:
            node = node.setdefault(p, {})

    return tree


def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    client.subscribe("#")


def on_message(client, userdata, msg):

    payload = msg.payload.decode(errors="ignore")

    try:
        parsed = json.loads(payload)
    except:
        parsed = payload

    topic = msg.topic

    history[topic].append(parsed)
    rates[topic].append(time.time())

    socketio.emit("mqtt_update", {
        "topic": topic,
        "history": list(history[topic]),
        "rate": len(rates[topic])
    })


@socketio.on("connect")
def client_connected():

    print("Web client connected")

    for topic in history:

        socketio.emit("mqtt_update", {
            "topic": topic,
            "history": list(history[topic]),
            "rate": len(rates[topic])
        })

    socketio.emit("topic_tree", build_tree())


@socketio.on("publish")
def publish_message(data):

    topic = data["topic"]
    payload = data["payload"]

    mqtt_client.publish(topic, payload)


mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
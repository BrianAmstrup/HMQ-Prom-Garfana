import os, json, time
from collections import defaultdict, deque
from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "superuser")
MQTT_PASS = os.getenv("MQTT_PASS", "admin")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # no async_mode

history = defaultdict(lambda: deque(maxlen=30))
rates = defaultdict(lambda: deque(maxlen=50))

def build_tree():
    tree = {}
    for topic in history.keys():
        node = tree
        for part in topic.split("/"):
            node = node.setdefault(part, {})
    return tree

def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    client.subscribe("#")  # subscribe to all topics

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="ignore")
    try:
        parsed = json.loads(payload)
    except:
        parsed = payload

    topic = msg.topic
    history[topic].append(parsed)
    rates[topic].append(time.time())

    # Emit to all connected clients (works reliably in this simple setup)
    socketio.emit("mqtt_update", {
        "topic": topic,
        "history": list(history[topic]),
        "rate": len(rates[topic])
    })

    socketio.emit("topic_tree", build_tree())

@socketio.on("connect")
def client_connected():
    for topic in history:
        socketio.emit("mqtt_update", {
            "topic": topic,
            "history": list(history[topic]),
            "rate": len(rates[topic])
        })
    socketio.emit("topic_tree", build_tree())

@socketio.on("publish")
def handle_publish(data):
    mqtt_client.publish(data["topic"], data["payload"])

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()  # non-blocking

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
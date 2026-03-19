import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

host = os.getenv("MQTT_HOST", "hivemq")
port = int(os.getenv("MQTT_PORT", "1883"))
topic = os.getenv("MQTT_TOPIC", "sensors/temperature")
interval = int(os.getenv("INTERVAL", "5"))
username = os.getenv("MQTT_USER", "sensor")
password = os.getenv("MQTT_PASSWORD", "password")
client_id = os.getenv("MQTT_HOST_CLIENTID", "Temp-simulator")

connected = False

# ----------------------------
# Callbacks
# ----------------------------
def on_connect(client, userdata, flags, reason_code, properties):
    global connected
    connected = True
    print("✅ Connected:", reason_code)

def on_disconnect(client, userdata, reason_code, properties):
    global connected
    connected = False
    print("❌ Disconnected:", reason_code)

# ----------------------------
# Client setup
# ----------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)

client.username_pw_set(username=username, password=password)
client.reconnect_delay_set(min_delay=1, max_delay=120)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# ----------------------------
# Initial connect retry loop
# ----------------------------
while True:
    try:
        print("Connecting...")
        client.connect(host, port, 60)
        break
    except Exception as e:
        print("Connect failed, retrying in 5s:", e)
        time.sleep(5)

client.loop_start()  # ✅ REQUIRED for auto-reconnect

print(f"Starting temperature publisher with ID {client_id} → {host}:{port}, topic='{topic}'")

# ----------------------------
# Publish loop
# ----------------------------
try:
    while True:
        if connected:
            message = {
                "temperature": round(random.uniform(2.0, 35.0), 2),
                "isotime": datetime.now(timezone.utc)
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z"),
                "SensorID": "TempSimulator",
                "unixtime": int(time.time() * 1000),
            }

            payload = json.dumps(message)

            result = client.publish(topic, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                # print("✅ Published")
                print(f"✅ Successfully published to '{topic}': {payload}")
            else:
                print("❌ Publish failed:", result.rc)
        else:
            print("⏳ Waiting for connection...")

        time.sleep(interval)

except KeyboardInterrupt:
    print("Stopping publisher...")
    client.loop_stop()
    client.disconnect()
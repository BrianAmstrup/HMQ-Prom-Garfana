import time
import random
import os
import paho.mqtt.client as mqtt
import sparkplug_b_pb2


GROUP_ID = "factory1"
EDGE_NODE_ID = "edge01"

TOPIC_NBIRTH = f"spBv1.0/{GROUP_ID}/NBIRTH/{EDGE_NODE_ID}"
TOPIC_NDATA = f"spBv1.0/{GROUP_ID}/NDATA/{EDGE_NODE_ID}"

host = os.getenv("MQTT_HOST", "hivemq")
port = int(os.getenv("MQTT_PORT", "1883"))
# topic = os.getenv("MQTT_TOPIC", "sensors/temperature")
interval = int(os.getenv("INTERVAL", "5"))
username = os.getenv("MQTT_USER", "SPsim")       # MQTT username
password = os.getenv("MQTT_PASSWORD", "password")   # MQTT password
client_id = "SP-b-simulator"



seq = 0


def create_metric(payload, name, datatype, value):
    metric = payload.metrics.add()
    metric.name = name
    metric.datatype = datatype

    if datatype == 9:  # Float
        metric.float_value = value
    elif datatype == 4:  # Int
        metric.int_value = value
    elif datatype == 12:  # String
        metric.string_value = value


def create_payload(metrics):
    global seq

    payload = sparkplug_b_pb2.Payload()
    payload.timestamp = int(time.time() * 1000)
    payload.seq = seq

    for m in metrics:
        create_metric(payload, *m)

    seq += 1
    return payload.SerializeToString()


def publish_nbirth(client):
    metrics = [
        ("temperature", 9, 0.0),
        ("pressure", 9, 0.0),
        ("status", 12, "INIT")
    ]

    payload = create_payload(metrics)

    client.publish(TOPIC_NBIRTH, payload, qos=1)
    print("NBIRTH published")


def publish_ndata(client):

    metrics = [
        ("temperature", 9, random.uniform(20, 30)),
        ("pressure", 9, random.uniform(1, 5)),
        ("status", 12, "RUNNING")
    ]

    payload = create_payload(metrics)

    client.publish(TOPIC_NDATA, payload, qos=0)
    print("NDATA published")


def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    publish_nbirth(client)


def main():

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
    # client.on_connect = on_connect
    client.username_pw_set(username=username, password=password)
    client.connect(host, port, 60)
    client.loop_start()

    publish_nbirth(client)

    while True:
        publish_ndata(client)
        time.sleep(interval)

if __name__ == "__main__":
    main()
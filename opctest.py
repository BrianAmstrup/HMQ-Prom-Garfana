from opcua import Client

client = Client("opc.tcp://127.0.0.1:4841/")
# client.set_security_string("None")
client.connect()

print("Connected!")
client.disconnect()
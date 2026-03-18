import zmq
import time
import json
import sys

MAIN_SERVER_IP   = "127.0.0.1"
MAIN_SERVER_PORT = "6000"

PUBLISHER_IP = "127.0.0.1"

SERVICE_MESSAGES = {
    "MOVIES":      ["MOVIES] Harry Potter", "[MOVIES] Interstellar", "[MOVIES] The Matrix"],
    "WEATHER":          ["[WEATHER] Foggy", "[WEATHER] Sunny 22°C", "[WEATHER] Rainy"],
    "HOUR":           [],   # Dynamically generated
    "PERSONAL_INFO":  ["[GITHUB] alsteve23", "[LOCATION] Edificio Senescyt - Urcuqui"],
}

#Arguments
if len(sys.argv) < 3:
    print("Usage: python publisher.py <SERVICE> <PORT_PUB>")
    print("Available Services:", list(SERVICE_MESSAGES.keys()) + ["HOUR"])
    sys.exit(1)
 
SERVICE_NAME = sys.argv[1].upper()
PUB_PORT     = sys.argv[2]
 
context = zmq.Context()


#Register a service in the main server
def register_service():
    req = context.socket(zmq.REQ)
    req.setsockopt(zmq.LINGER, 0)
    req.setsockopt(zmq.RCVTIMEO, 3000)
    req.connect(f"tcp://{MAIN_SERVER_IP}:{MAIN_SERVER_PORT}")
    msg = json.dumps({
        "action":  "REGISTER",
        "service": SERVICE_NAME,
        "ip":      PUBLISHER_IP,
        "port":    PUB_PORT
    })
    req.send_string(msg)
    try:
        reply = json.loads(req.recv_string())
        print(f"[PUBLISHER-{SERVICE_NAME}] Register: {reply['message']}")
    except zmq.error.Again:
        print(f"[PUBLISHER-{SERVICE_NAME}] Main server did not answer the register.")
    finally:
        req.close()
 
register_service()

#Created a socker to start publishing

pub = context.socket(zmq.PUB)
pub.bind(f"tcp://0.0.0.0:{PUB_PORT}")
print(f"[PUBLISHER-{SERVICE_NAME}] Publishing on the port {PUB_PORT}...")
 
time.sleep(1)   # dar tiempo a que los subscribers se conecten
 
msg_index = 0
messages = SERVICE_MESSAGES.get(SERVICE_NAME, [f"[{SERVICE_NAME}] Test message"])
 
while True:
    if SERVICE_NAME == "HOUR":
        payload = f"[HOUR] {time.asctime()}"
    elif messages:
        payload = messages[msg_index % len(messages)]
        msg_index += 1
    else:
        payload = f"[{SERVICE_NAME}] Not configured messages"
 
    print(f"[PUBLISHER-{SERVICE_NAME}] Sending: {payload}")
    pub.send_string(payload)
    time.sleep(5)
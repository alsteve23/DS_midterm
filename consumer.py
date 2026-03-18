 
import zmq
import json
import sys
 
# Setting the servers
MAIN_SERVER_IP    = "127.0.0.1"
MAIN_SERVER_PORT  = "6000"
REPLICA_SERVER_IP = "127.0.0.1"
REPLICA_SERVER_PORT = "6001"
 
TIMEOUT_MS = 3000   # 3 seconds 
 
# Arguments
if len(sys.argv) < 2:
    print("Usage: python consumer.py <SERVICE> [NUM_MESSAGES]")
    sys.exit(1)
 
SERVICE_NAME  = sys.argv[1].upper()
NUM_MESSAGES  = int(sys.argv[2]) if len(sys.argv) >= 3 else 5
 
context = zmq.Context()
 
#Query the main server or replica
def query_server(server_ip, server_port, service_name, label):
    print(f"[CONSUMER] Quering {label} ({server_ip}:{server_port}) by SERVICE '{service_name}'...")
    req = context.socket(zmq.REQ)
    req.setsockopt(zmq.LINGER, 0)
    req.setsockopt(zmq.RCVTIMEO, TIMEOUT_MS)
    req.connect(f"tcp://{server_ip}:{server_port}")
    try:
        msg = json.dumps({"action": "QUERY", "service": service_name})
        req.send_string(msg)
        reply = json.loads(req.recv_string())
        req.close()
        return reply
    except zmq.error.Again:
        print(f"[CONSUMER] ⚠️  {label} did not answer (timeout {TIMEOUT_MS}ms).")
        req.close()
        return None
 
# Resolve the service location
reply = query_server(MAIN_SERVER_IP, MAIN_SERVER_PORT, SERVICE_NAME, "MAIN SERVER")
 
if reply is None or reply.get("status") != "OK":
    print("[CONSUMER] Trying with REPLICA SERVER ...")
    reply = query_server(REPLICA_SERVER_IP, REPLICA_SERVER_PORT, SERVICE_NAME, "REPLICA SERVER ")
 
if reply is None or reply.get("status") != "OK":
    reason = reply.get("message", "Unknown") if reply else "no answer"
    print(f"[CONSUMER] Could not resolve the SERVICE '{SERVICE_NAME}': {reason}")
    sys.exit(1)
 
pub_ip   = reply["ip"]
pub_port = reply["port"]
print(f"[CONSUMER] SERVICE '{SERVICE_NAME}' found in {pub_ip}:{pub_port}")
 
# Subscribe to the publisher
sub = context.socket(zmq.SUB)
sub.connect(f"tcp://{pub_ip}:{pub_port}")
 
# The topic matches with the service
topic_filter = f"[{SERVICE_NAME}]"
sub.setsockopt_string(zmq.SUBSCRIBE, topic_filter)
print(f"[CONSUMER] Suscribed to '{topic_filter}' on {pub_ip}:{pub_port}. Waiting {NUM_MESSAGES} messages...\n")
 
received = 0
while received < NUM_MESSAGES:
    message = sub.recv_string()
    print(f"[CONSUMER] 📨 {message}")
    received += 1
 
print(f"\n[CONSUMER] {NUM_MESSAGES} Received messages. End.")
sub.close()
context.term()
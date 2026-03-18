import zmq
import json, time

"""
MAIN SERVER
Hears publishers' registers 
Replicates de information to the replica server
Responds to the consumers queries about the service location
"""

MAIN_SERVER_PORT   = '6000'

REPLICA_SERVER_IP   = '127.0.0.1'

REPLICA_SERVER_PORT = '6001'


#To register the services: "name_service":{"ip":..., 'port':...}
service_registry ={}

context = zmq.Context()

server=context.socket(zmq.REP)
server.bind(f"tcp://0.0.0.0:{MAIN_SERVER_PORT}")
print(f"[MAIN SERVER] Hearing on port {MAIN_SERVER_PORT}...")

def sync_to_replica(registry):
    try:
        rep_socket = context.socket(zmq.REQ)
        rep_socket.setsockopt(zmq.LINGER, 0)
        rep_socket.setsockopt(zmq.RCVTIMEO, 2000)
        rep_socket.connect(f"tcp://{REPLICA_SERVER_IP}:{REPLICA_SERVER_PORT}")
        msg = json.dumps({"action": "SYNC", "registry": registry})
        rep_socket.send_string(msg)
        reply = rep_socket.recv_string()
        rep_socket.close()
        print(f"[MAIN SERVER] Replica Synchronized: {reply}")
    except zmq.error.Again:
        print("[MAIN SERVER]  Unable to connect to the replica server (timeout).")
    except Exception as e:
        print(f"[MAIN SERVER]  Error eith the replica syncronization: {e}")

while True:
    try:
        raw = server.recv_string()
        request = json.loads(raw)
        action = request.get("action")

        #publisher registers a service
        if action == "REGISTER":
            service = request["service"]
            ip      = request["ip"]
            port    = request["port"]
            service_registry[service] = {"ip": ip, "port": port}
            print(f"[MAIN SERVER] Service registered: [{service}] → {ip}:{port}")
            sync_to_replica(service_registry)
            server.send_string(json.dumps({"status": "OK", "message": f"Service '{service}' registered."}))

        #Consumer queries the location of a service
        elif action == "QUERY":
            service = request["service"]
            if service in service_registry:
                info = service_registry[service]    
                print(f"[MAIN SERVER] Query of '{service}' → answered with {info}")
                server.send_string(json.dumps({"status": "OK", "ip": info["ip"], "port": info["port"]}))
            else:
                print(f"[MAIN SERVER] Query of '{service}' → not found.")
                server.send_string(json.dumps({"status": "NOT_FOUND", "message": f"Service '{service}' not registered."}))
        
        else:
            server.send_string(json.dumps({"status": "ERROR", "message": "Unknown action."}))
    
    except json.JSONDecodeError:
        server.send_string(json.dumps({"status": "ERROR", "message": "Invalid JSON."}))
    except KeyboardInterrupt:
        print("\n[MAIN SERVER] Turning of...")
        break
    
server.close()
context.term()
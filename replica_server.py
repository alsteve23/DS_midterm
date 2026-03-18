import zmq
import json
 
REPLICA_SERVER_PORT = "6001"
 
service_registry = {}
 
context = zmq.Context()
 
server = context.socket(zmq.REP)
server.bind(f"tcp://0.0.0.0:{REPLICA_SERVER_PORT}")
print(f"[REPLICA SERVER] Hearing on port {REPLICA_SERVER_PORT}...")

while True:
    try:
        raw = server.recv_string()
        request = json.loads(raw)
        action = request.get("action")
 
        # Gets the synchronization from the main server
        if action == "SYNC":
            service_registry = request["registry"]
            print(f"[REPLICA SERVER] Register synchronized: {service_registry}")
            server.send_string(json.dumps({"status": "OK", "message": "Updated Replica ."}))


        # --- Consumer query, when the main server does not answer
        elif action == "QUERY":
            service = request["service"]
            if service in service_registry:
                info = service_registry[service]
                print(f"[REPLICA SERVER] Query of '{service}' → answered with {info}")
                server.send_string(json.dumps({"status": "OK", "ip": info["ip"], "port": info["port"]}))
            else:
                print(f"[REPLICA SERVER] Query of '{service}' Not found.")
                server.send_string(json.dumps({"status": "NOT_FOUND", "message": f"Servicio '{service}' no registrado."}))
 
        else:
            server.send_string(json.dumps({"status": "ERROR", "message": "Unknown action."}))
 
    except json.JSONDecodeError:
        server.send_string(json.dumps({"status": "ERROR", "message": "Invalid JSON."}))
    except KeyboardInterrupt:
        print("\n[REPLICA SERVER] Turning of...")
        break
 
server.close()
context.term()
 
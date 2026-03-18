# DS_midterm
Cómo ejecutar (abrir una terminal por proceso)
Paso 1 – Iniciar servidores
# Terminal 1
python replica_server.py

# Terminal 2
python main_server.py
Paso 2 – Registrar publishers
bash# Terminal 3
python publisher.py PELICULAS 15000

# Terminal 4
python publisher.py CLIMA 15001

# Terminal 5 (opcional)
python publisher.py HORA 15003
Paso 3 – Iniciar consumers
bash# Terminal 6 (recibe 5 mensajes del servicio PELICULAS)
python consumer.py PELICULAS 5

# Terminal 7
python consumer.py CLIMA 5

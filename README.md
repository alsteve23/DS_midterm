# DS_midterm

## 🚀 Cómo ejecutar (abrir una terminal por proceso)

## Paso 1 – Iniciar servidores

**Terminal 1**

```bash
python replica_server.py
```

**Terminal 2**

```bash
python main_server.py
```

## Paso 2 – Registrar publishers

**Terminal 3**

```bash
python publisher.py MOVIES 15000
```

**Terminal 4**

```bash
python publisher.py WEATHER 15001
```

**Terminal 5 (opcional)**

```bash
python publisher.py HOur 15003
```

## Paso 3 – Iniciar consumers

**Terminal 6**

Recibe 5 mensajes del servicio PELICULAS:

```bash
python consumer.py MOVIES
```

**Terminal 7**

```bash
python consumer.py WEATHER
```

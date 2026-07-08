# Activer l'environement virtuele Python

```bash
source ENVIRONNEMENT/bin/activate
```

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

# Dans votre fichier .env
MCP_JWT_SECRET=....

# Se placer dans le dossier du projet
```bash
cd ~/....
```
# Lancer le serveur
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```
# Ouvrir un autre Terminal, et puis Initialiser et récupérer le session-id
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \ 
  -D -
```

# Une fois qu'on a le session-id, l'insérer dans le code suivant pour afficher tools/list
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: Votre session-id" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```
# Lire le tools/list avec authentification 
```bash
curl -s -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJZdXRvbmciLCJleHAiOjE3OTExMTMxMzh9.MVglZhB9JnFATAFZ5x1O2A2H5lW4gg2xlJNJZrfCtd4" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq
```
# Activer l'environement virtuele Python

```bash
source ENVIRONNEMENT/bin/activate
```
# Se placer dans le dossier du projet
```bash
cd ~/....
```
# Se placer dans le dossier du projet
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


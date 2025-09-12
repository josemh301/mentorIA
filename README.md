# Discord Bot con RAG - Inversiones Inmobiliarias

Bot de Discord que utiliza la API de EdenAI RAG para responder preguntas sobre inversiones inmobiliarias.

## Configuración

### 1. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto con:

```
DISCORD_BOT_TOKEN=tu_token_de_discord_aqui
EDENAI_API_KEY=tu_api_key_de_edenai_aqui
RAG_PROJECT_ID=tu_project_id_de_rag_aqui
```

### 4. Configurar el bot de Discord

1. Ve al [Discord Developer Portal](https://discord.com/developers/applications/)
2. Crea una nueva aplicación o selecciona la existente
3. Ve a "Bot" y obtén tu token (guárdalo en el archivo `.env`)
4. Para crear el enlace de invitación privado:
   - Ve a "OAuth2" → "URL Generator"
   - Marca `bot` en scopes
   - Usa el permission integer: `17179879424`
   - El enlace final será: `https://discord.com/oauth2/authorize?client_id=TU_CLIENT_ID&scope=bot&permissions=17179879424`

### 5. Ejecutar el bot
```bash
python src/bot.py
```

## Comandos disponibles

- `!ask <your question>` - Ask questions about real estate investments
- `!ping` - Check bot latency
- `!ayuda` - Show available commands

## Estructura del proyecto

- `src/bot.py` - Bot principal de Discord
- `src/rag.py` - Integración con la API de EdenAI RAG
- `requirements.txt` - Dependencias del proyecto
- `.env` - Variables de entorno (crear manualmente)

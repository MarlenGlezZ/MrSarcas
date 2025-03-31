# MrSarcas
Bot en Telegram que corre en un contenedor de Docker.


# Instrucciones para desplegar tu Bot Sarcástico de Telegram con Docker

## Requisitos previos
- Docker y Docker Compose instalados en tu sistema
- Un token de bot de Telegram (obtenido a través de [@BotFather](https://t.me/BotFather))

## Pasos para el despliegue

### 1. Prepara los archivos
Crea una carpeta para tu proyecto y añade los siguientes archivos:
- `bot.py` (el código principal del bot)
- `Dockerfile` (para crear la imagen Docker)
- `requirements.txt` (dependencias de Python)
- `docker-compose.yml` (configuración para Docker Compose)

### 2. Configura el token de Telegram
Existen dos formas de proporcionar el token al contenedor:

#### Opción 1: Usando un archivo .env
Crea un archivo `.env` en la misma carpeta con el siguiente contenido:
```
TELEGRAM_TOKEN=tu_token_aquí
```

#### Opción 2: Exportando la variable directamente
```bash
export TELEGRAM_TOKEN=tu_token_aquí
```

### 3. Construye y ejecuta el contenedor Docker
```bash
docker-compose up -d
```

Este comando construirá la imagen Docker y ejecutará el contenedor en segundo plano.

### 4. Verifica que el bot esté funcionando
Abre Telegram y busca tu bot por su nombre de usuario (@nombre_de_tu_bot).
Envíale un mensaje como "Hola" y debería responderte con una respuesta sarcástica.

### 5. Ver los logs del bot
Si necesitas depurar o ver qué está haciendo el bot:
```bash
docker-compose logs -f
```

### 6. Detener el bot
Cuando quieras detener el bot:
```bash
docker-compose down
```

## Personalización adicional

Si deseas agregar más respuestas sarcásticas o modificar el comportamiento del bot, edita los arrays de respuestas en el archivo `bot.py` y reconstruye la imagen:

```bash
docker-compose down
docker-compose up -d --build
```

¡Disfruta de tu bot sarcástico!

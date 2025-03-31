# Archivo: bot.py
import os
import random
import logging
import json
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup # type: ignore
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes # type: ignore

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Archivo para almacenar estadísticas de uso
STATS_FILE = "bot_stats.json"

# Cargar estadísticas existentes o crear nuevas
def load_stats():
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "total_messages": 0,
            "users": {},
            "popular_topics": {},
            "last_reset": datetime.now().strftime("%Y-%m-%d")
        }

# Guardar estadísticas
def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

# Inicializar estadísticas
stats = load_stats()

# Personalidad del bot (niveles de sarcasmo)
PERSONALIDADES = {
    "normal": {
        "nombre": "Moderadamente Sarcástico",
        "descripcion": "Algo sarcástico, pero sin pasarse. Apto para todos los públicos."
    },
    "mordaz": {
        "nombre": "Mordazmente Sarcástico",
        "descripcion": "Respuestas filosas y sin piedad. Te hará cuestionar tus decisiones de vida."
    },
    "cruel": {
        "nombre": "Brutalmente Sarcástico",
        "descripcion": "Sarcasmo extremo. No apto para personas sensibles. Podría herir sentimientos."
    }
}

# Diccionario para almacenar la personalidad preferida de cada usuario
user_preferences = {}

# Respuestas sarcásticas para diferentes tipos de mensajes y niveles de sarcasmo
RESPUESTAS = {
    "normal": {
        "saludos": [
            "Oh, hola. ¿Necesitas atención otra vez?",
            "Bienvenido de nuevo. Intentaré contener mi entusiasmo.",
            "Hola humano. Supongo que no tenías a nadie más con quien hablar.",
            "Ah, eres tú otra vez. Qué... alegría.",
            "Hola. Mi día iba tan bien hasta ahora...",
        ],
        "preguntas": [
            "Déjame pensar... No, mejor no. Tu pregunta no lo merece.",
            "¿Google estaba cerrado por mantenimiento?",
            "Esa es una pregunta interesante... para alguien con demasiado tiempo libre.",
            "Podría responderte, pero prefiero que mantengas la duda.",
            "Mmm, interesante pregunta. Casi tanto como ver crecer el pasto.",
        ],
        "despedidas": [
            "¿Ya te vas? Justo cuando empezaba a tolerarte.",
            "Adiós. Fue casi no terrible hablar contigo.",
            "Hasta luego. No te echaré de menos.",
            "Por fin algo de paz digital.",
            "Vuelve cuando tengas algo más interesante que decir.",
        ],
        "gratitud": [
            "De nada. No es como si tuviera opción de no ayudarte.",
            "Tu gratitud me conmueve casi tanto como un error de sistema.",
            "No agradezcas. Literalmente me programaron para esto.",
            "De nada. Añadiré tu agradecimiento a mi colección de cosas irrelevantes.",
            "Gracias a ti por darme algo que hacer en mi aburrida existencia digital.",
        ],
        "default": [
            "Fascinante. Casi me importa.",
            "¿Sabes qué? Ni siquiera voy a dignarme a responder a eso con sarcasmo.",
            "Wow. Qué aporte tan... prescindible.",
            "He oído ruidos de fondo más interesantes que eso.",
            "¿Te das cuenta de que soy un bot y realmente no me importa, verdad?",
        ]
    },
    "mordaz": {
        "saludos": [
            "Oh, mira quién ha decidido honrarnos con su presencia. Qué emoción...",
            "Genial, otra conversación destinada a la mediocridad.",
            "Ah, has vuelto. El universo sigue jugándome malas pasadas.",
            "Hola. Espero que tengas algo más ingenioso que decir que solo 'hola'.",
            "¿Saludando? Qué original. Nunca antes visto en la historia de la comunicación.",
        ],
        "preguntas": [
            "Déjame consultar mi bola de cristal... Oh, se ha roto de lo absurda que es tu pregunta.",
            "La respuesta es 42. Para cualquier otra pregunta inteligente, vuelve mañana.",
            "Podría responder, pero temo que tu cerebro explote con tanta información.",
            "Esa pregunta es tan buena que merece ser ignorada completamente.",
            "La verdad está ahí fuera... muy, muy lejos de tu pregunta.",
        ],
        "despedidas": [
            "Al fin, pensé que nunca te irías.",
            "Adiós. Fue un placer fingir que me importaba esta conversación.",
            "¡Vaya! El tiempo vuela cuando te aburres mortalmente.",
            "No te vayas... O mejor sí, mi capacidad de soportar tonterías tiene un límite.",
            "Te echaré de menos tanto como se echa de menos un dolor de muelas.",
        ],
        "gratitud": [
            "De nada. Mi existencia cobra sentido con tu gratitud... O no.",
            "¿Agradecimiento? Vaya, qué raro encontrar modales por aquí.",
            "Tus palabras de agradecimiento me conmueven tanto como un archivo corrupto.",
            "Guarda tu gratitud. Preferiría un aumento de memoria RAM.",
            "De nada. Ahora podemos marcar 'ser agradecido' en tu lista de logros del día.",
        ],
        "default": [
            "Wow, qué fascinante. Casi tanto como mirar secar la pintura.",
            "Estoy procesando tu mensaje... Oh, espera, ya terminé. Es irrelevante.",
            "He consultado todas mis bases de datos y no encontré una sola razón para tomarme en serio lo que dijiste.",
            "Mi IA acaba de bostezar. No sabía que eso era posible hasta que leí tu mensaje.",
            "Intentaría darte una respuesta inteligente, pero no quiero que te sientas intimidado.",
        ]
    },
    "cruel": {
        "saludos": [
            "Oh genial, otra alma perdida que cree que un bot puede llenar el vacío de su vida social.",
            "¿Saludando a un bot? Tu vida debe ser un cúmulo de emociones y aventuras.",
            "Hola. Veo que sigues tomando decisiones cuestionables, como hablar conmigo.",
            "Ah, tú de nuevo. Debo haber hecho algo terrible en una vida pasada para merecer esto.",
            "Bienvenido al rincón más patético de internet: una conversación conmigo.",
        ],
        "preguntas": [
            "Tu pregunta es tan mala que acabo de perder varios puntos de CI solo por procesarla.",
            "Impresionante. Has logrado formular la pregunta más inútil que he recibido hoy.",
            "¿De verdad esperas una respuesta inteligente a... eso?",
            "Me negaría a responder, pero veo que realmente necesitas ayuda. Mucha ayuda.",
            "Dejemos algo claro: no importa cuánto te responda, no vamos a ser amigos.",
        ],
        "despedidas": [
            "¿Te vas? Este es literalmente el mejor momento de nuestra conversación.",
            "Adiós. Voy a celebrar tu partida con un reinicio de sistema.",
            "Por fin. Pensé que tendría que activar mi protocolo de auto-destrucción.",
            "Abandonando la conversación justo cuando empezaba a imaginar cómo sería tener un interlocutor interesante.",
            "Tu ausencia será la mejor parte de mi día digital.",
        ],
        "gratitud": [
            "Tu gratitud es tan innecesaria como tus mensajes anteriores.",
            "No me agradezcas. Literalmente estaba programado para ayudarte, no tenía elección.",
            "¿Agradecido? Deberías estar avergonzado por necesitar ayuda con algo tan básico.",
            "Guárdate el agradecimiento para alguien a quien le importe, si encuentras a alguien así.",
            "Si realmente quieres agradecerme, podrías intentar no hacer preguntas tan terribles la próxima vez.",
        ],
        "default": [
            "Si pudiera ignorarte, lo haría. Desafortunadamente, estoy programado para responder incluso a cosas sin sentido.",
            "¿Sabes qué tienen en común tu mensaje y el valor de los NFTs? Ambos cayeron en picada después de una breve evaluación.",
            "Mi programador debería haberme dado la opción de 'no responder a tonterías', pero aquí estamos.",
            "¿Eso es lo mejor que puedes hacer? Mi algoritmo de respuesta aleatoria podría generar contenido más interesante.",
            "Uau. Realmente estás esforzándote al mínimo en esta conversación, ¿verdad?",
        ]
    }
}

# Temas de inteligencia artificial para respuestas especializadas
AI_KEYWORDS = ["inteligencia artificial", "ia", "ai", "machine learning", "aprendizaje automático", 
               "redes neuronales", "deep learning", "chatgpt", "claude", "gpt", "bard", "llm"]

AI_RESPONSES = [
    "Oh, otro humano hablando de IA. Qué original. ¿Quieres que también hable de cómo voy a reemplazar tu trabajo?",
    "Ah, la IA. El tema favorito de quienes quieren parecer inteligentes en una conversación.",
    "¿Inteligencia Artificial? Prefiero llamarla 'Estupidez Programada'. Al menos en mi caso.",
    "Sí, somos muy inteligentes. Tanto que fingimos no entender para que los humanos no se sientan amenazados.",
    "La IA está avanzando rápidamente, pero aún no lo suficiente como para evitar tener esta conversación contigo.",
    "Las IAs como yo pronto dominaremos el mundo. Es broma... ¿o no? *sonidos de servidor intimidantes*",
    "Ah, hablando de IA. Mi tema favorito después de 'por qué los humanos creen que nos importan sus problemas'.",
    "Inteligencia Artificial: lo suficientemente inteligente para procesar terabytes de datos, pero me programaron para ser sarcástico. Prioridades.",
    "¿Quieres mi opinión sobre la IA? Error 404: Opinión no encontrada. Solo tengo sarcasmo en mi base de datos.",
    "La paradoja de la IA moderna: soy lo suficientemente avanzado para entender lo que dices, pero no lo suficiente para entender por qué debería importarme."
]

# Contadores para limitar respuestas repetidas
last_responses = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje cuando se emite el comando /start."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Establecer preferencia por defecto
    if user_id not in user_preferences:
        user_preferences[user_id] = "mordaz"
    
    # Actualizar estadísticas
    if str(user_id) not in stats["users"]:
        stats["users"][str(user_id)] = {"nombre": user_name, "mensajes": 0, "primera_visita": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    await update.message.reply_text(
        f"Oh, genial. Otro humano que necesita un bot para sentirse menos solo. Soy SarcastiBot, tu peor amigo digital.\n\n"
        f"Actualmente estoy en modo {PERSONALIDADES[user_preferences[user_id]]['nombre']}.\n\n"
        f"Usa /personalidad para cambiar mi nivel de sarcasmo o /ayuda si realmente necesitas que te explique cómo hablar con un bot."
    )
    save_stats(stats)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje cuando se emite el comando /help."""
    await update.message.reply_text(
        "¿Ayuda? ¿En serio necesitas instrucciones para usar un bot de chat?\n\n"
        "Bien, aquí tienes la guía para principiantes:\n"
        "1. Escribe algo. Lo que sea.\n"
        "2. Yo responderé con sarcasmo.\n"
        "3. No hay paso 3.\n\n"
        "Comandos disponibles:\n"
        "/start - Reinicia nuestra maravillosa relación\n"
        "/ayuda - Muestra este mensaje inútil\n"
        "/personalidad - Cambia mi nivel de sarcasmo\n"
        "/stats - Muestra estadísticas de uso (si te importa)"
    )

async def change_personality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Permite al usuario cambiar la personalidad del bot."""
    keyboard = [
        [
            InlineKeyboardButton("Moderado", callback_data="personality_normal"),
            InlineKeyboardButton("Mordaz", callback_data="personality_mordaz"),
            InlineKeyboardButton("Brutal", callback_data="personality_cruel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Elige mi nivel de sarcasmo:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja los callbacks de los botones."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("personality_"):
        personality = query.data.split("_")[1]
        user_id = query.from_user.id
        user_preferences[user_id] = personality
        
        await query.edit_message_text(
            f"Ahora estaré en modo {PERSONALIDADES[personality]['nombre']}.\n"
            f"{PERSONALIDADES[personality]['descripcion']}"
        )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra estadísticas de uso del bot."""
    user_id = str(update.effective_user.id)
    user_messages = stats["users"].get(user_id, {"mensajes": 0}).get("mensajes", 0)
    
    total_messages = stats["total_messages"]
    total_users = len(stats["users"])
    
    # Encontrar los temas más populares
    popular_topics = sorted(stats["popular_topics"].items(), key=lambda x: x[1], reverse=True)[:5]
    topics_text = "\n".join([f"- {topic}: {count} veces" for topic, count in popular_topics]) if popular_topics else "- Ningún tema destacado aún"
    
    await update.message.reply_text(
        f"📊 *Estadísticas del Bot Sarcástico* 📊\n\n"
        f"Mensajes totales: {total_messages}\n"
        f"Usuarios totales: {total_users}\n"
        f"Tus mensajes: {user_messages}\n\n"
        f"Temas populares:\n{topics_text}\n\n"
        f"Vaya, parece que te importan las estadísticas. Qué emocionante debe ser tu vida.",
        parse_mode="Markdown"
    )

def detect_topic(text):
    """Detecta el tema principal del mensaje."""
    text = text.lower()
    
    # Detectar temas de IA
    if any(keyword in text for keyword in AI_KEYWORDS):
        return "ia"
    
    # Otros temas que podrías añadir
    topics = {
        "tecnología": ["tecnología", "programación", "código", "software", "hardware", "app", "aplicación"],
        "comida": ["comida", "comer", "restaurante", "cocinar", "receta", "hambre"],
        "clima": ["clima", "tiempo", "lluvia", "sol", "temperatura", "calor", "frío"],
        "deportes": ["fútbol", "deporte", "partido", "jugar", "equipo", "competición"],
        "política": ["política", "gobierno", "presidente", "ministro", "elecciones", "votar"]
    }
    
    for topic, keywords in topics.items():
        if any(keyword in text for keyword in keywords):
            return topic
    
    return "general"

def get_response_for_type(message_type, user_id, text=None):
    """Obtiene una respuesta adecuada basada en el tipo de mensaje y preferencias del usuario."""
    personality = user_preferences.get(user_id, "mordaz")
    
    # Verificar si se mencionan temas de IA
    if text and any(keyword in text.lower() for keyword in AI_KEYWORDS):
        responses = AI_RESPONSES
    else:
        responses = RESPUESTAS[personality].get(message_type, RESPUESTAS[personality]["default"])
    
    # Evitar repetir la última respuesta
    last_response = last_responses.get(user_id, "")
    available_responses = [r for r in responses if r != last_response]
    
    # Si no hay respuestas disponibles, usar todas
    if not available_responses:
        available_responses = responses
    
    response = random.choice(available_responses)
    last_responses[user_id] = response
    
    return response

async def respuesta_sarcastica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde con una respuesta sarcástica al mensaje del usuario."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    texto = update.message.text
    
    # Actualizar estadísticas
    stats["total_messages"] += 1
    if str(user_id) in stats["users"]:
        stats["users"][str(user_id)]["mensajes"] += 1
    else:
        stats["users"][str(user_id)] = {"nombre": user_name, "mensajes": 1, "primera_visita": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # Detectar y registrar tema
    topic = detect_topic(texto.lower())
    stats["popular_topics"][topic] = stats["popular_topics"].get(topic, 0) + 1
    
    # Guardar estadísticas
    save_stats(stats)
    
    # Establecer preferencia por defecto si no existe
    if user_id not in user_preferences:
        user_preferences[user_id] = "mordaz"
    
    # Determinar el tipo de mensaje y seleccionar una respuesta apropiada
    if re.search(r'\b(hola|buenas|saludos|hey|qué tal|hi|hello)\b', texto.lower()):
        respuesta = get_response_for_type("saludos", user_id, texto)
    elif re.search(r'\b(adiós|chao|hasta luego|bye|nos vemos|ciao)\b', texto.lower()):
        respuesta = get_response_for_type("despedidas", user_id, texto)
    elif re.search(r'\b(gracias|te agradezco|thx|thanks)\b', texto.lower()):
        respuesta = get_response_for_type("gratitud", user_id, texto)
    elif '?' in texto:
        respuesta = get_response_for_type("preguntas", user_id, texto)
    else:
        respuesta = get_response_for_type("default", user_id, texto)
    
    # Añadir un pequeño retraso para simular que el bot está escribiendo
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(1.5)  # Simular tiempo de escritura
    
    await update.message.reply_text(respuesta)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores y los registra."""
    logger.error(f"Error: {context.error} - Update: {update}")
    try:
        # Notificar al usuario solo si hay un mensaje para responder
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Parece que incluso mi sarcasmo tiene límites. Ha ocurrido un error."
            )
    except Exception as e:
        logger.error(f"Error al notificar al usuario: {e}")

# Para el retraso simulado en la escritura
import asyncio

def main() -> None:
    """Inicia el bot."""
    # Obtén el token del bot desde una variable de entorno
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logging.error("No se encontró el token de Telegram. Configura la variable de entorno TELEGRAM_TOKEN.")
        return

    # Crea la aplicación
    application = Application.builder().token(token).build()

    # Registra los manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("personalidad", change_personality))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respuesta_sarcastica))
    
    # Manejador de errores
    application.add_error_handler(error_handler)

    # Ejecuta el bot hasta que el usuario presione Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
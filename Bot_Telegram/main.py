from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

async def responder_coctel(update: Update, context: CallbackContext):
    nombre = update.message.text.strip()
    ingredientes = obtener_receta(nombre)
    descripcion = obtener_descripcion(nombre)

    if ingredientes:
        mensaje = f"{nombre}: {descripcion}"
        mensaje += f"\n\nIngredientes para {nombre}:\n"
        for nombre_ingrediente, cantidad in ingredientes:
            mensaje += f"🔸 {cantidad} de {nombre_ingrediente}\n"
    else:
        mensaje = "No encontré ese cóctel. Asegúrate de escribirlo correctamente."

    await update.message.reply_text(mensaje)

def obtener_descripcion(nombre_coctel):
    conn=sqlite3.connect("Bot_Telegram/base_datos_bot.db")
    cursor=conn.cursor()
    consulta= """
    SELECT descripcion 
    FROM cocteles
    WHERE LOWER(nombre) = LOWER(?)
    """
    cursor.execute(consulta, (nombre_coctel,))
    resultados=cursor.fetchone()
    return resultados[0];

def obtener_receta(nombre_coctel):
    conn=sqlite3.connect("Bot_Telegram/base_datos_bot.db")

    cursor=conn.cursor()

    consulta = """
    SELECT i.nombre, ci.cantidad
    FROM cocteles c
    JOIN coctel_ingredientes ci ON c.id = ci.coctel_id
    JOIN ingredientes i ON i.id = ci.ingrediente_id
    WHERE LOWER(c.nombre) = LOWER(?)
    """

    cursor.execute(consulta, (nombre_coctel,))
    resultados=cursor.fetchall()  
    print(f"Resultados: {resultados}")
    return resultados;

# Comando /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "¡Bienvenido! Menciona un cóctel:"
    )
# Comando /ayuda
async def ayuda(update: Update, contexto: CallbackContext):
    await update.message.reply_text("Escribe el nombre de un cóctel y te daré una breve descripción," \
    " además de una receta para elaborarlo.")
# Comando /menu
async def menu(update:Update, contexto:CallbackContext):
    conn=sqlite3.connect("Bot_Telegram/base_datos_bot.db")
    cursor=conn.cursor()
    consulta="""
    SELECT nombre
    FROM cocteles
"""
    cursor.execute(consulta)
    resultados=cursor.fetchall()
    mensaje="Los cócteles son: \n"
    for (nombre,) in resultados:
        mensaje +=f"{nombre}\n"
    await update.message.reply_text(mensaje)
    return resultados;


# Configuración del bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ayuda",ayuda))
app.add_handler(CommandHandler("menu", menu))
print("🤖 Bot con menú iniciado...")
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_coctel))
app.run_polling()


from fastapi import FastAPI, APIRouter, Request
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler
import logging

# from .webhook import router as webhook_router

from ..config import settings

logger = logging.getLogger(__name__)

# Handler asincrono
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        param = context.args[0]
        await update.message.reply_text(f"Hai inviato il parametro: {param}")
    else:
        await update.message.reply_text("Nessun parametro ricevuto.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        param = context.args[0]
        await update.message.reply_text(f"Login Hai inviato il parametro: {param}")
    else:
        await update.message.reply_text("Login Nessun parametro ricevuto.")

# Definisci un router FastAPI ed un endpoint per il webhook
webhook_router = APIRouter()
bot_app = None

@webhook_router.post("")
async def telegram_webhook(request: Request):
    global bot_app
    data = await request.json()
    # data = dict(update)
    logger.info(f"Telegram bot webhook: {data}")
    # logger.info(f"Telegram bot webhook: {update}")
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

async def init(fastapi_app: FastAPI):
    global bot_app
    if not settings.telegram_bot.enable:
        logger.info("Telegram bot is disabled in config, it will not be started.")
        return

    # Costruisci l'app del bot
    bot_app = Application.builder().token(settings.telegram_bot.api_token).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("login", login))

    # Calcola l'url pubblico del webhook
    public_webhook_url = f"{settings.api.public_url}{settings.telegram_bot.webhook_uri}"

    logger.info(f"Telegram bot is starting! Webhook URL: {public_webhook_url}")

    # Aggiungi il router dell'endpoint webhook a FastAPI
    fastapi_app.include_router(webhook_router, prefix=f"{settings.telegram_bot.webhook_uri}", tags=["Telegram Bot Webhook"])

    # Registra il webhook sull' API telegram
    await bot_app.bot.set_webhook(public_webhook_url)

    # Inizializza l'app del bot
    await bot_app.initialize()



import os
import discord
import requests
from googletrans import Translator
from flask import Flask
from threading import Thread

# Webserver för 24/7 host
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

translator = Translator()

# Språk och deras kanaler/webhooks
LANGS = {
    "en": {
        "channel": int(os.getenv("CHANNEL_ENGLISH")),
        "webhook": os.getenv("WEBHOOK_ENGLISH")
    },
    "pl": {
        "channel": int(os.getenv("CHANNEL_POLISH")),
        "webhook": os.getenv("WEBHOOK_POLISH")
    },
    "de": {
        "channel": int(os.getenv("CHANNEL_GERMAN")),
        "webhook": os.getenv("WEBHOOK_GERMAN")
    },
    "uk": {
        "channel": int(os.getenv("CHANNEL_UKRAINIAN")),
        "webhook": os.getenv("WEBHOOK_UKRAINIAN")
    }
}

def send_webhook(webhook_url, username, avatar_url, content):
    if not webhook_url:
        return
    data = {
        "username": username,
        "avatar_url": avatar_url,
        "content": content
    }
    requests.post(webhook_url, json=data)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Identifiera källspråk via kanal
    source_lang = None
    for lang, info in LANGS.items():
        if message.channel.id == info["channel"]:
            source_lang = lang
            break

    if not source_lang:
        return  # Meddelande inte i någon av våra kanaler

    # Översätt till alla andra språk och skicka via deras webhooks
    for target_lang, info in LANGS.items():
        if target_lang == source_lang:
            continue
        translated = translator.translate(message.content, src=source_lang, dest=target_lang).text
        send_webhook(
            info["webhook"],
            message.author.display_name,
            message.author.avatar.url if message.author.avatar else "",
            translated
        )

# Starta botten med token från .env
client.run(os.getenv("DISCORD_TOKEN"))

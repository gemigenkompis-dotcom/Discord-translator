import os
import discord
import requests
from googletrans import Translator
from flask import Flask
from threading import Thread

# --- Environment Variables ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ENGLISH = int(os.getenv("CHANNEL_ENGLISH"))
CHANNEL_POLISH = int(os.getenv("CHANNEL_POLISH"))
CHANNEL_GERMAN = int(os.getenv("CHANNEL_GERMAN"))
CHANNEL_UKRAINIAN = int(os.getenv("CHANNEL_UKRAINIAN"))

WEBHOOK_ENGLISH = os.getenv("WEBHOOK_ENGLISH")
WEBHOOK_POLISH = os.getenv("WEBHOOK_POLISH")
WEBHOOK_GERMAN = os.getenv("WEBHOOK_GERMAN")
WEBHOOK_UKRAINIAN = os.getenv("WEBHOOK_UKRAINIAN")

# --- Discord client ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- Translator ---
translator = Translator()

# --- Flask server for uptime ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

# --- Webhook sender ---
def send_webhook(webhook_url, username, avatar_url, content):
    data = {
        "username": username,
        "avatar_url": avatar_url,
        "content": content
    }
    requests.post(webhook_url, json=data)

# --- Language mapping ---
CHANNEL_TO_LANG = {
    CHANNEL_ENGLISH: "en",
    CHANNEL_POLISH: "pl",
    CHANNEL_GERMAN: "de",
    CHANNEL_UKRAINIAN: "uk"
}

CHANNEL_TO_WEBHOOK = {
    CHANNEL_ENGLISH: WEBHOOK_ENGLISH,
    CHANNEL_POLISH: WEBHOOK_POLISH,
    CHANNEL_GERMAN: WEBHOOK_GERMAN,
    CHANNEL_UKRAINIAN: WEBHOOK_UKRAINIAN
}

@client.event
async def on_message(message):
    if message.author.bot:
        return

    source_channel = message.channel.id
    if source_channel not in CHANNEL_TO_LANG:
        return

    source_lang = CHANNEL_TO_LANG[source_channel]

    # Skicka översättningar till alla andra språk
    for target_channel, target_lang in CHANNEL_TO_LANG.items():
        if target_lang == source_lang:
            continue  # hoppa över samma språk

        try:
            translated_obj = await translator.translate(message.content, src=source_lang, dest=target_lang)
            translated_text = translated_obj.text
            send_webhook(
                CHANNEL_TO_WEBHOOK[target_channel],
                message.author.display_name,
                message.author.avatar.url if message.author.avatar else "",
                translated_text
            )
        except Exception as e:
            print(f"Översättningsfel: {e}")

# --- Run Discord bot ---
client.run(DISCORD_TOKEN)

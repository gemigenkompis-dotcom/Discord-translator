import os
import discord
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load all the shit
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

LANGUAGES = {
    "en": {
        "channel": int(os.getenv("CHANNEL_ENGLISH")),
        "webhook": os.getenv("WEBHOOK_ENGLISH"),
    },
    "pl": {
        "channel": int(os.getenv("CHANNEL_POLISH")),
        "webhook": os.getenv("WEBHOOK_POLISH"),
    },
    "de": {
        "channel": int(os.getenv("CHANNEL_GERMAN")),
        "webhook": os.getenv("WEBHOOK_GERMAN"),
    },
    "uk": {  # Ukrainian
        "channel": int(os.getenv("CHANNEL_UKRAINIAN")),
        "webhook": os.getenv("WEBHOOK_UKRAINIAN"),
    },
}

# Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


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

    author_name = message.author.display_name
    author_avatar = message.author.avatar.url if message.author.avatar else ""

    # Detect which language/channel the message is from
    for lang, info in LANGUAGES.items():
        if message.channel.id == info["channel"]:
            source_lang = lang

            # Translate to all other languages
            for target_lang, target_info in LANGUAGES.items():
                if target_lang == source_lang:
                    continue  # skip same language
                translated = GoogleTranslator(source=source_lang, target=target_lang).translate(message.content)
                send_webhook(target_info["webhook"], author_name, author_avatar, translated)
            break


client.run(TOKEN)

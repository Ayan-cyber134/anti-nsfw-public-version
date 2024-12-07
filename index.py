import discord
from discord.ext import commands
import requests

# Bot Configuration
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="%£%£", intents=intents)

# Sightengine API Configuration
API_USER = "user"
API_SECRET = "secret" 
API_URL = "https://api.sightengine.com/1.0/check.json"

# Image Analysis Function
def analyze_image(image_url):
    payload = {
        "url": image_url,
        "models": "nudity,wad,offensive,scam",  # Include multiple models
        "api_user": API_USER,
        "api_secret": API_SECRET,
    }
    response = requests.get(API_URL, params=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Event for Moderating Image Messages
@bot.event
async def on_message(message):
    if message.attachments:  # Check if the message contains attachments
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                # Analyze the image
                analysis = analyze_image(attachment.url)
                if analysis:
                    # Nudity Detection
                    nudity = analysis.get("nudity", {})
                    raw_nudity = nudity.get("raw", 0)
                    partial_nudity = nudity.get("partial", 0)

                    # Violence Detection
                    wad = analysis.get("weapon", 0) + analysis.get("alcohol", 0) + analysis.get("drugs", 0)

                    # Offensive Content Detection
                    offensive = analysis.get("offensive", {}).get("prob", 0)

                    # Take actions based on thresholds
                    if raw_nudity > 0.8 or partial_nudity > 0.8:
                        await message.delete()
                        await message.channel.send(
                            f"{message.author.mention}, your image was flagged as inappropriate and removed (nudity)."
                        )
                        await message.author.kick(reason="Uploaded inappropriate content (nudity).")
                    elif wad > 0.8:
                        await message.delete()
                        await message.channel.send(
                            f"{message.author.mention}, your image was flagged for promoting violence or harmful substances and removed."
                        )
                        await message.author.kick(reason="Uploaded violent or harmful content.")
                    elif offensive > 0.8:
                        await message.delete()
                        await message.channel.send(
                            f"{message.author.mention}, your image was flagged as offensive and removed."
                        )
                        await message.author.kick(reason="Uploaded offensive content.")
                    else:
                        print("Image passed the check.")

                else:
                    print("Failed to analyze the image. Check the API response.")
    await bot.process_commands(message)

# bot token
bot.run("token")

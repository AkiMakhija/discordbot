import json
import os
import random

import discord
import requests
from dotenv import load_dotenv
from replit import db

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

sad_words  = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starter_encouragements = [
  "Cheer up!",
  "Hang in there.",
  "You are a great person / bot!"
]

if "responding" not in db.keys():
  db["responding"] = True
  
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]

def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements
    
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  if db["responding"]:
    options=starter_encouragements[:]
    if "encouragements" in db.keys():
      options.extend(list(db["encouragements"]))
  
    if any(word in message.content for word in sad_words):
      response = random.choice(options)
      await message.channel.send(response)

  if message.content.startswith("$new"):
    encouraging_message = message.content.split("$new ",1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")

  if message.content.startswith("$del"):
    if "encouragements" in db.keys():
      index = int(message.content.split("$del ", 1)[1])
      delete_encouragement(index)
      encouragements = list(db["encouragements"])
      if encouragements:
          await message.channel.send(f"Additional Encouragements: {', '.join(encouragements)}")
      else:
          await message.channel.send("No more Additional encouragements left.")
  
  if message.content.startswith("$list"):
    encouragements=[]
    if "encouragements" in db.keys():
      encouragements=list(db["encouragements"])
    await message.channel.send( {', '.join(encouragements)})

  if message.content.startswith("$responding"):
    parts = message.content.split(maxsplit=1)  # Split on the first space only
    if len(parts) == 2:
        value = parts[1].strip().lower()
        if value == "true":
            db["responding"] = True
            await message.channel.send("Responding is on.")
        elif value == "false":
            db["responding"] = False
            await message.channel.send("Responding is off.")

keep_alive()
load_dotenv()
token = os.getenv('TOKEN')
client.run(token)
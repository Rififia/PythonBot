# coding: utf8

import discord
from discord.ext import commands
import constants
import sys
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
from datetime import datetime

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
console = sys.stdout




#detecter l'allumage du bot
@bot.event
async def on_ready():
    print("Successfully connected !")
    servernb = str(len(bot.guilds))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("serving "+servernb+" servers"))



@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    serveur = member.guild.id
    if channel is not None:
        await channel.send('Welcome in the server {0.mention}.'.format(member))

#commande test
@bot.command()
async def ping(ctx):
    """
    A small command to see if the bot is alive
    """
    await ctx.send("pong")

@bot.command()
async def python(ctx):
    """
    A command to execute python scripts.
    First, call the command, and wait for a bot waiting message.
    Second, write your code. You can choose to write it with or without the python code markdown\n(\`\`\`python\n code \n \`\`\`)\n
    """
    sys.stdout = console
    channel = ctx.channel
    authorid = ctx.author.id
    def check(m):
        return m.channel == channel and m.author.id == authorid
    messagebot = await ctx.send(constants.send_wait_msg)
    prgm = await bot.wait_for('message', check=check)
    await messagebot.delete(delay=2)
    await ctx.message.delete(delay=2)
    if prgm.content.startswith("```"):
        prgm.content = prgm.content.replace("```python","")
        prgm.content = prgm.content.replace("```","")
    with open("input.py","w") as input_file:
        input_file.write(prgm.content)

    os.system("wandbox-python3 run input.py > retour.txt")

    with open("retour.txt", "r") as output_file:
        raw_output = output_file.read()

    if not raw_output.startswith("signal: Killed"):
        raw_output = raw_output[17:]
    else:
        raw_output = "Note: Your program was killed (it's either too slow or too greedy in ressources)!\n" + raw_output

    raw_output = "```py\n" + raw_output + "```"

    if len(raw_output) <= 2000:
        message = await ctx.send(raw_output)
    else:
        with open("retour.txt", "r") as output_file:
            message = await ctx.send("Your program printed more than 1991 characters.", file=discord.File(output_file, filename=datetime.now().strftime("%d-%b-%Y-%H:%M:%S.txt")))

    await message.add_reaction(constants.emotrash)


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    messageReaction = await channel.fetch_message(payload.message_id)
    if messageReaction.author.id == constants.botid and payload.user_id != constants.botid:
        if payload.emoji.name == constants.emotrash:
            await messageReaction.delete()

 
@bot.event
async def on_message(ctx):
    servernb = str(len(bot.guilds))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("serving " + servernb + " servers"))



load_dotenv()
token = os.getenv('TOKEN')

keep_alive()
bot.run(token)

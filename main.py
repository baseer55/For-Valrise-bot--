import discord
from discord.ext import commands
from data import TOKEN

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.initial_setup = False

@bot.event
async def on_ready():
	print('Bot is ready!')
	if not bot.initial_setup:
		bot.initial_setup = True
		await bot.load_extension('extras')
		await bot.tree.sync(guild=discord.Object(id=1213615486986747934))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if 'wow' in message.content.lower():
        await message.add_reaction('\U0001F440')

    if "korwnaios" in message.content.lower():
        await message.channel.send('Gheaa')

    if "locmax" in message.content.lower():
        await message.channel.send('ng jew wtfff')    
    if "benson" in message.content.lower():
        await message.channel.send('Fucking arab')

    if "valrise" in message.content.lower():
        await message.channel.send('this retarded tdm server still alive?')

    if "samp" in message.content.lower():
        await message.channel.send('samp is dead bro')

    if "kacper" in message.content.lower():
        await message.channel.send('go to gym xd')

    if "dox" in message.content.lower():
        await message.channel.send('haram wtf')

    if "autism" in message.content.lower():
        await message.channel.send('autism based')
        
    if "sex" in message.content.lower (): 
        await message.channel.send('want sex bro?')


bot.run(TOKEN)
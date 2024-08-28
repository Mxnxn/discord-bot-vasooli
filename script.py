import os, asyncio, discord
from dotenv import load_dotenv
from discord.ext import commands
import re
from cogs.reminder import Reminder
from cogs.listall import List
from model.database import initialize_database
import datetime
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Set up the bot with the command prefix (e.g., "!")
intents = discord.Intents.all()
intents.message_content = True  #Enable the message content intent


prefix = '/'
bot = commands.Bot(command_prefix=prefix,description="Arrey! jaldi bol panvel nikalna hai!", intents=intents)
# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

load_dotenv()
DB_NAME = os.getenv('DB_NAME')

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		return
	if isinstance(error, commands.CommandInvokeError):
		print(f'command: {prefix}{ctx.command} | kwargs: {str(ctx.args[1].kwargs)} | error: {error}')
		return
	if isinstance(error, commands.MissingRequiredArgument):
		return await ctx.send(f'Command "{ctx.command}": A required argument is missing.')
	
	return print(f'command: {prefix}{ctx.command} | error: {error}')

async def main():
    async with bot:
        initialize_database()
        await bot.add_cog(Reminder(bot))
        await bot.add_cog(List(bot))
        await bot.start(TOKEN)

asyncio.run(main())
# Run the bot with your token
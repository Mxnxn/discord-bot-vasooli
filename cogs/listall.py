from discord.ext import tasks, commands
import sqlite3 as sql
from utils.time import time_shortner
from utils.sql import data_fetcher
import re
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv('DB_NAME')

class List(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.table = 'reminders'

    @commands.group(name='listall', invoke_without_command=True, description= 'Helps to list reminders')
    async def listall(self, ctx):
        await ctx.send("Please refer `-h` for more info")
    
    @listall.command(name='-h')
    async def list_all_help(self, ctx, query: str = None):
        print()
        await ctx.send('''```/listall <options> <param>
    -a to list all pending/upcoming reminders
    -p @<usr> to list user specific reminders
    -r <id> to delete an reminder```''')

    @listall.command(name='-a', description= 'to list all the pending/upcoming reminders')
    async def list_all_reminder(self, ctx, query: str = None):
        sql_query = f'SELECT * from {self.table};'
        rows = data_fetcher(sql_query)
        response = 'Pending reminders!```'
        if not rows:
            await ctx.send(f'No reminders!')
            return
        for i, row in enumerate(rows):
            print(row)
            time = time_shortner(row[3])
            remaining = time_shortner(row[4], True)
            response += f"\n{i+1}. \"{row[1]}\" in {time}: {remaining} remaning (_id: {row[0]})"
        await ctx.send(f'{response}```')
    
    @listall.command(name='-p')
    async def list_personal_reminder(self, ctx, *, query):
        id = re.search('<@(\d*)>', query)
        if id:
            discord_id = id.groups()[0]
            sql_query = f' SELECT * from {self.table} WHERE author_id = {discord_id};'
            rows = data_fetcher(sql_query)
            i = 0
            response = ''
            for row in rows:
                time = time_shortner(row[3])
                remaining = time_shortner(row[4], True)
                i =+ 1
                response += f"\n{i}. \"{row[1]}\" in {time}: {remaining} remaning (_id: {row[0]})"
            response = f'Isne <@{row[2]}> ye ye diya:```' + response
            await ctx.send(f'{response}```')
        else:
            await ctx.send(f"something is wrong! Syntax: `/listall -p @user`")

    @listall.command(name='-r')
    async def listall_r(self, ctx, *, query):
        match = re.search(r'\b\d+\b', query)
        if match:
            id = match.group()
            conn = sql.connect(DB_NAME)
            cur = conn.cursor()
            row = cur.execute(f'SELECT COUNT(*) FROM {self.table} WHERE id = {id};').fetchone()
            if row[0] == 0:
                await ctx.send(f"Id not exist! syntax: `/listall -r <digit>`")
            else:
                cur.execute(f'DELETE FROM {self.table} WHERE id = {id};')
                conn.commit()
            conn.close()
            if row[0] != 0:
                await self.list_all_reminder(ctx)
        else:
            await ctx.send(f"Incorrect id! syntax: `/listall -r <digit>`")
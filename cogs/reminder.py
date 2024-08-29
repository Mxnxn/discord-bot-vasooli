import discord
from discord.ext import tasks, commands

import sqlite3 as sql
import re

from dotenv import load_dotenv
import os

from utils.time import parse_time_duration, time_shortner, time_modify_and_shortner
from utils.sql import data_fetcher
import asyncio
import datetime
client = discord.Client(intents=discord.Intents.all())
load_dotenv()
DB_NAME = os.getenv('DB_NAME')

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DB_NAME
        self.table = 'reminders'
        self.reminder_loop.start()

    @commands.group(name='reminder', invoke_without_command=True)
    async def reminder(self, ctx, *, query:str):
        # Define the command you want to execute
        args = query.split('-t')
        author = ctx.author
        period = parse_time_duration(args[1].strip())
        text = args[0].strip()
        conn = sql.connect(self.db)
        cursor = conn.cursor()
        time = time_shortner(args[1].strip())
        date_1 = datetime.datetime.now()
        end_date = date_1 + datetime.timedelta(**period)
         
        cursor.execute('''
            INSERT INTO {} (author_id, task_period, task_trigger, task, server_id, ch_id) 
            VALUES (:author_id, :task_period, :task_trigger, :task, :server_id, :ch_id)
        '''.format(self.table), {
            'author_id':author.id,
            'task_period': args[1].strip(),
            'task_trigger': end_date,
            'task': text,
            'server_id':ctx.guild.id,
            'ch_id': ctx.channel.id
        })
        cursor.execute('''
            INSERT OR IGNORE INTO users (author_id, name, global_name) 
            VALUES (:author_id, :name, :global_name)
        '''.format(self.table), {
            'author_id':author.id,
            'name': author.name,
            'global_name': author.global_name
        })

        conn.commit()
        conn.close()

        # Send the output to the Discord channel
        await ctx.send(f'<@{author.id}> Tere ko "{text}" ke liye {time} ke bad milta hu')

    @reminder.command(name='-i')
    async def add_reminder(self, ctx, *, query: str):
        if '-a' in query:
            args = [arg.strip() for arg in query.split('-a')]
            id = args[0]
            match = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?').match(args[1])
            if not id or not match.group() or not args[1] : 
                await ctx.send('''Incorrect id, time or format! ```-i <missing/incorrect> -a <missing/incorrect>    
    format: 0d, 0h, 0m, 0s, or 0d0h (combination)```''')
                return None
            time = parse_time_duration(args[1])
            sql_query = f'SELECT * FROM {self.table} WHERE id = {id};'
            row = data_fetcher(sql_query)
            if row:
                prev_date = datetime.datetime.strptime(row[0][4], f'%Y-%m-%d %H:%M:%S.%f')
                new_date = prev_date + datetime.timedelta(**time)
                new_time_string = time_modify_and_shortner(row[0][3], args[1], 'ADD')
                print('here',new_date, new_time_string)
                conn = sql.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''UPDATE reminders SET task_trigger= ?, task_period=? WHERE id = ?;''', (new_date, new_time_string, id))
                conn.commit()
                conn.close()
                await ctx.send(f'Hattsale, ab vapis itna wait: `{new_time_string}`! Is janam mai panvel nahi ja payega.')
                return 
            await ctx.send('Incorrect <id> provided! run /listall -p @tag to findout!')
            return
        elif '-r' in query:
            args = [arg.strip() for arg in query.split('-r')]
            id = args[0]
            match = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?').match(args[1])
            if not id or not match.group() or not args[1] : 
                await ctx.send('''Incorrect id, time or format! ```-i <missing/incorrect> -a <missing/incorrect>    
    format: 0d, 0h, 0m, 0s, or 0d0h (combination)```''')
                return None
            time = parse_time_duration(args[1])
            sql_query = f'SELECT * FROM {self.table} WHERE id = {id};'
            row = data_fetcher(sql_query)
            if row:
                new_time_string = time_modify_and_shortner(row[0][3], args[1], 'REDUCE')
                # This will ask if reduction is in -minus time and want to delete instead!
                if new_time_string == '0s':
                    await ctx.send('requested query time will set timer to 0! Do you want to delete instead?')

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']

                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        await ctx.send('No response received. Operation cancelled.')
                        return None
                    
                    if msg.content.lower() == 'yes':
                        List = self.bot.get_cog('List')
                        await List.listall_r(ctx, query=f'-r {id}') 
                        await ctx.send('Kar diya! delete!')
                    else:
                        await ctx.send('Kaiko khali fokat kaam deta hai!')
                    return
                prev_date = datetime.datetime.strptime(row[0][4], f'%Y-%m-%d %H:%M:%S.%f')
                new_date = prev_date - datetime.timedelta(**time)
                conn = sql.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''UPDATE reminders SET task_trigger= ?, task_period=? WHERE id = ?;''', (new_date, new_time_string, id))
                conn.commit()
                conn.close()
                await ctx.send(f'ye hui na baat, ab khali itna wait: `{new_time_string}`! Is janam mai hi ja payega PANVEL.')
                return
             
            await ctx.send('Incorrect `id` provided! run `/listall -p @tag` to findout!')
            return
        await ctx.send('''Incorrect time! ```-i id -a <missing/incorrect>    
    format: 0d, 0h, 0m, 0s, or 0d0h (combination)```''')
        return
            
        


    def cog_unload(self):
        self.reminder_loop.cancel()

    @tasks.loop(minutes=10)
    async def reminder_loop(self):
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            sql_query = f'SELECT * FROM {self.table} r, users u WHERE u.author_id = r.author_id;'
            data = cursor.execute(sql_query).fetchall()
            row_ids = []
            for row in data:
                task_dt = datetime.datetime.strptime(row[4], f'%Y-%m-%d %H:%M:%S.%f') 
                now = datetime.datetime.now()
                if now > task_dt:
                    row_ids.append((row[0],))    
                    ctx = self.bot.get_guild(int(row[5])).get_channel(int(row[6]))
                    await ctx.send(f'<@{row[8]}> *{row[9]}/{row[10]}* jo bhi tera  naam hai: \"{row[1]}\" ye yaad aya kya? \"{row[3]}\" bola tha! ')
            cursor.executemany('DELETE FROM reminders WHERE id = ?;', row_ids)
            conn.commit()
            conn.close()    
        except Exception as e:
            print(e)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()
        return 

# diary.py
# discord bot invite link - 
# https://discord.com/api/oauth2/authorize?client_id=869745680472739880&permissions=8&scope=bot

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pymongo
import urllib
import random
from datetime import datetime
import asyncio
import dateutil.parser as date_parser
import geopy
import pytz

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')
MONGODB_CONN = os.getenv('MONGODB_CONN')

# # creates a geopy variable to find timezone from given City/Country
# g = geopy.geocoders.GoogleV3()

# creates connection with MongoDB atlas database
client = pymongo.MongoClient(MONGODB_CONN)

# imports the collection/tables
task_table = (client.get_database('todo')).records
user_table = (client.get_database('todo')).user_data

bot = commands.Bot(command_prefix='~')

@bot.command(name='list', help = 'It is supposed to list out your tasks, but it is currently broken')
async def lister(ctx):
    response = "Too lazy\nBitch"
    await ctx.send(response)
    
@bot.command(name='add', help = 'Adds a task. Follow through the prompts to create a solid entry')
async def adder(ctx):
    task_numb = 0
    user_id = str(ctx.message.author.id)
    date_added = str(datetime.utcnow().strftime("%d/%m/%Y"))
    time_added = str(datetime.utcnow().strftime("%H:%M:%S"))
    date_expire = date_added
    time_expire = None
    task = None
    server_ID = str(ctx.message.guild.id)
    server_name = ctx.message.guild.name
    
    def check(m: discord.Message):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
    
    ## Gets the task
    await ctx.channel.send("What is the task?")
    
    try:
        msg = await bot.wait_for("message", check=check, timeout=120.00)
    except asyncio.TimeoutError:
        await ctx.send(f"**{ctx.author}**, you didn't send any message that meets the check in this channel for 180 seconds..")
        return
    else:
        task = msg.content
        if task[0] == "~":
            await ctx.invoke(bot.get_command(task[1:].lower()))
            return
        else:
            await ctx.send(f"**{ctx.author}**, you responded with \'{msg.content}\'!")
        
        
    ## Gets the due date
    await ctx.channel.send("What date is this task due?")
################## date format with month - %d %b %Y
    try:
        msg = await bot.wait_for("message", check=check, timeout=120.00)     
    except asyncio.TimeoutError:
        await ctx.send(f"**{ctx.author}**, you didn't send any message that meets the check in this channel for 180 seconds..")
        return
    else:
        try:
            date_expire = str(date_parser.parse(msg.content).date().strftime('%d-%m-%Y'))
        except:
            await ctx.send(f"**{ctx.author}**, something was wrong with the format of your date ({msg.content}).\nPlease try adding the task again, with the date in the following format: dd-mm-yyyy")
            return
        else:
            if msg.content[0] == "~":
                await ctx.invoke(bot.get_command(msg.content[1:].lower()))
                return
            else:
                await ctx.send(f"**{ctx.author}**, you responded with \'{str(date_parser.parse(msg.content).date().strftime('%d %b %Y'))}!\'")
    
    
    ## Gets the due time
    await ctx.channel.send("What time is this task due (Type \"Skip\" to have the task due at the end of the day)?")
    
    try:
        msg = await bot.wait_for("message", check=check, timeout=120.00)     
    except asyncio.TimeoutError:
        await ctx.send(f"**{ctx.author}**, you didn't send any message that meets the check in this channel for 180 seconds..")
        return
    else:
        if(msg.content.lower() == "skip"):
            time_expire = str(date_parser.parse("21:59:59").time())
        elif msg.content[0] == "~":
            await ctx.invoke(bot.get_command(msg.content[1:].lower()))
            return
        else:
            try:
                time_expire = str(date_parser.parse(msg.content).time())
            except:
                await ctx.send(f"**{ctx.author}**, something was wrong with the format of your time ({msg.content}).\nPlease try adding the task again, with the time in the following format: hh:mm [am/pm]")
                return
            else:
                pass
        await ctx.send(f"**{ctx.author}**, you responded with \'{time_expire}\'!")
     
    
    ## Checks if the user is in our database. If not, creates an entry into the database.
    if user_table.count_documents({"user_id": user_id}) != 0:
        doc = user_table.find_one({"user_id": user_id})
        task_numb = 1 + int(doc["number_tasks"])
        user_table.update_one({ "user_id" : user_id }, { "$set": { "number_tasks": str(task_numb) } })
    else:
        task_numb = 1
        
        new_user = {
            "number_tasks": str(task_numb),
            "user_id": str(ctx.message.author.id),
            "user_name": str(ctx.author),
            "user_timezone": ""
        }   

        user_table.insert_one(new_user)
            
    new_task = {
        "task_id": str(task_numb),
        "user_id": user_id,
        "user_name": str(ctx.author),
        "date_added": date_added,
        "time_added": time_added,
        "date_expire": date_expire,
        "time_expire": time_expire,
        "task": task,
        "server_ID": server_ID,
        "server_name": server_name
    }

    task_table.insert_one(new_task)
    end_message = "Task Added!\n> Task: {}\n> Due Date: {}\n> Due Time: {}".format(task, date_expire, time_expire)
    await ctx.send(end_message)

############### UPCOMING FEATURES. NEED TO FIND GOOD API FOR TIMEZONE.
## Sets timezone of a user. Helps with precise removal of tasks that expire
# @bot.command(name='setZone', help = 'It is supposed to list out your tasks, but it is currently broken')
# async def smol(ctx):
    
#     def check(m: discord.Message):
#         return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
    
#     ## Gets the city/country
#     await ctx.channel.send("What is your city?")
    
#     try:
#         msg = await bot.wait_for("message", check=check, timeout=120.00)     
#     except asyncio.TimeoutError:
#         await ctx.send(f"**{ctx.author}**, you didn't send any message that meets the check in this channel for 180 seconds..")
#         return
#     else:
#         time_zone = g.timezone(g.geocode(msg.content).point)
#         await ctx.send(f"**{ctx.author}**, you responded with\nTask - {msg.content} which has a timezone of {str(time_zone)}!")
    
    
bot.run(TOKEN)


##################################################################################
#client = discord.Client()

# @client.event
# async def on_ready():
#     for guild in client.guilds:
#         if guild.name == GUILD:
#             break

#     print(
#         f'{client.user} is connected to the following guild:\n'
#         f'{guild.name}(id: {guild.id})'
#     )
    
# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
    
    

#client.run(TOKEN)   
##################################################################################
import os
import discord
from dotenv import load_dotenv
import pymongo
import urllib

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MONGODB_CONN = os.getenv('MONGODB_CONN')

# creates connection with MongoDB atlas database
client = pymongo.MongoClient(MONGODB_CONN)

table = (client.get_database('todo')).records
user_table = (client.get_database('todo')).user_data


print(table.count_documents({}))

new_entry = {
    "task_id": {
        "$numberInt": "2"
    },
    "user_id": "1234",
    "date_added": "12/04/1999",
    "time_added": "00:01",
    "date_expire": "12/04/1999",
    "time_expire": "00:02",
    "task": "Do Something",
    "server_ID": "1234",
    "server_name": "Server Test"
}

table.insert_one(new_entry)
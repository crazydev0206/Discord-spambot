import discord
import asyncio
import json

import termcolor


def write_fancy_message(event_name, color="yellow"):
    message = f"/!\ {event_name}"
    print(termcolor.colored(message, color, attrs=["bold"]))


client = discord.Client(intents=discord.Intents.all())
# dictionary to store user information for each user
user_data = {}

# name of the file to store user data
data_file = 'user_data.json'

# load user data from file
try:
    with open(data_file, 'r') as file:
        user_data = json.load(file)
        write_fancy_message("[DONE] Loaded user data from file correctly. Task completed.")
        # convert keys to int
        user_data = {int(k): v for k, v in user_data.items()}
        write_fancy_message("[DONE] Converted keys to int. Task completed.")
except:
    pass


# helper function to update user data
def update_user_data(user_id, key, value):
    if user_id not in user_data:
        print("User not found in user_data. Creating new entry. =>", user_id)
        user_data[user_id] = {}
    user_data[user_id][key] = value

    with open(data_file, 'w') as file:
        json.dump(user_data, file)


# mute time in minutes
mute_time = {0: 10, 1: 30, 2: 1440}


@client.event
async def on_message(message):
    spammed = False
    user_id = message.author.id
    user_data_key = 'last_message_time'
    current_time = message.created_at.timestamp()

    # check if the user is already muted
    if user_id in user_data and 'mute_end_time' in user_data[user_id] and current_time < user_data[user_id][
        'mute_end_time']:
        await message.delete()
        print("get out of here")
        return

    if message.author == client.user:
        return

    if user_id in user_data and user_data_key in user_data[user_id]:
        last_message_time = user_data[user_id][user_data_key]
        time_diff = current_time - last_message_time

        # check if the user is sending messages too fast
        if time_diff < 10:
            await message.delete()
            await message.author.send('Typing too fast only 1 text per 10 seconds.')
            spammed = True

        elif message.attachments:
            attachment_diff = current_time - user_data[user_id]['last_attachment_time']
            if attachment_diff < 120:
                await message.delete()
                await message.author.send('Typing too fast only 1 attachment per 2 minutes.')
                spammed = True
            else:
                update_user_data(user_id, 'last_attachment_time', current_time)
        elif message.content.find('.gif') != -1:
            gif_diff = current_time - user_data[user_id]['last_gif_time']
            if gif_diff < 120:
                await message.delete()
                await message.author.send('Typing too fast only 1 gif per 2 minutes.')
                spammed = True
            else:
                update_user_data(user_id, 'last_gif_time', current_time)
        elif message.content.startswith('http'):
            link_diff = current_time - user_data[user_id]['last_link_time']
            if link_diff < 300:
                await message.delete()
                await message.author.send('Typing too fast only 1 link per 5 minutes.')
                spammed = True
            else:
                update_user_data(user_id, 'last_link_time', current_time)
    else:
        update_user_data(user_id, 'last_message_time', current_time)
        update_user_data(user_id, 'spam_count', 0)
        if message.attachments:
            update_user_data(user_id, 'last_attachment_time', current_time)
            update_user_data(user_id, 'last_link_time', 0)
            update_user_data(user_id, 'last_gif_time', 0)
        elif message.content.find('.gif') != -1:
            update_user_data(user_id, 'last_gif_time', current_time)
            update_user_data(user_id, 'last_link_time', 0)
            update_user_data(user_id, 'last_attachment_time', 0)
        elif message.content.startswith('http'):
            update_user_data(user_id, 'last_link_time', current_time)
            update_user_data(user_id, 'last_attachment_time', 0)
            update_user_data(user_id, 'last_gif_time', 0)
        else:
            print("no attachment")
            update_user_data(user_id, 'last_link_time', 0)
            update_user_data(user_id, 'last_attachment_time', 0)
            update_user_data(user_id, 'last_gif_time', 0)

    update_user_data(user_id, user_data_key, current_time)

    # check if the user is spamming
    if user_id in user_data and 'spam_count' in user_data[user_id] and spammed:
        mute_duration = mute_time[user_data[user_id]['spam_count']]
        await message.author.send(f'You have been muted for {mute_duration} minutes for sending too many messages.')
        update_user_data(user_id, 'mute_end_time', current_time + mute_duration * 60)
        update_user_data(user_id, 'spam_count', (user_data[user_id]['spam_count'] + 1) % 3)


@client.event
async def on_ready():
    print('Bot is ready.')


# replace the token with your Discord bot token
client.run('')

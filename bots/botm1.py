import sys, os
filename = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(1, filename)
from zoomapi import OAuthZoomClient

import json
from configparser import ConfigParser
from pyngrok import ngrok
import time

cid = None
cname = None
parser = ConfigParser()
parser.read("bots/bot.ini")
client_id = parser.get("OAuth", "client_id")
client_secret = parser.get("OAuth", "client_secret")
browser_path = parser.get("OAuth", "browser_path")
port = parser.getint("OAuth", "port", fallback=4001)
print(f'id: {client_id} browser: {browser_path}')

redirect_url = ngrok.connect(port, "http")
print("Redirect URL is", redirect_url)

client = OAuthZoomClient(client_id, client_secret, port, redirect_url, browser_path)

user_response = client.user.get(id='me')
user = json.loads(user_response.content)
print(user)
print ('---')
print(json.loads(client.meeting.list(user_id="me").content))

first_channel = json.loads(client.chat_channels.list().content)["channels"][0]
cid = first_channel["id"]
cname = first_channel["name"]


stop = False
while not stop:
    print("Current channel name: " + cname)
    print("Current channel id: " + cid)    
    message = input("Enter message: ")
    if message == "!stop":
        stop = True 
    elif message == "!switch":
        cid = input("Enter new channel id: ")
        cname = res = json.loads(client.chat_channels.get(channel_id=cid).content)["name"]

    elif message == "!list channel":
        channel_list = json.loads(client.chat_channels.list().content)["channels"]
        print("----------Channels----------")
        for c in channel_list:
            print("id: "+c["id"])
            print("name: "+c["name"]+"\n")
        print("----------------------------")
    elif message == "!create channel":
        name = input("Enter name of your channel: ")
        c_type = int(input("Enter type of your channel(1-4): "))
        n = input("Enter number of the members(max of 5): ")
        emails = []
        for i in range(int(n)):
            member = {"email":input("Enter {}th member's email: ".format(i+1))}
            emails.append(member)
        res = json.loads(client.chat_channels.create(name=name, type=c_type, members=emails).content)
        print(res)
    elif message == "!get channel":
        c_id = input("Enter channel id:")  
        res = json.loads(client.chat_channels.get(channel_id=c_id).content)
        print(res)
    elif message == "!update channel":
        c_id = input("The id of the channel you wanna update: ")
        c_name = input("Enter new name for this channel: ")
        res = client.chat_channels.update(channel_id=c_id, name = c_name)
        print(res)
    elif message == "!delete channel":
        c_id = input("The id of the channel you wanna delete: ")
        res = client.chat_channels.delete(channel_id=c_id)
        print(res)
    elif message == "!list member":
        c_id = input("The id of the channel you wanna list: ")
        members = json.loads(client.chat_channels.list_member(channel_id=c_id).content)["members"]
        print("----------------------------")
        for m in members:
            print(m["id"])
            print(m["first_name"]+" "+m["last_name"]+"\n")
        print("----------------------------")
    elif message == "!invite":
        c_id = input("The id of the channel you wanna add members: ")
        n = input("Enter number of the members: ")
        members = []
        for i in range(int(n)):
            member = {"email":input("Enter {}th member's email: ".format(i+1))}
            members.append(member)
        res = client.chat_channels.invite_member(channel_id=c_id, members = members)
        print(res)
    elif message == "!join":
        c_id = input("The id of the channel you wanna join: ")
        res = client.chat_channels.join(channel_id = c_id)
        print(res)
    elif message == "!leave":
        c_id = input("The id of the channel you wanna leave: ")
        res = client.chat_channels.leave(channel_id = c_id)
        print(res)
    elif message == "!remove":
        c_id = input("The id of the channel you wanna remove member: ")
        mb_id = input("The id of the member you wanna remove: ")
        res = client.chat_channels.remove_member(channel_id = c_id, member_id = mb_id)
        print(res.content)
    elif message == "!update message":
        ms_id = input("The id of the message you wanna update: ")
        ms = input("The content of the message you wanna update: ")
        res = client.chat_messages.update(message_id = ms_id, message = ms, to_channel=cid)
        print(res.content)
    elif message == "!delete message":
        ms_id = input("The id of the message you wanna delete: ")
        res = client.chat_messages.delete(message_id = ms_id, to_channel = cid)
        print(res.content)
    else:
        client.chat_messages.post(to_channel=cid, message=message)
        # print(json.loads(client.chat_messages.list(to_channel = cid, user_id="me").content))
        time.sleep(0.4)
        messages = json.loads(client.chat_messages.list(to_channel = cid, user_id="me").content)["messages"]
        print("----------------------------")
        for m in messages:
            print(m["date_time"]+" <"+m["id"]+">")
            print("-" + m["sender"] + ": " + m["message"]+"\n")
        print("----------------------------")

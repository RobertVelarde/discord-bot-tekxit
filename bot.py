import asyncio
import discord
import threading
import sys
from pexpect import popen_spawn, EOF
from config import *

command = "java -server -Xmx4G -Xms4G -jar forge-1.12.2-14.23.5.2824-universal.jar nogui"


# 'Forward-declaring' global variables
serverStatus = stopped
serverProcess= None
playerCount = 0

client = discord.Client()
clientLoop = asyncio.get_event_loop();

async def respond(message, response):
    print(response)
    await message.channel.send(response)

def inputThread(child):
    global serverStatus
    global serverProcess

    while serverStatus == running:
        command = input()
        if serverStatus == running:
            child.sendline(command)
        else:
            print("Server is no longer running.")

@client.event
async def on_ready():
    print("Ready! Updating game status.")
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game("Tekxit OFFLINE"))

@client.event
async def on_message(message):
    global serverStatus

    # Messages from the bot
    if message.author == client.user:
        return

    # Start
    if message.content.startswith('$start'):

        # Check flags
        if serverStatus == starting:
            await respond(message, "Server is already starting.")

        elif serverStatus == running:
            await respond(message, "Server is already running.")

        elif serverStatus == stopping:
            await respond(message, "Server is currently shutting down. Please wait to restart.")

        elif serverStatus == stopped:
            await respond(message, "Starting the server...")
            await startServer(message)

    # Stop
    if message.content.startswith('$stop'):

        # Check flags
        if serverStatus == starting:
            await respond(message, "Server is currently starting. Please wait before shutting down.")

        elif serverStatus == running:
            if playerCount > 0:
                await respond(message, "Cannot shutdown. Someone is online")
            else:
                await respond(message, "Shutting down the server...")
                await stopServer()

        elif serverStatus == stopping:
            await respond(message, "Server is already shutting down.")

        elif serverStatus == stopped:
            await respond(message, "Server is already shut down.")

def serverThread(message, child):
    global serverStatus
    global playerCount

    loop = asyncio.new_event_loop();
    asyncio.set_event_loop(loop)
    child.logfile_read = sys.stdout.buffer

    # Starting
    while serverStatus == starting:
        index = child.expect([regexFml, regexDone, regexLine], timeout=None)

        # regexFml
        if index == 0:
            child.sendline('/fml confirm')

        # regexDone
        elif index == 1:
            print("Server is online!")
            serverStatus = running
            loop.run_until_complete(client.change_presence(status=discord.Status.online, activity=discord.Game("Tekxit ONLINE")))
            asyncio.run_coroutine_threadsafe(message.channel.send("Server is online!"), clientLoop).result()

            # Start thread so we can take input from user and send it to the server as commands
            threading.Thread(target=inputThread, daemon=True, args=(serverProcess,)).start()

    # Running
    while serverStatus != stopped:
        try:
            index = child.expect([regexJoin, regexLeave, regexLine], timeout=None)

            # regexJoin
            if index == 0:
                playerCount += 1

            # regexLeave
            elif index == 1:
                playerCount -= 1

        except EOF:
            serverStatus = stopped
            print("Shut down.")
            loop.run_until_complete(client.change_presence(status=discord.Status.dnd, activity=discord.Game("Tekxit OFFLINE")))
            asyncio.run_coroutine_threadsafe(message.channel.send("Server is offline."), clientLoop).result()

    loop.close()

async def startServer(message):
    global serverProcess
    global serverStatus

    serverStatus = starting
    serverProcess = popen_spawn.PopenSpawn(command)
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Tekxit STARTING"))
    threading.Thread(target=serverThread, daemon=True, args=(message,serverProcess,)).start()

async def stopServer():
    global serverProcess

    serverStatus = stopping
    serverProcess.sendline('stop')

print("Starting the bot...")
client.run(discordToken)

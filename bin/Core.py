import zmq
import json
import subprocess
import spotipy
import dotenv
import os
from spotipy.oauth2 import SpotifyOAuth
from pythonosc.udp_client import SimpleUDPClient
import time
import random
from colorama import Fore



core_start = time.time()
custompy = None
message = None

with open("config.json", "r", encoding="utf-8") as file:
    configdata = json.load(file)

dotenv.load_dotenv()

ip = "127.0.0.1"
port = 9000

client = SimpleUDPClient(ip, port)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-currently-playing"
    ))

def secondsToTime(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:2d}:{minutes:02d}:{seconds:02d}"

def get_current_spotify_song():
    current = sp.current_user_playing_track()
    if current is None or current.get("item") is None:
        return {}

    item = current["item"]
    return {
        "title": item["name"],
        "artist": item["artists"][0]["name"],
        "album": item["album"]["name"],
        "is_playing": current["is_playing"]
    }

def insert_string_at_index(original_string, string_to_insert, index):
    return original_string[:index] + string_to_insert + original_string[index:]

def get_gpu_status_no_popup():
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            creationflags=0x08000000
        )
        gpus = []
        for line in result.stdout.strip().split("\n"):
            index, name, mem_total, mem_used, load = line.split(", ")
            gpus.append(
                type("GPU", (object,), {
                    "id": int(index),
                    "name": name,
                    "memoryTotal": float(mem_total)/1000,
                    "memoryUsed": float(mem_used)/1000,
                    "load": float(load)/100
                })()
            )
        return gpus


endstr = ""
chatbox = ""

chatpy = subprocess.Popen(["python", "Chat.py"])

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:8391")

print(Fore.GREEN + "[+] Socket Successfully Bound.")


primarydata = {
    "chatbox": "Awaiting Socket Connection...",
    "chatboxmessage": "",
    "afk": False
}

statindex = 0
loop_time = time.time()
afkvalset = False
afktime = 0
while True:
    if loop_time+2 > time.time():
        socket.recv_json()
        socket.send_json(primarydata)
        continue

    loop_time = time.time()
    gpus = get_gpu_status_no_popup()
    gpu = gpus[0]
    spotstr = "⏸️"
    spotifyret = get_current_spotify_song()
    if spotifyret:
        titless = str(spotifyret["title"])
        if len(str(spotifyret["title"])) > 18:
            titless = insert_string_at_index(str(spotifyret["title"]), "...[]]\-=", 17)
        spotemoji = "⏸️"
        if spotifyret["is_playing"]:
            spotemoji = "🎵"
        spotstr = f"{spotemoji} {titless.split('[]]\-=')[0]} ᵇʸ {spotifyret['artist']}"


    timestr = f"⏱️ ᴾˡᵃʸ ᵀᶦᵐᵉ {secondsToTime(time.time() - core_start)}"
    gpustat = f"ᵍᵖᵘ {int(gpu.load*50)}% ¦ ᵛʳᵃᵐ {round(gpu.memoryUsed, 1 )}/{round(gpu.memoryTotal, 1)}Gb"
    statstr = f"{random.choice(configdata["emojis"])} {configdata["status_messages"][statindex]}"

    
    
    statindex += 1
    if statindex >= len(configdata["status_messages"]):
        statindex = 0
        with open("config.json", 'r', encoding="utf8") as file:
            newdata = json.load(file)
            if newdata != configdata:
                try:
                    configdata = newdata
                    print(Fore.GREEN + "[+] Updated Config Data Successfully.")
                except: print(Fore.RED + "[-] Config Data Failed to Load.")

    primarydata.update({"chatbox": endstr})


    newmsg = socket.recv_json()

    if newmsg != message:
        message = newmsg
        if not message["closing"]: print(Fore.BLUE + "[/] Received New Input Data.")

    if message["client"] == "chat":
        if message["afk"]:
            if not afkvalset:
                afk_time = time.time()
                afkvalset = True
            statstr = f"💤 ᶜᵘʳʳᵉⁿᵗˡʸ ᵃᶠᵏ ᶠᵒʳ {secondsToTime(time.time() - afk_time)}"
        elif not message["afk"]: afkvalset = False
        primarydata.update({"chatboxmessage": message["chatboxmessage"], "afk": message["afk"]})
        if message["closing"]:
            break
        
        chatbox = message["chatboxmessage"]


    socket.send_json(primarydata)
    

    endstr = f"{statstr}\n{gpustat}\n{timestr}\n{spotstr}\n{chatbox}"

    client.send_message("/chatbox/input", [endstr, True, False])



chatpy.terminate()
chatpy.wait()

os.system("pause")
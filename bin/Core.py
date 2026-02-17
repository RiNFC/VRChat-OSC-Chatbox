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
from colorama import Fore, init
from datetime import datetime

init()

print(Fore.MAGENTA + "[;] Experimental Swirl Str")
print("""Paterns:
1, ∘·•∘·•∘·•∘·•∘·•
2, ｡･ﾟ･｡･ﾟ･｡･ﾟ･
3, ┈┊┈┊┈┊┈┊┈
4, ˙·˙·˙·˙·˙·
5, ◌◦∘·∘◦◌◦∘·∘\n""")



superscript_numbers = [
    "⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"
]

normal_numbers = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]

core_start = time.time()
custompy = None
message = None

with open("config.json", "r", encoding="utf-8") as file:
    configdata = json.load(file)

try:
    with open(".timecache", "r") as file:
        timecache = json.load(file)
        if time.time() - timecache["closingtime"] < 300:
            core_start = timecache["core_start"]

except: pass

dotenv.load_dotenv()


port = 9000

try: ip = configdata["ip"]
except:
    ip = "127.0.0.1"
    if ".ip" in os.listdir():
        with open(".ip", "r", encoding="utf8") as file:
            ip = file.read()
            with open("config.json", "w", encoding="utf8") as file:
                json.dump(configdata.update({"ip": ip}))
        os.remove(".ip")
        
    

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

def get_current_time():
    return datetime.now().strftime("%I:%M %p")



def secondsToTimeH(seconds):
    seconds = int(seconds)  # convert float → int
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{minutes:2d}:{seconds:02d}"

def progressbar(progress, duration):
    barstr = ""
    progstr = ""
    durastr = ""
    timeindex = round(((progress/1000)/(duration/1000))*10)
    for i in range(0, 11):
        if i <= timeindex: 
            barstr = barstr + "▓"
        else: barstr = barstr + "░"
    
    ts = secondsToTimeH(progress/1000)
    first = False
    first2 = False

    for c in secondsToTimeH(duration/1000):
        try:
            sixseven2 = normal_numbers.index(c)
            durastr = durastr + superscript_numbers[sixseven2]
        except ValueError:
            if first2:
                durastr = durastr + "'"
            else: first2 = True

    for pmo in ts:
        try:
            sixseven = normal_numbers.index(pmo)
            progstr = progstr + superscript_numbers[sixseven]
        except ValueError:
            if first:
                progstr = progstr + "'"
            else: first = True
    return(f"{progstr} {barstr} {durastr}")



def secondsToTime(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:2d}:{minutes:02d}:{seconds:02d}"

def get_current_spotify_song():
    try:
        current = sp.current_user_playing_track()
    except: 
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-currently-playing"
    ))
        current = sp.current_user_playing_track()
        
    if current is None or current.get("item") is None:
        return {}

    item = current["item"]
    return {
        "title": item["name"],
        "artist": item["artists"][0]["name"],
        "album": item["album"]["name"],
        "is_playing": current["is_playing"],
        "progress": current["progress_ms"],
        "duration": item["duration_ms"]
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
barstr = ""
gpustatstr = ""
spotstr = ""

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

paterns= ["∘·•∘·•∘·•∘·•∘·•", "｡･ﾟ･｡･ﾟ･｡･ﾟ･", "┈┊┈┊┈┊┈┊┈", "˙·˙·˙·˙·˙·", "◌◦∘·∘◦◌◦∘·∘"]

statindex = 0
loop_time = time.time()
afkvalset = False
afktime = 0
newprimary = paterns[configdata["swirlindex"]-1]
while True:
    if loop_time+2 > time.time():
        socket.recv_json()
        socket.send_json(primarydata)
        continue
    
    endstrformat = str(configdata["endstrformat"])

    loop_time = time.time()

    if endstrformat.count(r"{spotstr}"):
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
            barstr = progressbar(spotifyret["progress"], spotifyret["duration"])


    playtimestr = f"⏱️ ᴾˡᵃʸ ᵀᶦᵐᵉ {secondsToTime(time.time() - core_start)}"

    if endstrformat.count(r"{gpustatstr}"):
        gpus = get_gpu_status_no_popup()
        gpu = gpus[0]
        gpustatstr = f"ᵍᵖᵘ {int(gpu.load*50)}% ¦ ᵛʳᵃᵐ {round(gpu.memoryUsed, 1 )}/{round(gpu.memoryTotal, 1)}Gb"

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
                newprimary = paterns[configdata["swirlindex"]-1]
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


    
    if endstrformat.count(r"{swirlstr}"):
        firststr = newprimary[0]
        newprimary = newprimary.removeprefix(firststr)
        newprimary = newprimary + firststr
    

    based = str(endstrformat).replace(" ", "\n")

    based = based.replace(r"{statstr}", statstr).replace(r"{gpustatstr}", gpustatstr).replace(r"{playtimestr}", playtimestr).replace(r"{spotstr}", spotstr).replace(r"{chatbox}", chatbox).replace(r"{barstr}", barstr).replace(r"{swirlstr}", newprimary).replace(r"{timestr}", get_current_time())


    endstr = based

    #endstr = f"{statstr}\n{gpustatstr}\n{timestr}\n{spotstr}\n{chatbox}"


    client.send_message("/chatbox/input", [endstr, True, False])
    socket.send_json(primarydata)



chatpy.terminate()
chatpy.wait()

print(Fore.RESET)

with open(".timecache", "w") as file:
    json.dump({"closingtime": time.time(), "core_start": core_start}, file)

os.system("pause")
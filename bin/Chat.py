import tkinter as tk
import zmq
import threading
import time
import json
import subprocess

afk = False
current_text = ""
closing = False


with open("bin/config.json", "r", encoding="utf8") as file: 
    configdata = json.load(file)

foreground = configdata["fg"]
background = configdata["bg"]

def on_input_change(*args):
    global current_text
    current_text = entry_var.get()

def afk_toggle():
    global afk
    afk = not afk
    afkbutton.config(fg="green" if afk else "yellow")

def customwindow():
    custompy = subprocess.Popen(["python", "bin/Custom.py"])

root = tk.Tk()
root.title("Ri's Chatbox")
root.geometry("200x190")
root.config(bg=background)
root.attributes('-topmost', True) 

def on_close():
    global closing
    closing = True


label = tk.Label(root, text="Failed to Start Thread for Socket Connection...\n Contact Ri :3", fg=foreground)
label.pack(pady=10)
label.config(bg=background)


afkbutton = tk.Button(root, text="AFK", bg=background, fg=foreground, command=afk_toggle)
afkbutton.pack(pady=0)

custombutton = tk.Button(root, text="Customize", bg=background, fg=foreground, command=customwindow)
custombutton.pack()


entry_var = tk.StringVar()
entry_var.trace_add("write", on_input_change)



entry = tk.Entry(root, textvariable=entry_var, width=30)
entry.pack(pady=7)
entry.config(bg=background, fg=foreground)
root.iconbitmap("bin/icon.ico")

def zmq_thread():
    global current_text
    global afk
    global closing
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:8391")
    while True:
        socket.send_json({"client": "chat", "afk": afk, "chatboxmessage": current_text, "closing": closing})
        message = socket.recv_json()
        if closing: root.after(0, lambda: label.config(text="Ending Socket Connection..."))
        elif message["chatbox"]: root.after(0, lambda: label.config(text=message["chatbox"]))
        
        
        

threading.Thread(target=zmq_thread, daemon=True).start()


root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
import tkinter as tk
import json
from colorama import Fore
from tkinter.filedialog import askopenfilename


with open("config.json", "r", encoding="utf8") as file: 
    configdata = json.load(file)

foreground = configdata["fg"]
background = configdata["bg"]


root = tk.Tk()
root.title("Customization")
root.geometry("900x700")
root.config(bg=background)
root.attributes('-topmost', True)
root.iconbitmap(configdata["iconpath"])




def iconfileselect():
    file_types = (
    ("Icon files", "*.ico"),
    ("All files", "*.*")
    )
    
    path = askopenfilename(filetypes=file_types)
    if path:
        configdata.update({"iconpath": path})

def on_close():
    global configdata
    global format_var
    global bg_var
    global fg_var
    emojilist = []

    for e in emoji_var.get(): emojilist.append(e)
    configdata.update({"emojis": emojilist, "endstrformat": format_var.get(), "fg": fg_var.get(), "bg": bg_var.get(), "title": title_var.get()})

    with open("config.json", "w", encoding="utf8") as file:
        json.dump(configdata, file)
        print(Fore.GREEN + "[/] Dumped New Config Data")
            
    root.destroy()

def create_status_row(status):
    row = tk.Frame(root, bg=background)
    row.pack(fill="x", anchor="w", pady=2)

    label = tk.Label(row, text=status, fg=foreground, bg=background)
    label.pack(side="left", anchor="w")

    button = tk.Button(row,
        text="X",
        fg="red",
        bg=background,
        command=lambda r=row, s=status: deletecmd(r, s))
    button.pack(side="right")



def add_status():
    status = entry_var.get().strip()
    if not status:
        return

    configdata["status_messages"].append(status)
    create_status_row(status)
    entry_var.set("")


def deletecmd(row, status_text):
    row.destroy()

    configdata["status_messages"].remove(status_text)
    

for status in configdata["status_messages"]:
    row = tk.Frame(root, bg=background)
    row.pack(fill="x", anchor="w", pady=2)

    label = tk.Label(row, text=status, fg=foreground, bg=background)
    label.pack(side="left", anchor="w")

    button = tk.Button(row,
        text="X",
        fg="red",
        bg=background,
        command=lambda r=row, s=status: deletecmd(r, s))
    button.pack(side="right")



entry_var = tk.StringVar()
emoji_var = tk.StringVar()
format_var = tk.StringVar()
fg_var = tk.StringVar()
bg_var = tk.StringVar()
title_var = tk.StringVar()

fg_var.set(configdata["fg"])
bg_var.set(configdata["bg"])
title_var.set(configdata["title"])

 
format_var.set(configdata["endstrformat"])

adderrow = tk.Frame(root, bg=background)
adderrow.pack(fill="x", pady=10)


entry = tk.Entry(adderrow, textvariable=entry_var, width=30)
entry.pack(pady=7)
entry.config(bg=background, fg=foreground)

adderbutton = tk.Button(adderrow, text="Add", fg=foreground, bg=background, command=add_status)
adderbutton.pack(side="right")

formatinfo = r"""
List of all Format Vars: (Seperate by Spaces)
{statstr}: Status Bar
{gpustatstr}: GPU Stats
{timestr}: Current Playtime
{spotstr}: Spotify
{barstr}: Spotify Progress Bar
{chatbox}: The Fucking Chatbox"""

formatinfolabel = tk.Label(adderrow, text=formatinfo, bg=background, fg=foreground)
formatinfolabel.pack(anchor="w")

formatentry = tk.Entry(adderrow, textvariable=format_var, width=70)
formatentry.pack(pady=7)
formatentry.config(bg=background, fg=foreground)



emoji_var.set("".join(configdata["emojis"]).replace("️", ""))


emojientry = tk.Entry(adderrow, textvariable=emoji_var, width=30)
emojientry.pack(pady=7)
emojientry.config(bg=background, fg=foreground)

titleentry = tk.Entry(root, textvariable=title_var, width=20)
titleentry.pack(pady=3, side="right", anchor="n")
titleentry.config(bg=background, fg=foreground)

fgentry = tk.Entry(root, textvariable=fg_var, width=6)
fgentry.pack(pady=0, side="right")
fgentry.config(bg=background, fg=foreground)

bgentry = tk.Entry(root, textvariable=bg_var, width=6)
bgentry.pack(pady=0, side="right")
bgentry.config(bg=background, fg=foreground)







iconbutton = tk.Button(root, text="icon", fg=foreground, bg=background, command=iconfileselect)
iconbutton.pack(side="right", padx=2)


root.protocol("WM_DELETE_WINDOW", on_close)

print(Fore.GREEN + "[+] Customization Window Opened.")
root.mainloop()


print(Fore.RED + "[-] Customization Window Closed.")
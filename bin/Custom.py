import tkinter as tk
import json
from colorama import Fore




with open("config.json", "r", encoding="utf8") as file: 
    configdata = json.load(file)

foreground = configdata["fg"]
background = configdata["bg"]

root = tk.Tk()
root.title("Customization")
root.geometry("800x700")
root.config(bg=background)
root.attributes('-topmost', True)
root.iconbitmap("icon.ico")


def on_close():
    global configdata
    emojilist = []

    for e in emoji_var.get(): emojilist.append(e)
    configdata.update({"emojis": emojilist})

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



adderrow = tk.Frame(root, bg=background)
adderrow.pack(fill="x", pady=10)


entry = tk.Entry(adderrow, textvariable=entry_var, width=30)
entry.pack(pady=7)
entry.config(bg=background, fg=foreground)


emoji_var.set("".join(configdata["emojis"]).replace("️", ""))


emojientry = tk.Entry(adderrow, textvariable=emoji_var, width=30)
emojientry.pack(pady=7)
emojientry.config(bg=background, fg=foreground)

adderbutton = tk.Button(adderrow, text="Add", fg=foreground, bg=background, command=add_status)
adderbutton.pack(side="right")






root.protocol("WM_DELETE_WINDOW", on_close)

print(Fore.GREEN + "[+] Customization Window Opened.")
root.mainloop()


print(Fore.RED + "[-] Customization Window Closed.")
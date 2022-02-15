import io
import os
from ctypes import windll
from tkinter import *
from urllib.request import urlopen
from PIL import Image, ImageTk
import re
from json import load


class Overlay(Tk):

    def __init__(self):
        super().__init__()

        self.overlayheight = 160
        self.way = None
        self.names = None
        self.names_mem = None
        self.rank = {
            "PLAYER": {"translate": "Игрок", "color": "white"},
            "VIP": {"translate": "VIP", "color": "#00be00"},
            "PREMIUM": {"translate": "Premium", "color": "#00dada"},
            "HOLY": {"translate": "Holy", "color": "#ffba2d"},
            "IMMORTAL": {"translate": "Immortal", "color": "#e800d5"},
            "BUILDER": {"translate": "Билдер", "color": "#009c00"},
            "SRBUILDER": {"translate": "Проверенный билдер", "color": "#009c00"},
            "MAPLEAD": {"translate": "Главный билдер", "color": "#009c00"},
            "YOUTUBE": {"translate": "YouTube", "color": "#fe3f3f"},
            "DEV": {"translate": "Разработчик", "color": "#00bebe"},
            "ORGANIZER": {"translate": "Организатор", "color": "#00bebe"},
            "MODER": {"translate": "Модератор", "color": "#1b00ff"},
            "WARDEN": {"translate": "Проверенный модератор", "color": "#1b00ff"},
            "CHIEF": {"translate": "Главный модератор", "color": "#1b00ff"},
            "ADMIN": {"translate": "Главный админ", "color": "#00bebe"}
        }
        self.colormap = {'0': 'black', '1': 'blue', '2': 'green3', '3': 'green4', '4': 'cyan3', '5': 'magenta3',
                         '6': 'orange', '7': 'gray65', '8': 'gray35', '9': 'royal blue', 'a': 'lawn green',
                         'b': 'cyan2', 'c': 'tomato', 'd': 'orchid2', 'e': 'yellow', 'f': 'white'}

        self.GWL_EXSTYLE = -20
        self.WS_EX_APPWINDOW = 0x00040000
        self.WS_EX_TOOLWINDOW = 0x00000080

        self.overrideredirect(True)
        self.wm_attributes("-transparentcolor", "#fffff1")
        self.attributes("-topmost", True)
        self.config(bg="#fffff1")
        self.resizable(width=False, height=False)
        self.title("RaidOverlay v0.1")

        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        self.changePositionFrame = Frame(self, width=185, height=14, bg="gray10")
        self.changePositionFrame.pack_propagate(False)
        self.changePositionFrame.pack()
        self.changePositionFrame.text = Label(self.changePositionFrame, bg="gray13",
                                              text=f"Tab in chat to get nicknames",
                                              fg="snow", font=("TkDefaultFont", 10, "bold"))
        self.changePositionFrame.text.pack(side=LEFT)

        for bind in [self.changePositionFrame, self.changePositionFrame.text]:
            bind.bind("<Button-1>", self.start_move)
            bind.bind("<ButtonRelease-1>", self.stop_move)
            bind.bind("<B1-Motion>", self.moving)
            bind.bind("<Map>", self.frame_mapped)

        self.after(10, self.overlay)

        self.after(10, self.set_appwindow)
        self.mainloop()

    def overlay(self):
        with open(os.getenv("APPDATA") + "\.vimeworld\minigames\logs\latest.log", "r", encoding='utf-8') as file:
            file = file.readlines()[-1][39:].strip()
            if self.names != file.split(", ") and not bool(re.search('[а-яА-Я\[<.!:;/#]', file)):
                self.names = file.split(", ")
                del file

                try:
                    self.overlayFrame.destroy()
                except:
                    pass
                self.overlayFrame = Frame(self, width=42, height=130, bg="#fffff1")
                self.overlayFrame.pack_propagate(False)
                self.overlayFrame.pack()

                self.names_mem = []
                path = ""
                for i in range(len(self.names)):
                    path += self.names[i] + ","
                    if i % 49 == 0 or i == len(self.names) - 1:
                        self.names_mem += load(urlopen(f"https://api.vimeworld.ru/user/name/{path}"))
                        path = ""

                self.images = []

                try:
                    self.changePositionFrame.text.destroy()
                except:
                    pass

                self.changePositionFrame.text = Label(self.changePositionFrame, bg="gray13",
                                                      text=f"0/{len(self.names)}",
                                                      fg="snow", font=("TkDefaultFont", 10, "bold"))
                self.changePositionFrame.text.pack(side=LEFT)

                for j in range(0, len(self.names), 6):
                    self.images.append([])
                    self.overlayFrame.line = Frame(self.overlayFrame, width=42 * 6, height=60, bg="#fffff1")
                    self.overlayFrame.line.pack(side=TOP)

                    for i in range(6):
                        if j + i == len(self.names):
                            break
                        self.changePositionFrame.text.config(text=f"{j + i + 1}/{len(self.names)}")
                        self.update()
                        self.update_idletasks()
                        self.overlayheight += 60
                        self.overlayFrame.config(height=self.overlayheight)
                        image_byt = urlopen(f"https://skin.vimeworld.ru/head/{self.names[j + i]}/35.png").read()
                        image_b64 = Image.open(io.BytesIO(image_byt))

                        self.images[j // 6].append([])
                        self.images[j // 6][i] = ImageTk.PhotoImage(image_b64, master=self)
                        self.overlayFrame.line.player = Label(self.overlayFrame.line, bg="#fffff1",
                                                              image=self.images[j // 6][i])
                        self.overlayFrame.line.player.pack(side=LEFT, pady=2, padx=2)
                        self.overlayFrame.line.player.bind("<Enter>", self.on_enter)
                        self.overlayFrame.line.player.bind("<Leave>", self.on_leave)

                        if j == 0:
                            self.changePositionFrame.config(width=42.3 * len(self.overlayFrame.line.winfo_children()))
                            self.overlayFrame.config(width=42.3 * len(self.overlayFrame.line.winfo_children()))
                            self.overlayFrame.line.config(width=42.3 * len(self.overlayFrame.line.winfo_children()))

        self.after(500, lambda: self.overlay())

    def get_time(self, time):
        cut = {"day": [86400, "д."],
               "hour": [3600, "ч."],
               "min": [60, "м."]}
        text = ""
        for i in cut:
            text += f"{time // cut[i][0]} {cut[i][1]} "
            time = time % cut[i][0]
        return text

    # Make Icon in taskbar
    def set_appwindow(self):
        hwnd = windll.user32.GetParent(self.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, self.GWL_EXSTYLE)
        style = style & ~self.WS_EX_TOOLWINDOW
        style = style | self.WS_EX_APPWINDOW
        windll.user32.SetWindowLongW(hwnd, self.GWL_EXSTYLE, style)

        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())

    # Moving part
    def start_move(self, event):
        global x, y
        x = event.x
        y = event.y

    def stop_move(self, event):
        global x, y
        x = None
        y = None

    def moving(self, event):
        global x, y
        x_ = (event.x_root - x)
        y_ = (event.y_root - y)
        self.geometry("+%s+%s" % (x_, y_))

    def frame_mapped(self, e):
        self.update_idletasks()
        self.overrideredirect(True)
        self.state('normal')

    # Player menu
    def on_enter(self, e):
        if "!toplevel" in e.widget.winfo_name() or "!toplevel" in e.widget.winfo_parent():
            return
        else:
            if self.way is not None:
                for e.widget in self.winfo_children():
                    if isinstance(e.widget, Toplevel):
                        e.widget.destroy()
                        self.way = None
                        return

            self.way = e.widget

            self.menu = Toplevel(self)
            self.menu.overrideredirect(True)
            self.menu.attributes("-topmost", True)
            self.menu.resizable(width=False, height=False)
            self.config(bg="gray13")
            self.menu.frame = Frame(self.menu, width=200, height=220, bg="gray13")
            self.menu.frame.pack()

            label = e.widget.winfo_name()
            parent = e.widget.winfo_parent()
            player = 0 if label == "!label" else int(label.split("!label")[-1]) - 1
            player = player if parent.split(".!frame")[-1] == "" else player + 6 * (
                    int(parent.split(".!frame")[-1]) - 1)

            user_rank = self.rank.get(self.names_mem[player].get("rank"))
            user = self.names_mem[player]
            guild = user.get("guild")

            self.menu.user = Frame(self.menu.frame, width=180, height=22, bg=user_rank.get("color"), bd=2)
            self.menu.user.pack(side=TOP, padx=5, pady=5)
            # NICKNAME FRAME
            self.menu.user_frame = Frame(self.menu.user, width=180, height=22, bg="gray13")
            self.menu.user_frame.pack_propagate(False)
            self.menu.user_frame.pack(side=TOP)
            self.menu.user_frame_center = Frame(self.menu.user_frame, width=180, height=22, bg="gray13")
            self.menu.user_frame_center.pack(side=TOP)
            self.menu.user_frame.rank = Label(self.menu.user_frame_center, bg="gray13", text=user_rank.get("translate"),
                                              fg=user_rank.get("color"), font=("TkDefaultFont", 10, "bold"))
            self.menu.user_frame.rank.pack(side=LEFT, pady=3)
            self.menu.user_frame.nickname = Label(self.menu.user_frame_center, bg="gray13", text=user.get("username"),
                                                  fg="snow", font=("TkDefaultFont", 10, "bold"))
            self.menu.user_frame.nickname.pack(side=LEFT, pady=3)

            # ID FRAME
            self.menu.user_id_frame = Frame(self.menu.user, width=180, height=22, bg="gray13")
            self.menu.user_id_frame.pack_propagate(False)
            self.menu.user_id_frame.pack(side=TOP)
            self.menu.user_id_frame.id = Label(self.menu.user_id_frame, bg="gray13", text=f'ID: {user.get("id")}',
                                               fg="snow", font=("TkDefaultFont", 10, "bold"))
            self.menu.user_id_frame.id.pack(side=LEFT, pady=3)

            # LEVEL
            self.menu.user_level_frame = Frame(self.menu.user, width=180, height=22, bg="gray13")
            self.menu.user_level_frame.pack_propagate(False)
            self.menu.user_level_frame.pack()
            self.menu.user_level_frame.level = Label(self.menu.user_level_frame, bg="gray13",
                                                     text=f'LEVEL: {user.get("level")} [{int(user.get("levelPercentage") * 100)}%]',
                                                     fg="snow", font=("TkDefaultFont", 10, "bold"))
            self.menu.user_level_frame.level.pack(side=LEFT, pady=3)

            # PLAYED
            self.menu.user_played_time_frame = Frame(self.menu.user, width=180, height=22, bg="gray13")
            self.menu.user_played_time_frame.pack_propagate(False)
            self.menu.user_played_time_frame.pack()
            self.menu.user_played_time_frame.playedSeconds = Label(self.menu.user_played_time_frame, bg="gray13",
                                                                   text=f'PLAYED: {self.get_time(user.get("playedSeconds"))}',
                                                                   fg="snow", font=("TkDefaultFont", 10, "bold"))
            self.menu.user_played_time_frame.playedSeconds.pack(side=LEFT, pady=3)

            if user.get("guild") is not None:
                self.menu.guild = Frame(self.menu.frame, width=180, height=22,
                                        bg=self.colormap.get(guild.get("color")[1:]), bd=2)
                self.menu.guild.pack(side=TOP, padx=5, pady=5)

                # GUILD FRAME
                self.menu.guild_frame = Frame(self.menu.guild, width=180, height=22, bg="gray13")
                self.menu.guild_frame.pack_propagate(False)
                self.menu.guild_frame.pack(side=TOP)

                tag = ""
                if user.get("guild").get("tag") is not None:
                    tag = f'<{user.get("guild").get("tag")}> '
                self.menu.guild_frame.name = Label(self.menu.guild_frame, bg="gray13",
                                                   text=f'{tag}{user.get("guild").get("name")}',
                                                   fg=self.colormap.get(guild.get("color")[1:]),
                                                   font=("TkDefaultFont", 10, "bold"))
                self.menu.guild_frame.name.pack(side=TOP, pady=3)

                # ID FRAME
                self.menu.guild_id_frame = Frame(self.menu.guild, width=180, height=22, bg="gray13")
                self.menu.guild_id_frame.pack_propagate(False)
                self.menu.guild_id_frame.pack(side=TOP)
                self.menu.guild_id_frame.id = Label(self.menu.guild_id_frame, bg="gray13",
                                                    text=f'ID: {guild.get("id")}',
                                                    fg="snow", font=("TkDefaultFont", 10, "bold"))
                self.menu.guild_id_frame.id.pack(side=LEFT, pady=3)

                # LEVEL
                self.menu.guild_level_frame = Frame(self.menu.guild, width=180, height=22, bg="gray13")
                self.menu.guild_level_frame.pack_propagate(False)
                self.menu.guild_level_frame.pack()
                self.menu.guild_level_frame.level = Label(self.menu.guild_level_frame, bg="gray13",
                                                          text=f'LEVEL: {guild.get("level")} [{int(guild.get("levelPercentage") * 100)}%]',
                                                          fg="snow", font=("TkDefaultFont", 10, "bold"))
                self.menu.guild_level_frame.level.pack(side=LEFT, pady=3)

            widget_x, widget_y = e.widget.winfo_rootx(), e.widget.winfo_rooty()
            self.menu.geometry("+%s+%s" % (widget_x, widget_y))
            self.menu.bind("<Enter>", self.on_enter)
            self.menu.bind("<Leave>", self.on_leave)

    def on_leave(self, e):
        if "label" not in e.widget.winfo_name() and "!frame" not in e.widget.winfo_parent():
            for e.widget in self.winfo_children():
                if isinstance(e.widget, Toplevel):
                    e.widget.destroy()
                    self.way = None

    # Exit part :)

    def exit(self):
        self.destroy()


if __name__ == '__main__':
    Overlay()

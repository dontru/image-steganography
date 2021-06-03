import os
import sys
import hashlib
import random
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from ctypes import windll
from PIL import Image, ImageTk


class Settings:
    def __init__(self):
        self.title = "Image encryption"
        self.resizable = {"width": False, "height": False}
        self.bg_color = "#202020"  # "#224466"
        self.fg_color = "#eeffff"

        self.title_bar_height = 2
        self.title_bar_bg_color = "#222222"
        self.exit_symbol = "×"
        self.title_bar_relief = tk.FLAT

        self.text_width = 80
        self.text_height = 24
        self.text_border = 12
        self.text_bg_color = "#353a3f"  # 1e2124
        self.text_cursor_color = "#bbcccc"
        self.text_relief = tk.FLAT

        self.image_text = "UPLOAD IMAGE"
        self.image_height = 10
        self.image_bg_color = "#2e3030"

        self.password_border = 10
        self.password_bg_color = "#202020"
        self.password_relief = tk.FLAT

        self.buttons_border = 8
        self.button_width = 15
        self.button_border = 0
        self.button_bg_color = "#292929"
        self.button_fg_color = "#cccccc"
        self.button_padx = 1

        self.title_bar_config = {"title": self.title, "height": self.title_bar_height, "bg": self.title_bar_bg_color, "fg": self.fg_color,
                                 "exit_symbol": self.exit_symbol, "exit_relief": self.title_bar_relief}
        self.text_config = {"width": self.text_width, "height": self.text_height,
                            "bg": self.text_bg_color, "fg": self.fg_color,
                            "bd": self.text_border, "relief": self.text_relief,
                            "insertbackground": self.text_cursor_color, "placeholder": "Text to encrypt", "placeholder_fg": "#606060"}
        self.image_config = {"text": self.image_text, "width": 244, "height": 148,
                             "bg": self.image_bg_color, "fg": self.fg_color, "compound": tk.CENTER}
        self.password_config = {"bg": self.password_bg_color, "fg": self.fg_color,
                                "bd": self.password_border, "relief": self.password_relief,
                                "insertbackground": self.fg_color, "placeholder": "Password", "placeholder_fg": "#606060"}
        self.buttons_config = {"bg": self.password_bg_color, "bd": self.buttons_border,
                               "button_width": self.button_width, "button_bd": self.button_border,
                               "button_bg": self.button_bg_color, "button_fg": self.button_fg_color,
                               "button_padx": self.button_padx}
        self.option_config = {"bg": self.bg_color, "fg": self.fg_color, "text": "safe mode"}


class Tk(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

    def center(self):
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width/2) - (width/2))
        y = int((screen_height/2) - (height/2))
        self.geometry("+{0}+{1}".format(x, y))

    def minimize(self):
        self.after(10, self.overrideredirect(False))
        self.after(20, self.wm_state("iconic"))
        self.after(30, lambda: self.bind("<Map>", self.restore))

    def restore(self, event):
        self.unbind("<Map>")
        self.after(30, lambda: self.overrideredirect(True))
        self.after(40, lambda: self.set_appwindow())

    def set_appwindow(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = windll.user32.GetParent(self.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        # re-assert the new window style
        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())  # wm_deiconify


class Button(tk.Button):
    def __init__(self, parent, **options):
        hover_bg = options.pop("hover_bg")
        tk.Button.__init__(self, parent, **options)
        self.bind("<Enter>", lambda event: self.config(bg=hover_bg))
        self.bind("<Leave>", lambda event: self.config(bg=options["bg"]))


class TitleBar(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text=options["title"], height=options["height"],
                              bg=options["bg"], fg=options["fg"])

        self.exit_button = Button(self, text=options["exit_symbol"], width=options["height"] * 2,
                                  bg=options["bg"], fg=options["fg"], activebackground="#bb3333",  # options["bg"],
                                  activeforeground=options["fg"],
                                  command=sys.exit, relief=options["exit_relief"], bd=0, hover_bg="#aa2222")

        self.min_button = Button(self, text="_", width=options["height"] * 2,
                                 bg=options["bg"], fg=options["fg"], activebackground="#2f3333",
                                 activeforeground=options["fg"],
                                 command=parent.minimize, relief=options["exit_relief"], bd=0, hover_bg="#2f3333")

        self.root = parent
        self.x = 0
        self.y = 0
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<ButtonRelease-1>", self.stop_move)
        self.label.bind("<B1-Motion>", self.on_motion)

        self.exit_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.min_button.pack(side=tk.RIGHT, fill=tk.Y)
        self.label.pack(fill=tk.X)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = 0
        self.y = 0

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry("+{0}+{1}".format(x, y))


class PlaceholderWidget:
    def __init__(self, **options):
        self.__fg = options["fg"]
        self.__placeholder = options["placeholder"]
        self.__placeholder_fg = options["placeholder_fg"]
        self.bind("<FocusOut>", lambda event: self.on_focus_out() if self.is_empty() else None)
        self.on_focus_out()

    def on_focus(self, *args):
        self.unbind("<Button-1>")
        self.unbind("<FocusIn>")
        self.config(fg=self.__fg)
        self.set("")

    def on_focus_out(self, *args):
        self.bind("<Button-1>", self.on_focus)
        self.bind("<FocusIn>", self.on_focus)
        self.config(fg=self.__placeholder_fg)
        self.set(self.__placeholder)

    def is_empty(self):
        text = self.get()
        if len(text) == 0 or text == "\n":
            return True
        else:
            return False


class PasswordWidget(PlaceholderWidget):
    def __init__(self, **options):
        PlaceholderWidget.__init__(self, **options)
        self.__show = "●"

    def on_focus(self, *args):
        PlaceholderWidget.on_focus(self, *args)
        self.config(show=self.__show)

    def on_focus_out(self, *args):
        PlaceholderWidget.on_focus_out(self, *args)
        self.config(show="")


class PopUpMenuWidget:
    def __init__(self):
        self.bind("<Button-3>", self.do_popup)
        self.popup = tk.Menu(self, tearoff=0)
        self.popup.add_command(label="Cut", command=lambda: self.event_generate("<<Cut>>"))
        self.popup.add_command(label="Copy", command=lambda: self.event_generate("<<Copy>>"))
        self.popup.add_command(label="Paste", command=lambda: self.event_generate("<<Paste>>"))

    def do_popup(self, event):
        try:
            self.popup.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup.grab_release()


class CypherText(tk.Text, PlaceholderWidget, PopUpMenuWidget):
    def __init__(self, parent, **options):
        p_text = options.pop("placeholder")
        p_fg_color = options.pop("placeholder_fg")
        tk.Text.__init__(self, parent, **options)
        PlaceholderWidget.__init__(self, fg=options["fg"], placeholder=p_text, placeholder_fg=p_fg_color)
        PopUpMenuWidget.__init__(self)

    def get(self, *args):
        return tk.Text.get(self, "1.0", tk.END)

    def set(self, x):
        self.delete("1.0", tk.END)
        self.insert("1.0", x)


class TextFrame(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self)
        self.scrollbar = tk.Scrollbar(self)
        self.text = CypherText(self, **options)

        self.scrollbar.config(command=self.text.yview)

        # self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack()


class ImageLabel(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self, parent, width=options.pop("width"), height=options.pop("height"))
        self.pack_propagate(False)
        self.label = tk.Label(self, **options)
        self.label.pack(fill=tk.BOTH, expand=True)
        self.origin_path = None
        self.image = None
        self.displayed_image = None
        self.darken_image = None
        self.label.bind("<Button-1>", self.load_image)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def load_image(self, *args):
        try:
            self.origin_path = filedialog.askopenfilename()
            self.image = Image.open(self.origin_path)
            image_width, image_height = self.image.size
            image_ratio = image_width / image_height
            if image_ratio <= 1:
                proportion = self.winfo_height() / image_height
            else:
                proportion = self.winfo_width() / image_width
            new_size = (int(image_width * proportion), int(image_height * proportion))
            resized_image = self.image.resize(new_size, Image.ANTIALIAS)
            self.displayed_image = ImageTk.PhotoImage(resized_image)
            self.label.config(text="", image=self.displayed_image)
            darken = self.image.point(lambda p: p * 0.5)
            darken_resized = darken.resize(new_size, Image.ANTIALIAS)
            self.darken_image = ImageTk.PhotoImage(darken_resized)
        except AttributeError:
            pass
        except OSError:
            messagebox.showerror("File error", "Cannot identify image file")
        except ZeroDivisionError:
            messagebox.showerror("File error", "Empty image")

    def on_enter(self, *args):
        if self.image:
            self.label.config(text="UPLOAD DIFFERENT IMAGE", image=self.darken_image)

    def on_leave(self, *args):
        if self.image:
            self.label.config(text="", image=self.displayed_image)


class PasswordEntry(tk.Entry, PasswordWidget):
    def __init__(self, parent, **options):
        p_text = options.pop("placeholder")
        p_fg_color = options.pop("placeholder_fg")
        self.__password = tk.StringVar()
        tk.Entry.__init__(self, parent, **options, textvariable=self.__password)
        PasswordWidget.__init__(self, fg=options["fg"], placeholder=p_text, placeholder_fg=p_fg_color)

    def get(self):
        return self.__password.get()

    def set(self, x):
        self.__password.set(x)


class MainButtons(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self, parent, bg=options["bg"], bd=options["bd"])
        self.encrypt_button = Button(self, text="Encrypt", width=options["button_width"], bd=options["button_bd"],
                                        bg=options["button_bg"], fg=options["button_fg"], hover_bg="#303030")
        self.decrypt_button = Button(self, text="Decrypt", width=options["button_width"], bd=options["button_bd"],
                                        bg=options["button_bg"], fg=options["button_fg"], hover_bg="#303030")
        self.encrypt_button.pack(side=tk.LEFT, padx=options["button_padx"])
        self.decrypt_button.pack(padx=options["button_padx"])

    def encrypt_button_listener(self, coder, text_widget, password_widget, image_widget):
        self.encrypt_button.config(command=lambda: coder.encrypt(text_widget.get(),
                                                                 password_widget.get(),
                                                                 image_widget))

    def decrypt_button_listener(self, coder, text_widget, password_widget, image_widget):
        self.decrypt_button.config(command=lambda: coder.decrypt(text_widget,
                                                                 password_widget.get(),
                                                                 image_widget.image))


class Option(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self, parent, bg="green")
        self.__value = tk.BooleanVar(self, False)
        checkbutton = tk.Checkbutton(self, bg=options["bg"], activebackground=options["bg"], variable=self.__value)
        label = tk.Label(self, text=options["text"], bg=options["bg"], fg=options["fg"])
        label.bind("<Button-1>", self.invoke)
        checkbutton.pack(side=tk.LEFT)
        label.pack(anchor=tk.W, pady=2)

    def invoke(self, *args):
        if not self.__value.get():
            self.__value.set(True)
        else:
            self.__value.set(False)


class OptionBar(tk.Frame):
    pass


class Coder:
    def __init__(self):
        pass

    def get_pixel_order(self, password, image):
        width, height = image.size
        items = list(range(3 * width * height))
        seed = hashlib.sha256(bytes(password, encoding="utf-8")).hexdigest()
        random.seed(seed)
        random.shuffle(items)
        random.seed()
        return items

    def encrypt(self, message, password, image_widget):
        image = image_widget.image
        if image is None:
            return

        pixels_order = self.get_pixel_order(password, image)

        if message[-1] == "\n":
            message = message[:-1]
        message += "\0"

        width, height = image.size
        max_length= int(3 * width * height / 8)
        if len(message) > max_length:
            print(messagebox.askyesno("Title", "asdf"))

        pixels = image.load()
        byte_index = 0
        for character in message:
            binary_character = "{0:08b}".format(ord(character))
            for binary in binary_character:
                item = pixels_order[byte_index]
                x = int(item / 3) % width
                y = int(int(item / 3) / width)
                color = item % 3
                edit_pixel = image.getpixel((x, y))
                edit_color = edit_pixel[color]
                byte_to_encrypt = int(binary)
                if edit_color % 2 != byte_to_encrypt:
                    changed_pixel = list(edit_pixel)
                    if changed_pixel[color] == 0:
                        changed_pixel[color] += 1
                    elif changed_pixel[color] == 255:
                        changed_pixel[color] -= 1
                    else:
                        changed_pixel[color] += [-1, 1][random.randint(0, 1)]
                    pixels[x, y] = tuple(changed_pixel)
                byte_index += 1

        origin_path = image_widget.origin_path
        ctime = os.path.getctime(origin_path)
        mtime = os.path.getmtime(origin_path)
        atime = os.path.getatime(origin_path)

        filename = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG", ".png"), ("BMP", ".bmp")],
                                                initialfile="link_to_initial_file.png")  # title="Save As"
        try:
            image.save(filename)
            powershell_commands = ["powershell.exe",
                                   "$file = Get-Item " + filename + "\n",
                                   "$origin = New-Object -Type DateTime -ArgumentList 1970, 1, 1, 2, 0, 0, 0\n",
                                   "$file.CreationTime = $origin.AddSeconds(" + str(ctime) + ")\n",
                                   "$file.LastWriteTime = $origin.AddSeconds(" + str(mtime) + ")\n",
                                   "$file.LastAccessTime = $origin.AddSeconds(" + str(atime) + ")\n", ]
            subprocess.call(powershell_commands)
        except ValueError:
            pass

    def decrypt(self, text_widget, password, image):
        if image is None:
            return

        pixels_order = self.get_pixel_order(password, image)

        letters = []
        width, height = image.size
        byte_index = 0
        while True:
            letter_bytes = []
            for i in range(8):
                x = int(pixels_order[byte_index + i] / 3) % width
                y = int(int(pixels_order[byte_index + i] / 3) / width)
                color = pixels_order[byte_index + i] % 3
                pixel = image.getpixel((x, y))
                selected_color = pixel[color]
                letter_bytes.append(selected_color % 2)
            letter = chr(int("".join(str(v) for v in letter_bytes), 2))
            letters.append(letter)
            byte_index += 8
            if letter == "\0":
                break

        text_widget.on_focus()
        text_widget.set("".join(letters[:-1]))


if __name__ == '__main__':
    settings = Settings()
    coder = Coder()
    root = Tk()
    title_bar = TitleBar(root, **settings.title_bar_config)
    text_frame = TextFrame(root, **settings.text_config)
    image = ImageLabel(root, **settings.image_config)
    password = PasswordEntry(root, **settings.password_config)
    buttons = MainButtons(root, **settings.buttons_config)
    safe_mode_option = Option(root, **settings.option_config)

    buttons.encrypt_button_listener(coder, text_frame.text, password, image)
    buttons.decrypt_button_listener(coder, text_frame.text, password, image)

    title_bar.pack(fill=tk.X)
    # text.pack(side=tk.RIGHT)
    text_frame.pack(side=tk.RIGHT)
    image.pack()
    password.pack(fill=tk.X)
    buttons.pack()
    # safe_mode_option.pack(anchor=tk.W)

    # root.bind("<Key>", lambda x: print("asfd"))

    root.wm_title(settings.title)
    root.resizable(**settings.resizable)
    root.config(bg=settings.bg_color)
    root.overrideredirect(True)
    root.after(10, lambda: root.set_appwindow())
    root.update_idletasks()
    root.center()
    root.mainloop()

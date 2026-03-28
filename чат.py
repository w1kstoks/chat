from customtkinter import *
from socket import *
from threading import Thread


class MainWindow(CTk):
    def __init__(self, name, sock: socket):
        super().__init__()
        self.name = name
        self.socket = sock

        self.geometry('800x600')
        self.title('LogiTalk')

        # CTkOptionMenu, CTkButton (2 штуки), CTkScrollableFrame, CtkEntry
        self.btn_send = CTkButton(self, width=50, height=40, text='✈', command=self.send_message)

        self.btn_open = CTkButton(self, width=50, height=40, text='📁')

        self.chat_field = CTkScrollableFrame(self)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення')
        self.message_entry.bind('<Return>', self.send_message)

        self.theme_change = CTkOptionMenu(self, width=150, values=['Системна', 'Світла', 'Темна'],
                                          command=self.change_theme_colors)

        self.btn_send.place(x=0, y=0)
        self.btn_open.place(x=0, y=0)
        self.chat_field.place(x=0, y=0)
        self.message_entry.place(x=0, y=0)
        self.theme_change.place(x=0, y=0)

        self.adaptive_ui()
        try:
            hello = f'TEXT@{self.name}@Підключився до чату\n'
            self.socket.sendall(hello.encode())
            Thread(target=self.receive_message, daemon=True).start()
        except:
            pass

    def change_theme_colors(self, value):
        if value == 'Системна':
            set_appearance_mode('system')
        elif value == 'Світла':
            set_appearance_mode('light')
        elif value == 'Темна':
            set_appearance_mode('dark')

    def adaptive_ui(self):
        ww = self.winfo_width()
        wh = self.winfo_height()

        self.chat_field.configure(width=ww - 20, height=wh - 50)

        self.btn_send.place(x=ww - 50, y=wh - 40)
        self.btn_open.place(x=ww - 105, y=wh - 40)
        self.message_entry.configure(width=ww - 110, height=40)
        self.message_entry.place(x=0, y=wh - 40)

        self.after(100, self.adaptive_ui)

    def add_message(self, message, img=None, sender=0):
        message_frame = CTkFrame(self.chat_field)
        if sender:
            message_frame.pack(pady=5, padx=5, anchor='w')
            message_frame.configure(fg_color="#636363")
        else:
            message_frame.pack(pady=5, padx=5, anchor='e')
            message_frame.configure(fg_color="#2B2EE0")

        w_size = min(500, self.winfo_width() - 20)

        if not img:
            CTkLabel(message_frame, text=message, text_color='#fff', justify='left', wraplength=w_size).pack(padx=10,
                                                                                                             pady=5)
        else:
            CTkLabel(message_frame, text=message, text_color='#fff', justify='left', wraplength=w_size, image=img,
                     compound='top').pack(padx=10, pady=5)

    def send_message(self, e=None):
        message = self.message_entry.get()
        if message and message != '':
            self.add_message(message)
            data = f'TEXT@{self.name}@{message}\n'  # TEXT@Dmytro@Привіт\n
            try:
                self.socket.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, 'end')

    def receive_message(self):
        buffer = ''
        while True:
            try:
                message = self.socket.recv(32000)
                buffer += message.decode('utf-8', errors='igrone')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break
        self.socket.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@', 3)  # TEXT@Dmytro@Привіт -> ['TEXT','Dmytro','Привіт']
        ms_type = parts[0]  # тип повідомлення 'TEXT'
        if ms_type == 'TEXT':
            if len(parts) >= 3:
                self.add_message(f'{parts[1]}: {parts[2]}', sender=1)


if __name__ == "__main__":
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('5.tcp.eu.ngrok.io',11549))
        app = MainWindow("User", client_socket)
    except:
        print("Не вдалося підключитися до сервера")
        app = MainWindow("vova", None)

    app.mainloop()


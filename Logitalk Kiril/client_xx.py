from customtkinter import *
from socket import *
from threading import Thread
from tkinter.messagebox import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('650x400')
        self.title('Онлайн-чат')

        # Прапор і параметри меню
        self.is_show_menu = False
        self.frame_width = 0
        self.frame_speed = 20

        self.frame = CTkFrame(self, width=0, height=400)
        self.frame.place(x=0, y=0)
        self.frame.pack_propagate(False)

        # ---Кнопка виклику меню---
        self.btn = CTkButton(self, text='Меню', width=50, command=self.toggle_show_menu)
        self.btn.place(x=10, y=5)

        # ---Елементи меню---
        self.label = CTkLabel(self.frame, text='Налаштування:')
        self.label.pack(pady=20)

        self.name_entry = CTkEntry(self.frame, placeholder_text="Ім'я/нікнейм")
        self.name_entry.pack(pady=5)

        self.signup_btn = CTkButton(self.frame, text='Зареєструватися', command=self.sign_up)
        self.signup_btn.pack(pady=5)

        self.signout_btn = CTkButton(self.frame, text='Вийти з чату', command=self.sign_out)
        self.signout_btn.pack(pady=5)

        self.clear_btn = CTkButton(self.frame, text='Очистити чат', command=self.clear_chat)
        self.clear_btn.pack(pady=5)

        self.theme = CTkOptionMenu(self.frame,
                                   values=['Темна тема', 'Світла тема'],
                                   command=self.change_theme)
        self.theme.pack(pady=5)

        # ---Пошук по історії---
        self.search_entry = CTkEntry(self, placeholder_text='🔍 Пошук по історії', width=250)
        self.search_entry.place(x=80, y=5)
        self.search_entry.bind('<KeyRelease>', self.search_in_chat)

        # ---Список користувачів---
        self.users_frame = CTkFrame(self, width=150, height=360)
        self.users_frame.place(x=500, y=30)
        self.users_label = CTkLabel(self.users_frame, text='Активні користувачі:')
        self.users_label.pack(pady=5)
        self.users_list = CTkTextbox(self.users_frame, width=140, height=330, state='disabled')
        self.users_list.pack(padx=5)
        self.active_users = set()

        # ---Вікно чату---
        self.chat_text = CTkTextbox(self, state='disabled', wrap='word', width=480, height=290)
        self.chat_text.place(x=0, y=30)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення', width=400)
        self.message_entry.place(x=0, y=340)
        self.message_entry.bind('<Return>', lambda event: self.send_message())

        self.send_button = CTkButton(self, text='>>', width=40, height=30, command=self.send_message)
        self.send_button.place(x=400, y=340)

        # ---Статус---
        self.status_bar = CTkLabel(self, text="Не авторизований")
        self.status_bar.place(x=340, y=5)

        self.connection_label = CTkLabel(self, text="●", text_color="red")
        self.connection_label.place(x=620, y=5)

        self.username = ''

        # ---Теги форматування---
        self.chat_text.tag_config("system", foreground="gray")
        self.chat_text.tag_config("my_message", foreground="blue")
        self.chat_text.tag_config("other_message", foreground="black")

        # ---Підключення до сервера---
        try:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            t = Thread(target=self.recv_message, daemon=True)
            t.start()
            self.check_connection()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися: {e}")

    # ---Меню (анімація)---
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.hide_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        if self.frame_width < 200:
            self.frame_width += self.frame_speed
            self.frame.configure(width=self.frame_width)
            self.after(10, self.show_menu)
        else:
            # Когда меню полностью выехало, сдвигаем чат
            self.chat_text.place(x=200, y=30)
            self.message_entry.place(x=200, y=340)
            self.send_button.place(x=600, y=340)

    def hide_menu(self):
        if self.frame_width > 0:
            self.frame_width -= self.frame_speed
            self.frame.configure(width=self.frame_width)
            self.after(10, self.hide_menu)
        else:
            # Когда меню скрыто — возвращаем чат обратно
            self.chat_text.place(x=0, y=30)
            self.message_entry.place(x=0, y=340)
            self.send_button.place(x=400, y=340)


    # ---Реєстрація---
    def sign_up(self):
        username = self.name_entry.get().strip()
        if not username:
            showerror('ПОМИЛКА!', 'Поле імені порожнє!')
            return
        if len(username) < 2:
            showerror('ПОМИЛКА!', 'Ім\'я занадто коротке!')
            return
        if len(username) > 20:
            showerror('ПОМИЛКА!', 'Ім\'я занадто довге!')
            return

        try:
            self.username = username
            hello = f'{self.username} приєднується'
            self.client_socket.sendall(hello.encode())
            self.name_entry.configure(state='disabled')
            self.signup_btn.configure(state='disabled')
            self.status_bar.configure(text=f"Авторизований як: {self.username}")
            self.add_message(f'Нікнейм: {self.username}', "system")
            self.add_user(username)
        except Exception as e:
            self.add_message(str(e), "system")

    # ---Вихід---
    def sign_out(self):
        try:
            if hasattr(self, 'client_socket') and self.username:
                goodbye = f'{self.username} покидає чат'
                self.client_socket.sendall(goodbye.encode())
                self.remove_user(self.username)
        except:
            pass
        finally:
            self.username = ''
            self.name_entry.configure(state='normal')
            self.signup_btn.configure(state='normal')
            self.status_bar.configure(text="Не авторизований")
            self.add_message("Ви вийшли з чату", "system")

    # ---Надсилання---
    def send_message(self):
        if not self.username:
            showerror('ПОМИЛКА!', 'Спочатку зареєструйтеся!')
            return
        message = self.message_entry.get().strip()
        if message:
            text = f'{self.username}: {message}'
            try:
                self.client_socket.sendall(text.encode())
                display_text = text.replace(f'{self.username}', 'Я')
                self.add_message(display_text, "my_message")
            except Exception as e:
                self.add_message(f"Помилка: {e}", "system")
        self.message_entry.delete(0, END)

    # ---Додавання повідомлення---
    def add_message(self, text, tag="other_message"):
        self.chat_text.configure(state='normal')
        if tag == "other_message":
            if 'приєднується' in text or 'покидає' in text:
                tag = "system"
        self.chat_text.insert(END, text + '\n', tag)
        self.chat_text.configure(state='disabled')
        self.chat_text.see(END)
        self.update_users_from_system_message(text)

    def recv_message(self):
        while True:
            try:
                message = self.client_socket.recv(4096).decode().strip()
                if not message:
                    self.add_message("З'єднання розірвано", "system")
                    self.connection_label.configure(text_color="red")
                    break
                self.add_message(message)
            except:
                self.add_message("З'єднання розірвано", "system")
                self.connection_label.configure(text_color="red")
                break

    # ---Пошук по історії---
    def search_in_chat(self, event=None):
        term = self.search_entry.get().lower()
        content = self.chat_text.get("1.0", END).lower()
        self.chat_text.tag_remove("highlight", "1.0", END)
        if term:
            idx = "1.0"
            while True:
                idx = self.chat_text.search(term, idx, nocase=True, stopindex=END)
                if not idx:
                    break
                end_idx = f"{idx}+{len(term)}c"
                self.chat_text.tag_add("highlight", idx, end_idx)
                idx = end_idx
            self.chat_text.tag_config("highlight", background="yellow", foreground="black")

    # ---Активні користувачі---
    def add_user(self, name):
        self.active_users.add(name)
        self.refresh_users()

    def remove_user(self, name):
        self.active_users.discard(name)
        self.refresh_users()

    def refresh_users(self):
        self.users_list.configure(state='normal')
        self.users_list.delete(1.0, END)
        for u in sorted(self.active_users):
            self.users_list.insert(END, f"• {u}\n")
        self.users_list.configure(state='disabled')

    def update_users_from_system_message(self, text):
        if 'приєднується' in text:
            self.add_user(text.split()[0])
        elif 'покидає' in text:
            self.remove_user(text.split()[0])

    # ---Перевірка з'єднання---
    def check_connection(self):
        try:
            self.client_socket.getpeername()
            self.connection_label.configure(text_color="green")
        except:
            self.connection_label.configure(text_color="red")
        self.after(5000, self.check_connection)

    # ---Теми---
    def change_theme(self, choice):
        set_appearance_mode("dark" if choice == 'Темна тема' else "light")

    # ---Очистити---
    def clear_chat(self):
        self.chat_text.configure(state='normal')
        self.chat_text.delete(1.0, END)
        self.chat_text.configure(state='disabled')
        self.add_message("Чат очищено", "system")

    # ---Закриття---
    def on_closing(self):
        try:
            if hasattr(self, 'client_socket') and self.username:
                goodbye = f'{self.username} покидає чат'
                self.client_socket.sendall(goodbye.encode())
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
        except:
            pass
        finally:
            self.destroy()


# ---Параметри---
HOST = '127.0.0.1'
PORT = 8080

if __name__ == "__main__":
    window = MainWindow()
    window.protocol("WM_DELETE_WINDOW", window.on_closing)
    window.mainloop()

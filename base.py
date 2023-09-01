import datetime
import json
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

from utility_function import handle_errors


@handle_errors(log_file="base.log", text='PackageGeneratorApp')
class PackageGeneratorApp:
    def __init__(self, root):
        self.check_buttons_frame = None
        self.input_text = None
        self.time_label = None
        self.generated_command_label = None
        self.path_to_pkg_combobox = None
        self.progressbar = None
        self.root = root
        self.root.title("Clio lite pkg builder")

        self.window_width = 800
        self.window_height = 400

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.x_position = (self.screen_width - self.window_width) // 2
        self.y_position = (self.screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}")

        self.packages = []
        self.selected_packages = []

        # Получите текущую дату и время
        self.current_datetime = datetime.datetime.now()

        # Преобразуйте дату и время в строку в нужном формате
        self.formatted_datetime = self.current_datetime.strftime("%d.%m.%Y_%H.%M.%S")

        # Создайте строку с добавленным "_v1"
        self.result_string = f"packages_{self.formatted_datetime}"

        self.path_var = tk.StringVar()
        self.path_var.set("")

        self.path_for_pkg_var = tk.StringVar()
        self.path_to_pkg_var = tk.StringVar()

        self.package_name_var = tk.StringVar()
        self.package_name_var.set(f"{self.result_string}")

        self.check_buttons = []

        self.generated_command_var = tk.StringVar()
        self.generated_command_var.set("Команда")  # Устанавливаем начальное значение пустой строки

        self.start_time = 0
        self.stop_timer_event = threading.Event()  # Создаем событие для остановки таймера
        self.isStopTimer = False

        self.load_settings()
        self.create_widgets()

    def create_widgets(self):
        frame_1 = ttk.Frame(self.root)
        frame_1.place(width=800, height=400, x=14, y=1)

        path_var = ttk.Entry(frame_1, cursor="ibeam", textvariable=self.path_var)
        path_var.place(width=265, height=25, x=8, y=20)
        self.set_placeholder(path_var, "D:\\Pkg\\")

        button_add_path = ttk.Button(frame_1, text="Добавить путь", command=self.add_path_for_pkg)
        button_add_path.place(width=115, height=27, x=650, y=19)

        button_open_packages = ttk.Button(frame_1, text="Добавить/Удалить пакеты", command=self.open_packages_input)
        button_open_packages.place(width=164, height=27, x=476, y=19)

        label_package_name = ttk.Label(frame_1, text="Путь для сохранения пакета")
        label_package_name.place(width=250, height=17, x=6, y=1)

        self.path_to_pkg_combobox = ttk.Combobox(self.root, values=self.path_for_pkg_var.get().split(","), width=50)
        self.path_to_pkg_combobox.set(self.path_to_pkg_var.get())
        self.path_to_pkg_combobox.place(width=757, height=25, x=20, y=74)
        self.path_to_pkg_combobox.bind("<<ComboboxSelected>>", self.on_path_selected)

        label_selected_path = ttk.Label(frame_1, text="Выбранный путь для пакета")
        label_selected_path.place(width=168, height=17, x=6, y=54)

        package_name_var = ttk.Entry(frame_1, cursor="ibeam", textvariable=self.package_name_var)
        package_name_var.place(width=180, height=25, x=286, y=20)

        label_path = ttk.Label(frame_1, text="Наименование пакета")
        label_path.place(width=133, height=17, x=285, y=1)

        button_generate_command = ttk.Button(self.root, text="Запустить", command=self.run_command)
        button_generate_command.place(width=115, height=27, x=14, y=360)

        button_generate_command = ttk.Button(self.root, text="Собрать команду", command=self.generate_command)
        button_generate_command.place(width=115, height=27, x=510, y=360)

        self.generated_command_label = tk.Label(self.root, textvariable=self.generated_command_var, anchor="w")
        self.generated_command_label.place(width=744, height=25, x=12, y=326)

        self.create_check_buttons()

        button_save_settings = ttk.Button(self.root, text="Сохранить настройки", command=self.save_settings)
        button_save_settings.place(width=141, height=27, x=640, y=360)

        button_select_all = ttk.Button(self.root, text="Выделить все", command=self.select_all_checkboxes)
        button_select_all.place(width=115, height=27, x=140, y=360)

        self.progressbar = ttk.Progressbar(self.root, mode='determinate', length=240)
        self.progressbar.place(x=262, y=363)

        self.time_label = ttk.Label(self.root, text="Время выполнения: 0.0 мин.")
        self.time_label.pack_forget()

    def select_all_checkboxes(self):
        for package, var, cb in self.check_buttons:
            var.set(1)

    def paste(self, event):
        self.input_text.event_generate("<<Paste>>")

    def select_all(self, event):
        self.input_text.tag_add(tk.SEL, "1.0", tk.END)
        self.input_text.mark_set(tk.INSERT, "1.0")
        self.input_text.see(tk.INSERT)
        return "break"

    def on_path_selected(self, event):
        self.path_to_pkg_var.set(self.path_to_pkg_combobox.get())

    def add_path_for_pkg(self):
        input_window = tk.Toplevel(self.root)
        input_text = tk.Text(input_window)
        input_text.pack()
        input_text.insert(tk.END, self.path_for_pkg_var.get())
        input_text.bind("<Control-v>", self.paste)
        input_text.bind("<Control-a>", self.select_all)

        def save_path_for_pkg():
            path_for_pkg = input_text.get("1.0", tk.END).strip()
            self.path_for_pkg_var.set(path_for_pkg)
            input_window.destroy()

            self.save_settings()

        tk.Button(input_window, text="Сохранить", command=save_path_for_pkg).pack()

    def create_check_buttons(self):
        self.check_buttons_frame = ttk.Frame(self.root)
        self.check_buttons_frame.place(width=757, height=217, x=12, y=107)

        check_buttons_frame_inner = ttk.Frame(self.check_buttons_frame)
        check_buttons_frame_inner.pack()

        row = 0
        col = 0
        for package in self.packages:
            var = tk.IntVar()
            cb = tk.Checkbutton(check_buttons_frame_inner, text=package, variable=var)
            cb.grid(row=row, column=col, padx=3, pady=3, sticky="w")
            self.check_buttons.append((package, var, cb))

            col += 1
            if col == 4:
                col = 0
                row += 1

    def open_packages_input(self):
        input_window = tk.Toplevel(self.root)
        input_text = tk.Text(input_window)
        input_text.pack()

        input_text.insert(tk.END, ", ".join(self.packages))

        input_text.bind("<Control-v>", self.paste)
        input_text.bind("<Control-a>", self.select_all)

        def update_packages():
            packages_input = input_text.get("1.0", tk.END).strip()
            self.packages = [pkg.strip() for pkg in packages_input.split(",")]
            self.check_buttons_frame.destroy()
            self.create_check_buttons()
            input_window.destroy()

        tk.Button(input_window, text="Сохранить", command=update_packages).pack()

    def generate_command(self):
        selected_packages = [package for package, var, cb in self.check_buttons if var.get() == 1]
        selected_packages_str = ', '.join(selected_packages)
        path = self.path_var.get()
        if not path.endswith('/'):
            path += '/'
        command = f"clio generate-pkg-zip -p '{selected_packages_str}' -d '{path}{self.package_name_var.get()}.zip'"

        self.generated_command_var.set(command)

        self.root.clipboard_clear()
        self.root.clipboard_append(command)
        self.root.update()

        print("Generated Command:", command)

    def load_settings(self):
        if os.path.exists("setting.json"):
            try:
                with open("setting.json", "r") as file:
                    data = json.load(file)
                    self.path_var.set(data.get("path", ""))
                    self.path_for_pkg_var.set(data.get("path_for_pkg", ""))
                    self.packages = data.get("packages", [])
                    self.path_to_pkg_var.set(data.get("path_to_pkg", ""))
            except FileNotFoundError:
                pass
        else:
            self.package_name_var.set("")

    def save_settings(self):
        self.packages = list(set(self.packages))

        data = {
            "path": self.path_var.get(),
            "path_for_pkg": self.path_for_pkg_var.get(),
            "path_to_pkg": self.path_to_pkg_var.get(),
            "package_name": self.package_name_var.get(),
            "packages": self.packages
        }
        with open("setting.json", "w") as file:
            json.dump(data, file)

    def run_command(self):
        self.generate_command()
        self.start_time = time.time()

        selected_path = self.path_to_pkg_combobox.get()
        command = self.generated_command_var.get()

        if selected_path and command:
            confirmation = messagebox.askyesno("Подтверждение",
                                               f"Вы уверены, что хотите выполнить команду в каталоге:\n{selected_path}\n\nКоманда:\n{command}")
            if confirmation:
                try:
                    os.chdir(selected_path)
                    self.progressbar.config(mode='indeterminate')
                    self.progressbar.start()
                    start_time = time.time()
                    self.time_label.pack()

                    update_time_thread = threading.Thread(target=self.update_execution_time)
                    update_time_thread.start()

                    def execute_command():
                        try:
                            result = subprocess.run(['powershell.exe', '-Command', command], shell=True,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE, text=True)
                            self.progressbar.stop()
                            self.progressbar.config(mode='determinate')
                            self.stop_timer_event.set()
                            self.time_label.pack_forget()

                            end_time = time.time()
                            execution_time = end_time - start_time
                            minutes = int(execution_time // 60)
                            fraction_minutes = execution_time % 60

                            output_message = result.stdout + "\n\n" + f"Время выполнения: {minutes:.0f}.{fraction_minutes:.0f} мин."
                            if result.stderr:
                                output_message += "Стандартный вывод ошибок:\n" + result.stderr
                            messagebox.showinfo("Результат выполнения команды", output_message)
                        except Exception as e:
                            self.progressbar.stop()
                            self.progressbar.config(mode='determinate')
                            self.stop_timer_event.set()
                            self.time_label.pack_forget()
                            print("Ошибка выполнения команды:", str(e))
                        finally:
                            end_time = time.time()
                            execution_time = end_time - start_time
                            print(execution_time)

                    command_thread = threading.Thread(target=execute_command)
                    command_thread.start()
                except Exception as e:
                    self.progressbar.stop()
                    self.progressbar.config(mode='determinate')
                    self.stop_timer_event.set()
                    self.time_label.pack_forget()
                    print("Ошибка выполнения команды:", str(e))

    def update_execution_time(self):
        while not self.stop_timer_event.is_set():
            end_time = time.time()
            execution_time = end_time - self.start_time
            minutes = int(execution_time // 60)
            fraction_minutes = execution_time % 60
            self.time_label.config(text=f"Время выполнения: {minutes:.0f}.{fraction_minutes:.0f} мин.")
            time.sleep(1)

    @staticmethod
    def set_placeholder(widget, placeholder_text):
        def clear_placeholder(event):
            if widget.get() == placeholder_text:
                widget.delete(0, tk.END)
                widget.configure(foreground="gray")

        def restore_placeholder(event):
            if not widget.get():
                widget.insert(0, placeholder_text)
                widget.configure(foreground="gray")

        if not widget.get():
            widget.insert(0, placeholder_text)
            widget.configure(foreground="gray")
            widget.tag_add("placeholder", "1.0", "end")

        widget.bind("<FocusIn>", clear_placeholder)
        widget.bind("<FocusOut>", restore_placeholder)

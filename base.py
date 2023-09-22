import datetime
import json
import os
import platform
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

from utility_function import basis_handle_errors


@basis_handle_errors(text='PackageGeneratorApp')
class PackageGeneratorApp:
    def __init__(self, root):
        self.result_string = None
        self.current_datetime = None
        self.formatted_datetime = None
        self.scrollbar = None
        self.check_buttons_frame_inner = None
        self.canvas = None
        self.check_buttons_frame = None
        self.input_text = ""
        self.time_label = None
        self.is_default = True
        self.generated_command_label = None
        self.path_to_pkg_combobox = None
        self.progressbar = None

        self.root = root
        self.root.title("Clio lite pkg builder")
        self.root.minsize(800, 400)
        self.root.maxsize(800, 400)
        self.window_width = 800
        self.window_height = 400
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_position = (self.screen_width - self.window_width) // 2
        self.y_position = (self.screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}")
        self.ctrl_pressed = False
        self.packages = []
        self.selected_packages = []

        self.set_default_name_pkg()

        self.path_var = tk.StringVar()
        self.path_var.set("")

        self.path_for_pkg_var = tk.StringVar()
        self.path_to_pkg_var = tk.StringVar()

        self.check_buttons = []

        self.generated_command_var = tk.StringVar()
        self.generated_command_var.set("")

        self.start_time = 0
        self.stop_timer_event = threading.Event()
        self.isStopTimer = False

        self.package_name_var = tk.StringVar()

        self.load_settings()
        # --------------------------------------------------------------------------------------------------------------
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Открыть папку сохранения [Ctrl+o]", command=self.open_folder)
        self.root.bind("<Control-o>", self.open_folder_key)
        self.file_menu.add_command(label="Выход [Ctrl+q]", command=self.quit_program)
        self.root.bind("<Control-q>", self.quit_program)
        self.menu_bar.add_cascade(label="Меню", menu=self.file_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Справка [Ctrl+h]", command=self.show_help)
        self.root.bind("<Control-h>", self.show_help_key)
        self.menu_bar.add_cascade(label="Помощь", menu=self.help_menu)

        self.current_key_sequence = []

        self.key_commands = [
            {"key_sequence": "<Control-Key-1>", "command": self.select_all_checkboxes_key},
            {"key_sequence": "<Control-Key-2>", "command": self.open_packages_input_key},
            {"key_sequence": "<Control-Key-3>", "command": self.add_path_for_pkg_key},

            {"key_sequence": "<Control-s>", "command": self.save_settings_key},
            {"key_sequence": "<Control-r>", "command": self.run_command_key},
            {"key_sequence": "<Control-b>", "command": self.generate_command_key},

            # {"key_sequence": "<Escape>", "command": lambda x: root.destroy()},
        ]

        for item in self.key_commands:
            key_sequence = item["key_sequence"]
            command = item["command"]
            self.root.bind(key_sequence, self.execute_command(command))
        # --------------------------------------------------------------------------------------------------------------
        if self.package_name_var.get() == "":
            self.package_name_var.set(f"{self.result_string}")

        self.create_widgets()

    @staticmethod
    def execute_command(command):
        def wrapped(event):
            command(event)

        return wrapped

    def set_default_name_pkg(self):
        self.get_current_date_whit_format()
        self.result_string = f"packages_{self.formatted_datetime}"

    def get_current_date_whit_format(self):
        self.current_datetime = datetime.datetime.now()
        self.formatted_datetime = self.current_datetime.strftime("%d.%m.%Y_%H.%M.%S")

    def create_widgets(self):
        self.package_name_var.trace_add("write", self.check_text)
        # --------------------------------------------------------------------------------------------------------------
        frame_1 = ttk.Frame(self.root)
        frame_1.place(width=900, height=500, x=0, y=1)
        # --------------------------------------------------------------------------------------------------------------
        label_package_name = ttk.Label(frame_1, text="Путь для сохранения пакета")
        label_package_name.place(width=250, height=15, x=13, y=5)
        # --------------------------------------------------------------------------------------------------------------
        path_var = ttk.Entry(frame_1, cursor="ibeam", textvariable=self.path_var)
        path_var.place(width=260, height=25, x=15, y=25)
        # --------------------------------------------------------------------------------------------------------------
        label_path = ttk.Label(frame_1, text="Наименование пакета")
        label_path.place(width=145, height=17, x=288.5, y=5)

        package_name_var = ttk.Entry(frame_1, cursor="ibeam", textvariable=self.package_name_var)
        package_name_var.place(width=255, height=25, x=290.5, y=25)
        # --------------------------------------------------------------------------------------------------------------
        button_open_packages = ttk.Button(frame_1, text="Добавить пакеты", command=self.open_packages_input,
                                          style="My.TButton")
        button_open_packages.place(width=110, height=27, x=560.5, y=23)
        # --------------------------------------------------------------------------------------------------------------
        button_add_path = ttk.Button(frame_1, text="Добавить путь", command=self.add_path_for_pkg,
                                     style="My.TButton")
        button_add_path.place(width=100, height=27, x=685, y=23)
        # --------------------------------------------------------------------------------------------------------------
        label_selected_path = ttk.Label(frame_1, text="Путь до папки Pkg")
        label_selected_path.place(width=168, height=17, x=11, y=54)
        # --------------------------------------------------------------------------------------------------------------
        values = [item.strip() for item in self.path_for_pkg_var.get().split(",")]

        self.path_to_pkg_combobox = ttk.Combobox(self.root, values=values, width=50)

        self.path_to_pkg_combobox.set(self.path_to_pkg_var.get())
        self.path_to_pkg_combobox.place(width=771, height=25, x=14, y=74)
        self.path_to_pkg_combobox.bind("<<ComboboxSelected>>", self.on_path_selected)
        # --------------------------------------------------------------------------------------------------------------
        self.generated_command_label = tk.Label(self.root, textvariable=self.generated_command_var, anchor="s")
        self.generated_command_label.place(width=800, height=25, x=0, y=326)
        # --------------------------------------------------------------------------------------------------------------
        self.create_check_buttons()
        # --------------------------------------------------------------------------------------------------------------
        button_generate_command = ttk.Button(self.root, text="Запустить", command=self.run_command)
        button_generate_command.place(width=115, height=27, x=14, y=360)
        # --------------------------------------------------------------------------------------------------------------
        button_select_all = ttk.Button(self.root, text="Выделить все", command=self.select_all_checkboxes,
                                       style="My.TButton")
        button_select_all.place(width=115, height=27, x=140, y=360)
        # --------------------------------------------------------------------------------------------------------------
        button_generate_command = ttk.Button(self.root, text="Собрать строку", command=self.generate_command,
                                             style="My.TButton")
        button_generate_command.place(width=115, height=27, x=516, y=360)
        # --------------------------------------------------------------------------------------------------------------
        button_save_settings = ttk.Button(self.root, text="Сохранить настройки", command=self.save_settings,
                                          style="My.TButton")
        button_save_settings.place(width=141, height=27, x=645, y=360)
        # --------------------------------------------------------------------------------------------------------------
        self.progressbar = ttk.Progressbar(self.root, mode='determinate', length=235)
        self.progressbar.place(x=268, y=362)
        # --------------------------------------------------------------------------------------------------------------
        self.time_label = ttk.Label(self.root, text="Сборка началась: 0.0 мин.")
        self.time_label.pack_forget()

    def check_text(self, *args):
        entered_text = self.package_name_var.get()
        if entered_text.endswith("_save"):
            self.save_to_settings_one_attribute("package_name_var", self.package_name_var.get()[:-5])
            self.save_to_settings_one_attribute("is_default", True)
            self.package_name_var.set(self.package_name_var.get()[:-5])
            self.is_default = True
        if entered_text.endswith("_clear"):
            self.save_to_settings_one_attribute("package_name_var", "")
            self.save_to_settings_one_attribute("is_default", False)
            self.package_name_var.set(f"{self.result_string}")
            self.is_default = False
        if entered_text.endswith("_update"):
            self.set_default_name_pkg()
            self.package_name_var.set(f"{self.result_string}")
        else:
            pass

    def quit_program(self, event):
        self.root.quit()

    def select_all_checkboxes_key(self, event):
        self.select_all_checkboxes()

    def select_all_checkboxes(self):
        first_checkbox_state = self.check_buttons[0][1].get()
        for package, var, cb in self.check_buttons:
            var.set(1 - first_checkbox_state)

    def is_at_least_one_checkbox_selected(self):
        for package, var, cb in self.check_buttons:
            if var.get() == 1:
                return True
        return False

    def paste(self, event):
        self.input_text.event_generate("<<Paste>>")

    def select_all(self, event):
        self.input_text.tag_add(tk.SEL, "1.0", tk.END)
        self.input_text.mark_set(tk.INSERT, "1.0")
        self.input_text.see(tk.INSERT)
        return "break"

    def open_folder_key(self, event):
        self.open_path_in_explorer()

    def open_folder(self):
        self.open_path_in_explorer()

    def open_path_in_explorer(self):
        path = self.path_var.get()
        system = platform.system()
        if system == "Windows":
            os.system(f"start explorer {path}")
        elif system == "Darwin":  # macOS
            os.system(f"open {path}")
        elif system == "Linux":
            os.system(f"xdg-open {path}")
        else:
            print("Неизвестная операционная система, не удалось открыть папку.")

    def on_path_selected(self, event):
        self.path_to_pkg_var.set(self.path_to_pkg_combobox.get())

    def create_check_buttons(self):
        self.check_buttons_frame = ttk.Frame(self.root)
        self.check_buttons_frame.place(width=800, height=220, x=0, y=107)

        self.canvas = tk.Canvas(self.check_buttons_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.check_buttons_frame_inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.check_buttons_frame_inner, anchor="nw")

        self.scrollbar = ttk.Scrollbar(self.check_buttons_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        row = 0
        col = 0
        self.check_buttons = []
        for package in self.packages:
            var = tk.IntVar()
            cb = tk.Checkbutton(self.check_buttons_frame_inner, text=package, variable=var)
            cb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            self.check_buttons.append((package, var, cb))

            col += 1
            if col == 4:
                col = 0
                row += 1

        self.check_buttons_frame_inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def show_help_key(self, event):
        self.show_help()

    def show_help(self):
        help_text = (
            "Горячие клавиши:\n\n"
            "[Ctrl+1] - [Выбрать\\Отменить выбор] все(х) пакеты(ов)\n"
            "[Ctrl+2] - Добавить пакеты\n"
            "[Ctrl+3] - Добавить путь\n\n"

            "[Ctrl+s] - Сохранить настройки\n"
            "[Ctrl+r] - Запустить сборку\n"
            "[Ctrl+b] - Собрать команду\n\n"

            "[Ctrl+o] - Открыть папку сохранения\n"
            "[Ctrl+h] - Справка\n"
            "[Ctrl+q] - Выход\n\n"
            "Команды которые можно выполнять в поле ввода [Наименование пакета]:\n"
            "(? вводить команды нужно в конце текста [pkg_v1_save])\n"
            "[_save | _clear | _update]\n\n"
            "[_save] - сохраняет введённое наименование пакета в файл настроек.\nПри следующим открытии приложения в поле [Наименование пакета] будет выведено сохранённое наименование пакета\n\n"
            "[_clear] - чистит введённое наименование пакета в файл настроек.\nПри следующим открытии приложения в поле [Наименование пакета] будет выведено дефолтное наименование пакета [packages_<Текущая дата и время в формате [%d.%m.%Y_%H.%M.%S]>]\n\n"
            "[_update] - обновляет поле [Наименование пакета] дефолтным наименованием [packages_<Текущая дата и время в формате [%d.%m.%Y_%H.%M.%S]>]")

        self.create_window("Справка", help_text, show_save_button=False, width=600, height=400, editable=False)

    @basis_handle_errors(text='create_window')
    def create_window(self, title, initial_text, on_save=None, show_save_button=True, width=600, height=300,
                      is_fix_size=False, editable=True):
        window = tk.Toplevel(self.root, width=width, height=height)
        window.focus_set()  # Установить фокус на окно
        window.bind("<Escape>", lambda x: window.destroy())

        if is_fix_size:
            window.maxsize(width=width, height=height)
            window.minsize(width=width, height=height)

        window.title(title)
        icon_path = os.path.join('icons', 'icon.ico')
        window.iconbitmap(icon_path)

        window_width = width
        window_height = height
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2

        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        input_text = tk.Text(window, width=width, height=height)

        input_text.pack()
        input_text.insert(tk.END, initial_text)

        if not editable:
            input_text.config(state="disabled")
        else:
            input_text.bind("<Control-v>", self.paste)
            input_text.bind("<Control-a>", self.select_all)

        if on_save and show_save_button:
            def save_and_close():
                text = input_text.get("1.0", tk.END).strip()
                on_save(text)
                window.destroy()

            (ttk.Button(window, text="Сохранить", command=save_and_close)
             .place(width=115, height=27, x=465, y=258))

    def open_packages_input_key(self, event):
        self.open_packages_input()

    def open_packages_input(self):
        initial_text = ", ".join(self.packages)

        def on_save(text):
            self.packages = [pkg.strip() for pkg in text.split(",")]
            self.check_buttons_frame.destroy()
            self.create_check_buttons()
            self.save_settings()

        self.create_window("Введите пакеты", initial_text, on_save, is_fix_size=True)

    def update_path_combobox(self):
        result_string = self.delete_duplicate_for_str()
        values = result_string.split(",")
        self.path_to_pkg_combobox['values'] = values

    def add_path_for_pkg_key(self, event):
        self.add_path_for_pkg()

    def add_path_for_pkg(self):
        initial_text = self.path_for_pkg_var.get()

        def on_save(text):
            self.path_for_pkg_var.set(text)
            self.update_path_combobox()
            self.save_settings()

        self.create_window("Введите путь для пакета", initial_text, on_save, is_fix_size=True)

    def generate_command_key(self, event):
        self.generate_command()

    def generate_command(self):
        selected_packages = [package for package, var, cb in self.check_buttons if var.get() == 1]
        selected_packages_str = ', '.join(selected_packages)
        path = os.path.join(self.path_var.get(), '')
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
                    self.is_default = data.get("is_default", True)
                    self.path_to_pkg_var.set(data.get("path_to_pkg", ""))
                    self.package_name_var.set(data.get("package_name_var", ""))
            except FileNotFoundError:
                pass
        else:
            self.package_name_var.set("")

    def save_settings_key(self, event):
        self.save_settings()

    def save_settings(self):
        self.packages = list(set(self.packages))

        result_string = self.delete_duplicate_for_str()

        data = {
            "path": self.path_var.get(),
            "path_for_pkg": result_string,
            "path_to_pkg": self.path_to_pkg_var.get(),
            "packages": self.packages,
        }

        if self.is_default:
            data["is_default"] = self.is_default
            data["package_name_var"] = self.package_name_var.get()
        else:
            data["is_default"] = False
            if "package_name_var" in data:
                del data["package_name_var"]

        with open("setting.json", "w") as file:
            json.dump(data, file)

    @staticmethod
    def save_to_settings_one_attribute(name_attribute, value):
        with open("setting.json", "r") as file:
            data = json.load(file)

        data[name_attribute] = value

        with open("setting.json", "w") as file:
            json.dump(data, file, indent=4)

    def delete_duplicate_for_str(self):
        input_string = self.path_for_pkg_var.get()
        unique_lines = list(set(input_string.splitlines()))
        result_string = ",".join(unique_lines)
        return result_string

    def run_command_key(self, event):
        self.run_command()

    def run_command(self):
        if not self.is_at_least_one_checkbox_selected():
            messagebox.showinfo("Сборка", "Для запуска команды нужно выбрать хотя бы один пакет.")
            return

        if self.check_zip_file_in_directory(self.package_name_var.get()):
            messagebox.showinfo("Информация", f"Сборка с именем [{self.package_name_var.get()}] уже существует.")
            return

        self.generate_command()
        current_directory = os.getcwd()

        def handle_command_execution(result, start_time):
            self.progressbar.stop()
            self.progressbar.config(mode='determinate')
            self.stop_timer_event.set()
            self.time_label.pack_forget()

            if not self.is_default:
                self.set_default_name_pkg()
                self.package_name_var.set(f"{self.result_string}")

            end_time = time.time()
            execution_time = end_time - start_time
            minutes = int(execution_time // 60)
            fraction_minutes = execution_time % 60

            output_message = result.stdout + (f"Сборка пакета [{self.package_name_var.get()}] завершилась успешно!"
                                              f"\nВремя выполнения: {minutes:.0f}.{fraction_minutes:.0f} мин.")
            if result.stderr:
                output_message += "Стандартный вывод ошибок:\n" + result.stderr
            messagebox.showinfo("Результат выполнения команды", output_message)

        def execute_command_internal():
            try:
                os.chdir(self.path_to_pkg_var.get())

                result = subprocess.run(['powershell.exe', '-Command', self.generated_command_var.get()], shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True)

                handle_command_execution(result, self.start_time)

            except Exception as ex:
                self.handle_command_error(ex, self.start_time)

            finally:
                os.chdir(current_directory)  # Возвращаемся в исходную директорию после выполнения команды

        # Получаем путь и команду
        selected_path = self.path_to_pkg_var.get()
        command = self.generated_command_var.get()
        if selected_path and command:
            confirmation = messagebox.askyesno("Подтверждение",
                                               f"Вы уверены, что хотите выполнить команду в каталоге:\n{selected_path}\n\nКоманда:\n{command}")
            if confirmation:
                try:
                    os.chdir(selected_path)
                    self.progressbar.config(mode='indeterminate')
                    self.progressbar.start()
                    self.start_time = time.time()
                    self.time_label.pack()

                    update_time_thread = threading.Thread(target=self.update_execution_time)
                    update_time_thread.start()

                    command_thread = threading.Thread(target=execute_command_internal)
                    command_thread.start()

                except Exception as e:
                    self.handle_command_error(e, self.start_time)

    # Метод для обработки ошибок выполнения команды
    def handle_command_error(self, error, start_time):
        self.progressbar.stop()
        self.progressbar.config(mode='determinate')
        self.stop_timer_event.set()
        self.time_label.pack_forget()
        print("Ошибка выполнения команды:", str(error))
        end_time = time.time()
        execution_time = end_time - start_time
        print(execution_time)

    def update_execution_time(self):
        while not self.stop_timer_event.is_set():
            end_time = time.time()
            execution_time = end_time - self.start_time
            minutes = int(execution_time // 60)
            fraction_minutes = execution_time % 60
            self.time_label.config(text=f"Время выполнения: {minutes:.0f}.{fraction_minutes:.0f} мин.")
            time.sleep(1)

    def check_zip_file_in_directory(self, filename):
        files = os.listdir(self.path_var.get())

        for file in files:
            if file == filename + ".zip":
                return True
        return False

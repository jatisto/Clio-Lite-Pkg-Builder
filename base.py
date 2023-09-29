import datetime
import json
import os
import platform
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import ttk

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from CTkMenuBar import *
from utility_function import basis_handle_errors
from update_version import Updater

font = ("MesloLGS NF", 14)

updater = Updater()
version_app = updater.get_remote_version()


@basis_handle_errors(text='App')
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.frame_3 = None
        self.frame_2 = None
        self.frame_4 = None
        self.download_link_btn = None
        self.appearance_mode_option_menu = None
        self.theme = tk.StringVar()
        self.theme.set("system")
        self.default_theme = tk.StringVar()
        self.default_theme.set("dark-blue")
        self.template_date_name = tk.StringVar()
        self.template_date_name.set("%d.%m.%Y_%H.%M.%S")
        self.root_frame = None
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

        self.root = self
        self.root.title(f"Clio lite pkg builder v{version_app}")
        self.root.iconbitmap('icons/icon.ico')
        self.root.minsize(900, 415)
        self.root.maxsize(900, 415)
        self.window_width = 900
        self.window_height = 415
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_position = (self.screen_width - self.window_width) // 2
        self.y_position = (self.screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}")
        self.ctrl_pressed = False
        self.packages = []
        self.selected_packages = []

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
        self.set_default_name_pkg()
        # --------------------------------------------------------------------------------------------------------------
        ctk.set_appearance_mode(self.theme.get())
        ctk.set_default_color_theme(self.default_theme.get())

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.menu_bar = CTkTitleMenu(self.root, width=100, padx=0)
        self.button_1 = self.menu_bar.add_cascade("Меню", font=font)
        self.button_2 = self.menu_bar.add_cascade("Помощь", font=font)

        self.dropdown1 = CustomDropdownMenu(widget=self.button_1, font=ctk.CTkFont("MesloLGS NF", 14), border_width=0,
                                            corner_radius=5)
        self.dropdown1.add_option(option="Открыть папку сохранения [Ctrl+o]", command=self.open_folder, font=font,
                                  border_width=0, corner_radius=5)
        self.dropdown1.add_separator()
        self.root.bind("<Control-o>", self.open_folder_key)
        self.dropdown1.add_option(option="Выход [Ctrl+q]", command=self.quit_program, font=font, border_width=0,
                                  corner_radius=5)
        self.root.bind("<Control-q>", self.quit_program_key)

        self.dropdown2 = CustomDropdownMenu(widget=self.button_2, font=ctk.CTkFont("MesloLGS NF", 14), border_width=0,
                                            corner_radius=5)
        self.dropdown2.add_option(option="Справка [Ctrl+h]", command=self.show_help, font=font, border_width=0,
                                  corner_radius=5)
        self.root.bind("<Control-h>", self.show_help_key)

        self.current_key_sequence = []

        self.key_commands = [
            {"key_sequence": "<Control-Key-1>", "command": self.select_all_checkboxes_key},
            {"key_sequence": "<Control-Key-2>", "command": self.open_packages_input_key},
            {"key_sequence": "<Control-Key-3>", "command": self.add_path_for_pkg_key},

            {"key_sequence": "<Control-s>", "command": self.save_settings_key},
            {"key_sequence": "<Control-r>", "command": self.run_command_key},
            {"key_sequence": "<Control-b>", "command": self.generate_command_key},
        ]

        for item in self.key_commands:
            key_sequence = item["key_sequence"]
            command = item["command"]
            self.root.bind(key_sequence, self.execute_command(command))
        # --------------------------------------------------------------------------------------------------------------
        if self.package_name_var.get() == "":
            self.package_name_var.set(f"{self.result_string}")

        self.after(500, self.delayed_check_for_updates)
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
        self.formatted_datetime = self.current_datetime.strftime(self.template_date_name.get())

    def create_widgets(self):
        self.root_frame = ctk.CTkFrame(self.root, border_width=0, corner_radius=0, width=900, height=450)
        self.root_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.package_name_var.trace_add("write", self.check_text)

        # --------------------------------------------------------------------------------------------------------------
        frame_1 = ctk.CTkFrame(self.root_frame, border_width=0, corner_radius=0, width=900, height=450)
        frame_1.grid(row=0, column=0, columnspan=4, padx=(0, 0), pady=(0, 0), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        path_var = ctk.CTkEntry(master=frame_1, border_width=1, font=font,
                                textvariable=self.path_var,
                                placeholder_text="Путь для сохранения пакета", width=300, height=30)
        path_var.grid(row=1, column=0, padx=(15, 5), pady=(10, 10), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        package_name_var = ctk.CTkEntry(master=frame_1, font=font, border_width=1, textvariable=self.package_name_var,
                                        placeholder_text="Наименование пакета",
                                        width=250, height=30)
        package_name_var.grid(row=1, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        button_open_packages = ctk.CTkButton(master=frame_1, width=135, text="Добавить пакеты",
                                             command=self.open_packages_input)
        button_open_packages.grid(row=1, column=3, padx=(10, 5), pady=(10, 10), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        button_add_path = ctk.CTkButton(master=frame_1, width=135, text="Добавить путь",
                                        command=self.add_path_for_pkg)
        button_add_path.grid(row=1, column=4, padx=(10, 5), pady=(10, 10), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.frame_2 = ctk.CTkFrame(self.root_frame, border_width=0, corner_radius=0)
        self.frame_2.grid(row=1, column=0, columnspan=4, padx=(0, 0), pady=(5, 0), sticky="nsew")

        values = [item.strip() for item in self.path_for_pkg_var.get().split(",")]

        self.path_to_pkg_combobox = ctk.CTkComboBox(master=self.frame_2, font=font, values=values, width=870, height=30,
                                                    border_width=1,
                                                    dropdown_font=font, corner_radius=5, button_hover_color="gray",
                                                    dropdown_hover_color="#4b4b4b")

        self.path_to_pkg_combobox.set(self.path_to_pkg_var.get())
        self.path_to_pkg_combobox.grid(row=2, column=0, padx=(15, 15), pady=(10, 10), sticky="nsew")
        self.path_to_pkg_combobox.bind("<<ComboboxSelected>>", self.on_path_selected)
        # --------------------------------------------------------------------------------------------------------------
        self.create_check_buttons()
        # --------------------------------------------------------------------------------------------------------------
        self.frame_3 = ctk.CTkFrame(self.root_frame, width=860, height=100)
        self.frame_3.grid(row=4, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.appearance_mode_option_menu = ctk.CTkOptionMenu(master=self.frame_3, width=145, button_color="#4b4b4b",
                                                             values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)

        self.appearance_mode_option_menu.grid(row=0, column=0, columnspan=1, padx=(737, 0), pady=(5, 5), sticky="nsew")

        self.appearance_mode_option_menu.set(self.theme.get())
        # --------------------------------------------------------------------------------------------------------------
        self.frame_4 = ctk.CTkFrame(self.root_frame)
        self.frame_4.grid(row=5, column=0, columnspan=5, padx=(0, 0), pady=(5, 0), sticky="nsew")

        button_generate_command = ctk.CTkButton(master=self.frame_4, text="Запустить", command=self.run_command)
        button_generate_command.grid(row=0, column=0, padx=(15, 15), pady=(5, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        button_select_all = ctk.CTkButton(master=self.frame_4, text="Выделить все", command=self.select_all_checkboxes)
        button_select_all.grid(row=0, column=1, padx=(0, 15), pady=(5, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        self.progressbar = ttk.Progressbar(master=self.frame_4, mode='determinate', length=240)
        self.progressbar.grid(row=0, column=2, padx=(0, 15), pady=(5, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        button_generate_command = ctk.CTkButton(master=self.frame_4, text="Собрать строку",
                                                command=self.generate_command)
        button_generate_command.grid(row=0, column=3, padx=(0, 15), pady=(5, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------
        button_save_settings = ctk.CTkButton(master=self.frame_4, text="Сохранить настройки",
                                             command=self.save_settings)
        button_save_settings.grid(row=0, column=4, padx=(0, 15), pady=(5, 5), sticky="nsew")
        # --------------------------------------------------------------------------------------------------------------

    def check_text(self, *args):
        entered_text = self.package_name_var.get()
        if entered_text.endswith("_blue"):
            self.save_to_settings_one_attribute("default_theme", 'dark-blue')
            ctk.set_default_color_theme(self.default_theme.get())
            self.message_restart()
        if entered_text.endswith("_green"):
            self.save_to_settings_one_attribute("default_theme", 'green')
            ctk.set_default_color_theme(self.default_theme.get())
            self.message_restart()
        if entered_text.endswith("_date_template"):
            str_value = self.package_name_var.get()
            temp = str_value.replace("_date_template", "")
            print(temp)
            if "%" in temp:
                self.save_to_settings_one_attribute("template_date_name", temp)
                self.message_restart()
        if entered_text.endswith("_date_template_clear"):
            self.save_to_settings_one_attribute("template_date_name", "%d.%m.%Y_%H.%M.%S")
            self.message_restart()
        if entered_text.endswith("_save"):
            self.save_to_settings_one_attribute("package_name_var", self.package_name_var.get()[:-5])
            self.save_to_settings_one_attribute("package_name_var_old", self.package_name_var.get()[:-5])
            self.save_to_settings_one_attribute("is_default", True)
            self.package_name_var.set(self.package_name_var.get()[:-5])
            self.is_default = True
        if entered_text.endswith("_return_name"):
            self.set_attribute_from_settings_data("package_name_var_old", self.package_name_var)
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

    def message_restart(self):
        confirmation = CTkMessagebox(title="Информация",
                                     message=f"Для того, чтобы изменения вступили в силу необходима перезагрузка.\n\n",
                                     option_1="Перезагрузить", option_2="Нет", button_width=85, button_height=30,
                                     font=font)
        response = confirmation.get()
        if response == "Перезагрузить":
            self.restart_app()

    def quit_program_key(self, event):

        self.root.quit()

    def quit_program(self):
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
        self.check_buttons_frame = ctk.CTkFrame(self.root_frame, border_width=0)
        self.check_buttons_frame.grid(row=2, column=0, padx=(15, 15), pady=(10, 10), sticky="nsew")
        color_canvas = "#dbdbdb" if self.theme.get() == "Light" else "#2b2b2b"
        self.canvas = ctk.CTkCanvas(self.check_buttons_frame, width=860, height=150, bg=color_canvas, borderwidth=0,
                                    highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.check_buttons_frame_inner = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.check_buttons_frame_inner, anchor="nw")

        self.scrollbar = ctk.CTkScrollbar(self.check_buttons_frame, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        row = 0
        col = 0
        self.check_buttons = []

        sorted_packages = sorted(self.packages, key=lambda p: p.lower())  # Сортировка по алфавиту

        for package in sorted_packages:
            var = tk.IntVar()
            cb = ctk.CTkCheckBox(self.check_buttons_frame_inner, text=package, variable=var, font=font)
            cb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            self.check_buttons.append((package, var, cb))

            col += 1
            if col == 3:
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
            "[_save | _clear | _update | _blue | _green | _date_template]\n\n"
            "[_save] - сохраняет введённое наименование пакета в файл настроек.\nПри следующим открытии приложения в поле [Наименование пакета] будет выведено сохранённое наименование пакета\n\n"
            "[_clear] - чистит введённое наименование пакета в файл настроек.\nПри следующим открытии приложения в поле [Наименование пакета] будет выведено дефолтное наименование пакета [packages_<Текущая дата и время в формате [%d.%m.%Y_%H.%M.%S]>]\n\n"
            "[_update] - обновляет поле [Наименование пакета] дефолтным наименованием [packages_<Текущая дата и время в формате [%d.%m.%Y_%H.%M.%S]>]\n\n"
            "[_blue] - устанавливает цвета элементов в синий цвет\n\n"
            "[_green] - устанавливает цвета элементов в зелёный цвет\n\n"
            "[_date_template] - устанавливает шаблон даты для поля [Наименование пакета].\nПо умолчанию выбран шаблон [%d.%m.%Y_%H.%M.%S].\nДля установки другого шаблона, введите его в поле [Шаблон даты (%d.%m.%Y)], после введите _date_template. [%d.%m.%Y_date_template]\n\n"
            "[_date_template_clear] - вернёт шаблон по умолчанию [%d.%m.%Y_%H.%M.%S].\n\n"
            "[_return_name] - вернёт последнее сохранённое с помощью команды [_save], наименование пакета.\n\n")

        self.create_window("Справка", help_text, show_save_button=False, width=900, height=415, editable=False)

    @basis_handle_errors(text='create_window')
    def create_window(self, title, initial_text, on_save=None, show_save_button=True, width=900, height=415,
                      is_fix_size=False, editable=True):
        window = ctk.CTkToplevel(self, width=width, height=height)

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)

        window.after(100, window.lift)
        window.bind("<Escape>", lambda destroy: window.destroy())

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

        frame_5 = ctk.CTkFrame(window, width=width - 15, height=height - 15)
        frame_5.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        input_text = ctk.CTkTextbox(window, width=width, height=height, font=font)
        input_text.grid(row=0, column=0, padx=(5, 5), pady=(0, 0), sticky="nsew")
        input_text.insert(tk.END, initial_text)

        if not editable:
            input_text.configure(state="disabled")
        else:
            input_text.bind("<Control-v>", self.paste)
            input_text.bind("<Control-a>", self.select_all)

        if on_save and show_save_button:
            def save_and_close():
                text = input_text.get("1.0", tk.END).strip()
                on_save(text)
                window.destroy()

            (ctk.CTkButton(window, text="Сохранить", command=save_and_close, height=30)
             .grid(row=0, column=0, padx=(765, 15), pady=(365, 15), sticky="nsew"))

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
                    self.theme.set(data.get("theme", ""))
                    self.default_theme.set(data.get("default_theme", "dark-blue"))
                    self.template_date_name.set(data.get("template_date_name", "%d.%m.%Y_%H.%M.%S"))
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
            "theme": self.theme.get(),
            "default_theme": self.default_theme.get(),
            "template_date_name": self.template_date_name.get(),
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
            CTkMessagebox(title="Сборка", message="Для запуска команды нужно выбрать хотя бы один пакет.")
            return

        if self.check_zip_file_in_directory(self.package_name_var.get()):
            CTkMessagebox(title="Информация",
                          message=f"Сборка с именем [{self.package_name_var.get()}] уже существует.")
            return

        self.generate_command()
        current_directory = os.getcwd()

        def handle_command_execution(result, start_time):
            self.progressbar.stop()
            self.progressbar.config(mode='determinate')
            self.stop_timer_event.set()

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
            CTkMessagebox(title="Результат выполнения команды", message=output_message)

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
            confirmation = CTkMessagebox(title="Подтверждение",
                                         message=f"Вы уверены, что хотите выполнить команду в каталоге:\n{selected_path}\n\nКоманда:\n{command}",
                                         option_1="Да", option_2="Нет", button_width=85, button_height=30, font=font,
                                         width=600, height=200)
            response = confirmation.get()
            if response == "Да":
                try:
                    os.chdir(selected_path)
                    self.progressbar.config(mode='indeterminate')
                    self.progressbar.start()
                    self.start_time = time.time()
                    command_thread = threading.Thread(target=execute_command_internal)
                    command_thread.start()

                except Exception as e:
                    self.handle_command_error(e, self.start_time)

    # Метод для обработки ошибок выполнения команды
    def handle_command_error(self, error, start_time):
        self.progressbar.stop()
        self.progressbar.config(mode='determinate')
        self.stop_timer_event.set()
        print("Ошибка выполнения команды:", str(error))
        end_time = time.time()
        execution_time = end_time - start_time
        print(execution_time)

    def check_zip_file_in_directory(self, filename):
        files = os.listdir(self.path_var.get())

        for file in files:
            if file == filename + ".zip":
                return True
        return False

    def change_appearance_mode_event(self, new_appearance_mode):
        self.save_to_settings_one_attribute("theme", new_appearance_mode)
        ctk.set_appearance_mode(new_appearance_mode)
        self.restart_app()

    def restart_app(self):
        python = sys.executable
        self.destroy()
        subprocess.call([python, "main.py"])

    def loading_file(self):
        """
        Открывает ссылку для загрузки файла.

        :return: None
        """

        webbrowser.open(updater.get_download_link())
        self.after(200, lambda: self.download_link_btn.pack_forget())

    def check_for_updates(self):
        """
        Проверяет наличие обновлений приложения.

        :return: None
        """
        update_available, local_version = updater.check_update()

        if update_available:
            confirmation = CTkMessagebox(title="Обновление",
                                         message=f"Доступна новая версия программы [v{local_version}].\n\n",
                                         option_1="Скачать", option_2="Отменить", button_width=85, button_height=30,
                                         font=font)
            response = confirmation.get()
            if response == "Скачать":
                self.loading_file()

    def delayed_check_for_updates(self):
        """
        Выполняет отложенную проверку наличия обновлений приложения.
        :return: None
        """
        self.check_for_updates()

    @staticmethod
    def set_attribute_from_settings_data(name_attribute, value):
        with open("setting.json", "r") as file:
            data = json.load(file)

            if not isinstance(value, tk.StringVar):
                value.delete(0, tk.END)
                value.insert(0, (data[name_attribute]))
            else:
                value.set((data[name_attribute]))


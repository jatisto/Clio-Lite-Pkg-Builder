import datetime
import json
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes.themed_style import ThemedStyle
from utility_function import handle_errors


@handle_errors(log_file="base.log", text='PackageGeneratorApp')
class PackageGeneratorApp:
    def __init__(self, root):
        self.scrollbar = None
        self.check_buttons_frame_inner = None
        self.canvas = None
        self.theme_style = None
        self.theme_button = None
        self.style = ThemedStyle(root)
        self.dark_theme = None
        self.light_theme = None
        self.check_buttons_frame = None
        self.input_text = ""
        self.time_label = None
        self.generated_command_label = None
        self.path_to_pkg_combobox = None
        self.progressbar = None
        self.root = root
        self.root.title("Clio lite pkg builder")
        self.is_dark = False
        self.root.minsize(800, 400)
        self.root.maxsize(800, 400)
        self.window_width = 800
        self.window_height = 400

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.x_position = (self.screen_width - self.window_width) // 2
        self.y_position = (self.screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}")

        self.packages = []
        self.selected_packages = []

        self.current_datetime = datetime.datetime.now()
        self.formatted_datetime = self.current_datetime.strftime("%d.%m.%Y_%H.%M.%S")
        self.result_string = f"packages_{self.formatted_datetime}"

        self.path_var = tk.StringVar()
        self.path_var.set("")

        self.path_for_pkg_var = tk.StringVar()
        self.path_to_pkg_var = tk.StringVar()

        self.package_name_var = tk.StringVar()
        self.package_name_var.set(f"{self.result_string}")

        self.check_buttons = []

        self.generated_command_var = tk.StringVar()
        self.generated_command_var.set("")

        self.start_time = 0
        self.stop_timer_event = threading.Event()
        self.isStopTimer = False

        self.style = ttk.Style()
        self.load_settings()

        self.theme_colors = {
            "dark": {"bg": "#464646", "fg": "#efefef", "select_bg": "#efefef", "select_fg": "#464646",
                     "high_light": "#6c6c6c", "font": "JetBrains Mono"},
            "light": {"bg": "#efefef", "fg": "black", "select_bg": "#cacaca", "select_fg": "#464646",
                      "high_light": "#cacaca", "font": "JetBrains Mono"}
        }

        if self.is_dark:
            self.style.theme_use(self.dark_theme)
        else:
            self.style.theme_use(self.light_theme)

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        self.theme_style = "dark" if self.is_dark else "light"
        self.configure_styles(style, self.theme_style)
        # --------------------------------------------------------------------------------------------------------------
        frame_1 = ttk.Frame(self.root, style="My.TFrame")
        frame_1.place(width=900, height=500, x=0, y=1)
        # --------------------------------------------------------------------------------------------------------------
        label_package_name = ttk.Label(frame_1, text="Путь для сохранения пакета", style="My.TLabel")
        label_package_name.place(width=250, height=15, x=15, y=5)
        # --------------------------------------------------------------------------------------------------------------
        path_var = ttk.Entry(frame_1, cursor="ibeam", textvariable=self.path_var, style="My.TEntry")
        path_var.place(width=260, height=25, x=15, y=25)
        self.set_placeholder(path_var, "D:\\Pkg\\")
        # --------------------------------------------------------------------------------------------------------------
        label_path = ttk.Label(frame_1, text="Наименование пакета", style="My.TLabel")
        label_path.place(width=145, height=17, x=284.5, y=5)
        # --------------------------------------------------------------------------------------------------------------
        package_name_var = ttk.Entry(frame_1, cursor="ibeam", textvariable=self.package_name_var, style="My.TEntry")
        package_name_var.place(width=185, height=25, x=284.5, y=25)
        # --------------------------------------------------------------------------------------------------------------
        button_open_packages = ttk.Button(frame_1, text="Добавить пакеты", command=self.open_packages_input,
                                          style="My.TButton")
        button_open_packages.place(width=110, height=27, x=480.5, y=23)
        # --------------------------------------------------------------------------------------------------------------
        button_add_path = ttk.Button(frame_1, text="Добавить путь", command=self.add_path_for_pkg, style="My.TButton")
        button_add_path.place(width=100, height=27, x=602, y=23)
        # --------------------------------------------------------------------------------------------------------------
        self.theme_button = ttk.Button(self.check_buttons_frame, text="Темно", command=self.toggle_theme,
                                       compound="center", style="My.TButton")
        self.theme_button.place(width=70, height=27, x=715, y=24)
        # --------------------------------------------------------------------------------------------------------------
        label_selected_path = ttk.Label(frame_1, text="Путь до папки Pkg", style="My.TLabel")
        label_selected_path.place(width=168, height=17, x=15, y=54)
        # --------------------------------------------------------------------------------------------------------------
        self.path_to_pkg_combobox = ttk.Combobox(self.root, values=self.path_for_pkg_var.get().split(","), width=50,
                                                 style="My.TCombobox")
        self.path_to_pkg_combobox.set(self.path_to_pkg_var.get())
        self.path_to_pkg_combobox.place(width=771, height=25, x=14, y=74)
        self.path_to_pkg_combobox.bind("<<ComboboxSelected>>", self.on_path_selected)
        # --------------------------------------------------------------------------------------------------------------
        self.generated_command_label = tk.Label(self.root, textvariable=self.generated_command_var, anchor="s")
        self.generated_command_label.place(width=800, height=25, x=0, y=326)
        # --------------------------------------------------------------------------------------------------------------
        self.create_check_buttons()
        # --------------------------------------------------------------------------------------------------------------
        button_generate_command = ttk.Button(self.root, text="Запустить", command=self.run_command, style="My.TButton")
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
        self.time_label = ttk.Label(self.root, text="Время выполнения: 0.0 мин.")
        self.time_label.pack_forget()

    def configure_styles(self, style, theme_style):
        for widget_font in ["TButton", "TCheckbutton", "TCombobox", "TEntry", "TFrame", "TLabel",
                            "TLabelframe", "TLabelFrame", "TMenubutton", "TNotebook", "TPanedwindow",
                            "TPanedWindow", "TProgressbar", "TRadiobutton", "TScale", "TScrollbar",
                            "TSeparator", "TSizegrip", "TSpinbox", "TStyle", "TTreeview"]:
            style.configure(widget_font,
                            font=("JetBrains Mono", 9))

        for widget_name in ["TCombobox", "TButton", "TEntry", "TLabel"]:
            widget_colors = self.theme_colors[theme_style]
            style.configure(widget_name,
                            background=widget_colors["bg"],
                            foreground=widget_colors["fg"],
                            selectbackground=widget_colors["select_bg"],
                            selectforeground=widget_colors["select_fg"])

    def toggle_theme(self):
        current_theme = self.style.theme_use()
        new_theme = self.dark_theme if current_theme != self.dark_theme else self.light_theme
        style = ttk.Style()
        try:
            self.style.theme_use(new_theme)
            self.theme_button.configure(text="Темно" if new_theme == self.dark_theme else "Светло")
            self.apply_theme_to_checkboxes("dark" if new_theme == self.dark_theme else "light")
            self.progressbar.place(x=268, y=369 if new_theme == self.dark_theme else 362)
            self.is_dark = True if new_theme == self.dark_theme else False
            self.theme_style = "dark" if self.is_dark else "light"
            self.configure_styles(style, self.theme_style)
            self.canvas.configure(background=self.theme_colors[self.theme_style]["bg"])
            if style.lookup('TButton', style) != "":
                self.path_to_pkg_combobox.configure(style=style)
        except tk.TclError as e:
            messagebox.showerror("Theme Error", f"Error switching to {new_theme} theme: {e}")

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

    def create_check_buttons(self):
        self.theme_style = "dark" if self.is_dark else "light"
        self.check_buttons_frame = ttk.Frame(self.root)
        self.check_buttons_frame.place(width=800, height=220, x=0, y=107)

        self.canvas = tk.Canvas(self.check_buttons_frame, bg=self.theme_colors[self.theme_style]["bg"])
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
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.apply_theme_to_checkboxes(self.theme_style)

    def on_mousewheel(self, event):
        # Обработка события колесика мыши для прокрутки
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def apply_theme_to_checkboxes(self, theme):
        widget_color = self.theme_colors[theme]

        checkbox_background = widget_color["bg"]
        checkbox_foreground = widget_color["fg"]
        checkbox_highlight = widget_color["high_light"]

        self.generated_command_label.config(bg=checkbox_highlight, fg=checkbox_foreground)

        for package, var, cb in self.check_buttons:
            cb.configure(bg=checkbox_background, fg=checkbox_foreground, selectcolor=checkbox_background)

    def create_input_window(self, title, initial_text, on_save):
        input_window = tk.Toplevel(self.root)

        # Создайте экземпляр ThemedStyle для окна
        style = ThemedStyle(input_window)
        self.theme_style = "dark" if self.is_dark else "light"
        self.configure_styles(style, self.theme_style)

        # Выберите тему в зависимости от self.is_dark
        if self.is_dark:
            style.theme_use(self.dark_theme)
        else:
            style.theme_use(self.light_theme)

        input_window.iconbitmap('icons/icon.ico')

        input_text = tk.Text(input_window)

        self.theme_style = "dark" if self.is_dark else "light"
        widget = self.theme_colors[self.theme_style]
        input_text.configure(background=widget["bg"], foreground=widget["fg"], font=(widget["font"], 12))

        input_text.pack()
        input_text.insert(tk.END, initial_text)
        input_text.bind("<Control-v>", self.paste)
        input_text.bind("<Control-a>", self.select_all)

        def save_and_close():
            text = input_text.get("1.0", tk.END).strip()
            on_save(text)
            input_window.destroy()

        ttk.Button(input_window, text="Сохранить", command=save_and_close, style="My.TButton").pack()

    def open_packages_input(self):
        initial_text = ", ".join(self.packages)

        def on_save(text):
            self.packages = [pkg.strip() for pkg in text.split(",")]
            self.check_buttons_frame.destroy()
            self.save_settings()
            self.create_check_buttons()

        self.create_input_window("Введите пакеты", initial_text, on_save)

    def update_path_combobox(self):
        result_string = self.delete_duplicate_for_str()
        values = result_string.split(",")
        self.path_to_pkg_combobox['values'] = values

    def add_path_for_pkg(self):
        initial_text = self.path_for_pkg_var.get()

        def on_save(text):
            self.path_for_pkg_var.set(text)
            self.update_path_combobox()
            self.save_settings()

        self.create_input_window("Введите путь для пакета", initial_text, on_save)

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
                    self.is_dark = data.get("is_dark", True)
                    self.theme_colors = data.get("theme_color", "")
                    self.dark_theme = data.get("dark_theme", "equilux")
                    self.light_theme = data.get("light_theme", "plastik")
            except FileNotFoundError:
                pass
        else:
            self.package_name_var.set("")

    def save_settings(self):
        self.packages = list(set(self.packages))

        result_string = self.delete_duplicate_for_str()

        data = {
            "path": self.path_var.get(),
            "path_for_pkg": result_string,
            "path_to_pkg": self.path_to_pkg_var.get(),
            "package_name": self.package_name_var.get(),
            "is_dark": self.is_dark,
            "packages": self.packages,
            "theme_color": self.theme_colors,
            "dark_theme": self.dark_theme,
            "light_theme": self.light_theme,
        }
        with open("setting.json", "w") as file:
            json.dump(data, file)

    def delete_duplicate_for_str(self):
        input_list = self.path_for_pkg_var.get().split(",\n")
        unique_list = list(set(input_list))
        result_string = ",\n".join(unique_list)
        return result_string

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

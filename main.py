import tkinter as ttk
import customtkinter as ctk
from base import App
from utility_function import basis_handle_errors


@basis_handle_errors(text='PackageGeneratorApp')
def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

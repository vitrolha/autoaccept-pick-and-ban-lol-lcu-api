from lcu_driver import Connector
from time import sleep
import pyautogui
import pygetwindow as gw
from threading import Thread
import json

connector = Connector()

@connector.ready
async def selecionar(connection):
    i = 1
    while True:
        
        while i <6:
            print(i)
            if i ==5:
                print(i)
                break
            i += 1
        print("Saiuu")
        break
        

connector.start()
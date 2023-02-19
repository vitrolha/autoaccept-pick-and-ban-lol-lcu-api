from lcu_driver import Connector
from time import sleep
import pyautogui
import pygetwindow as gw
from threading import Thread
import json


connector = Connector()


async def selecionar(connection):
    await connection.request('patch', '/lol-champ-select/v1/session/actions/1', data = {"championId": 144, 'completed' : True})

@connector.ready
async def gameFase(connection):
    while True:
        
        #accept = await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
        fila = await connection.request('get', '/lol-lobby/v2/lobby/matchmaking/search-state')
        fila2 = await fila.json()
        fila3 = fila2.get('searchState')

        print("Fila",fila3)

        ban_fase = await connection.request('get', '/lol-champ-select/v1/session')
        ban_fase2 = await ban_fase.json()
        ban_fase3 = ban_fase2.get('actions')
        if ban_fase3 != None:
            for actions in ban_fase2['actions']:
                for action in actions:
                    if action['isInProgress']:
                            print(action['type']) 
                            if action['type'] == 'pick':
                                print("Selecao de compeoes")
                                picakr = await connection.request('patch', '/lol-champ-select/v1/session/actions/'+ str(1), data = {"championId": 144, "completed" : True})
                                print(picakr)
                            elif action['type'] == 'ban':
                                print("Banindo")
                                ban = await connection.request('patch', '/lol-champ-select/v1/session/actions/'+ str(1), data = {"championId": 84, "completed" : True})
                                sleep(10)
                                print(ban)
                            else:
                                if fila3 == 'Found':
                                    sleep(1)
                                    #accept
                                    sleep(8)
                                    print("Partida aceita")
                                if fila3 == 'Searching':
                                    print("Na fila") 
        sleep(3)



connector.start()

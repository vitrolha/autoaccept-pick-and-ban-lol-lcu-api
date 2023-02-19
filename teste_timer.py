from lcu_driver import Connector
from time import sleep
import pyautogui
import pygetwindow as gw
from threading import Thread
import json

connector = Connector()

@connector.ready
async def timer(connection):

    fila = await connection.request('get', '/lol-lobby/v2/lobby/matchmaking/search-state')
    fila_info = await fila.json()
    fila_estado = fila_info.get('searchState')
    #print("Fila",fila_estado)

    #Parte para aceitar partida automaticamente
    accept = await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')

    #teste para mostrar o champ
    pickar = await connection.request('patch', '/lol-champ-select/v1/session/actions/1', data={'championId': 84, 'completed': True })
    pickar_info = await pickar.json()
    print(pickar_info)
    
    fases = await connection.request('get', '/lol-champ-select/v1/session')
    fases_info = await fases.json()
    fase_actions = fases_info.get('actions')
    #print(fases_info)
    if fase_actions != None:
        print("separando")
        for fases in fases_info['actions']:
            for fase in fases:
                if fase['isInProgress']:
                    if fase['type'] == 'pick':
                        print("Pick fase")
                        sleep(3)
                        pickar
                        print(pickar_info)
                    
                    if fase['type'] == 'ban':
                        print("Ban fase")
                        
                        
                    else:
                        if fila_estado == 'Found':
                            sleep(1)
                            accept
                            sleep(8)
                            print("Partida Aceita")
                        if fila_estado == 'Searching':
                            print("Na fila")


        
connector.start()


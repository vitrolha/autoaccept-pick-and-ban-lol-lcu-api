from lcu_driver import Connector
from time import sleep
import pyautogui
import pygetwindow as gw
from threading import Thread
import time
import champions_pegar_json

connector = Connector()

#async def sessaoGame(connection):
#    while True:
#        sessao = await connection.request('get', '/lol-gameflow/v1/session')
#        print("Sessão:",await sessao.json())
#        sleep(5)

@connector.ready
async def gameFase(connection):
    print("Conectado ao LCU API")
    #pegando o pick e o ban e seus respectivos ids 
    pick = input("Pick:").capitalize()
    ban = input("Ban:").capitalize()
    pickeban = champions_pegar_json.pegarChampInfo(pick,ban)
    #print(pickeban[0]) pick
    #print(pickeban[1]) ban
    #Pegando informações do invocador
    na_champ_select = False
    posicao = -1
    fila = -2
    invocador_request = await connection.request('get', '/lol-login/v1/session')
    invocador_info = await invocador_request.json()
    #print(invocador_info)
    conta_id = invocador_info['summonerId']
    print("Id do invocador: ", conta_id)
    while True:
        selecao_campeoes = await connection.request('get', '/lol-champ-select/v1/session')
        selecao_campeoes_info = await selecao_campeoes.json()
        na_fila = await connection.request('get', '/lol-lobby/v2/lobby/matchmaking/search-state')
        na_fila_info = await na_fila.json()
        fila_estado = na_fila_info.get('searchState')
        fim = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
        fim_info = await fim.json()

        #print(selecao_campeoes_info)
        #print("Voltou pro primeiro While")
        #Parte para aceitar Partida
        if "errorCode" in selecao_campeoes_info and na_champ_select == False:
            if fila_estado == 'Searching':
                print('Na fila')
            if fila_estado == 'Found':
                print('Partida Encontrada')
                sleep(2)
                aceitar = await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
        if "errorCode" in selecao_campeoes_info and na_champ_select:
            print('Nao esta na selecao de campeoes')
            if fim_info == 'InProgress':
                print("Partida Iniciada")
                break
            posicao = -1
            fila = -2
            na_champ_select = False
        if 'errorCode' not in selecao_campeoes_info and not na_champ_select:
            print('Entrou na selecao de campeoes')
            na_champ_select = True
        if na_champ_select:
            fila_request = await connection.request('get', '/lol-gameflow/v1/session')
            fila_info = await fila_request.json()
            nova_fila = fila_info['gameData']['queue']['id']
            if nova_fila != fila:
                print("Fila diferente! Fila ID: " + str(nova_fila))
                fila = nova_fila
            if fila in [400, 420, 440, -1]:
                for user in selecao_campeoes_info["myTeam"]:
                    if user['summonerId'] == conta_id:
                        if posicao == -1:
                            print("Posicao do invocador " + str(user['cellId']))
                        posicao = user['cellId']
                for evento_grupo in selecao_campeoes_info['actions']:
                    for evento in evento_grupo:
                        if evento['actorCellId'] == posicao and evento['type'] == 'ban' and evento['isInProgress']:
                            evento_id = evento['id']
                            temporizador = await connection.request('get', '/lol-champ-select/v1/session/timer')
                            temporizador_info = await temporizador.json()
                            atual = time.time()
                            if 'internalNowInEpochMs' in temporizador_info:
                                restante = (temporizador_info['internalNowInEpochMs'] + temporizador_info[
                                                'adjustedTimeLeftInPhase']) / 1000 - atual
                                print("Vez de banir. Esperando %.2f sec" %(restante - 3))
                                sleep(restante - 3)
                                #Trocar o championId para banir o campeao dejesado
                                banir = await connection.request('patch', '/lol-champ-select/v1/session/actions/'+ str(evento_id), data = {"championId": pickeban[1], "completed" : True})
                                print(await banir.json())
                                print("Campeao banido!")
                                print("Tempo restante: %.2f sec" %(restante))
                                #Pegar o resto do tempo
                        if evento['actorCellId'] == posicao and evento['type'] == 'pick' and evento['isInProgress']:
                            evento_id_pick = evento['id']
                            #print(evento_id_pick)
                            temporizador = await connection.request('get', '/lol-champ-select/v1/session/timer')
                            temporizador_info = await temporizador.json()
                            atual = time.time()
                            if 'internalNowInEpochMs' in temporizador_info:
                                restante = (temporizador_info['internalNowInEpochMs'] + temporizador_info[
                                                'adjustedTimeLeftInPhase']) / 1000 - atual
                                print("Vez de pickar. Esperando %.2f sec" %(restante - 2))
                                sleep(restante - 2)
                                #Trocar o championId para pickar o campeao dejesado
                                pickar = await connection.request('patch', '/lol-champ-select/v1/session/actions/'+ str(evento_id_pick), data = {"championId": pickeban[0], 'completed' : True})
                                pickar_info = await pickar.json()
                                print("Campeao Pickado!")
                                while True:
                                    fim = await connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                                    fim_info = await fim.json()
                                    sleep(2)
                                    #print(fim_info)
                                    #print("Segundo While")
                                    if fim_info == 'InProgress' or fim_info == 'Matchmaking':
                                        #print('Saiu do segundo While')
                                        break
                                    


                        

         


        sleep(3)
connector.start()
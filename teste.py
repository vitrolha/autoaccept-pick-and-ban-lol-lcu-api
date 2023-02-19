from lcu_driver import Connector
from time import sleep
import pyautogui
import pygetwindow as gw
from threading import Thread
import json
import time


connector = Connector()

async def pickar(connection, fila_id, champion):
    await connection.request('post', '/lol-champ-select/v1/session/actions/'+ str(fila_id), data = {"championId": champion, "completed" : True})

@connector.ready
async def main(connection):

    print("Connected to LCU API")
    in_champion_select = False
    position = 1
    queue = -2
    summ_request = await connection.request("get", "/lol-login/v1/session")
    summ_info = await summ_request.json()
    print(summ_info)
    acc_id = summ_info["summonerId"]
    print("Summoner id is " + str(acc_id))

    while True:
        ch_select = await connection.request("get", "/lol-champ-select/v1/session")
        ch_select_info = await ch_select.json()
        print(ch_select_info)
        if "errorCode" in ch_select_info and in_champion_select:
            print("No longer in champion select")
            position = 1
            queue = -2
            in_champion_select = False
        if "errorCode" not in ch_select_info and not in_champion_select:
            print("Entered champion select")
            in_champion_select = True
        if in_champion_select:
            queue_request = await connection.request("get", "/lol-gameflow/v1/session")
            queue_info = await queue_request.json()
            print(queue_info)
            new_queue = queue_info["gameData"]["queue"]["id"]
            game_data = queue_info['gameData']
            queue_data = queue_info['gameData']['queue']
            id_data = queue_info['gameData']['queue']['id']
            print(f"Meu GameData: {game_data}, Meu Queue: {queue_data}, Meu Id: {id_data}")
            if new_queue != queue:
                print("Different queue detected. Queue ID: " + str(new_queue))
                queue = new_queue
            if queue in [400, 420, 440, -1]:
                for user in ch_select_info["myTeam"]:
                    if user["summonerId"] == acc_id:
                        if position == -1:
                            print("User position is " + str(user["cellId"]))
                        position = user["cellId"]
                for event_group in ch_select_info["actions"]:
                    for event in event_group:
                        if event["actorCellId"] == position and event["type"] == "pick" and event["isInProgress"]:
                            event_id = event["id"]
                            timer = await connection.request("get", "/lol-champ-select/v1/session/timer")
                            timer_info = await timer.json()
                            print(timer_info)
                            current = time.time()
                            if "internalNowInEpochMs" in timer_info:
                                remaining = (timer_info["internalNowInEpochMs"] + timer_info[
                                        "adjustedTimeLeftInPhase"]) / 1000 - current
                                print("Detected pick turn. Sleeping " + str(remaining - 25))
                                time.sleep(remaining - 25)
                                lock_in = await connection.request('patch', '/lol-champ-select/v1/session/actions/'+ str(event_id), data = {"championId": 84, "completed" : True})
                                lock_in_info = await lock_in.json()
                                print(lock_in_info)
                                print("Locked in.")
                        if event["actorCellId"] == position and event["type"] == "ban" and event["isInProgress"]:
                            event_id = event["id"]
                            timer = await connection.request("get", "/lol-champ-select/v1/session/timer")
                            timer_info = await timer.json()
                            print(timer_info)
                            current = time.time()
                            if "internalNowInEpochMs" in timer_info:
                                remaining = (timer_info["internalNowInEpochMs"] + timer_info[
                                        "adjustedTimeLeftInPhase"]) / 1000 - current
                                print("Detected ban turn. Sleeping " + str(remaining - 30))
                                time.sleep(remaining - 30)
                                lock_in = await connection.request('patch', '/lol-champ-select/v1/session/actions/'+ str(event_id), data = {"championId": 266, "completed" : True})
                                lock_in_info = await lock_in.json()
                                sleep(10) 
                                print(lock_in_info)
                                print("Banned.")

        sleep(3)
connector.start()

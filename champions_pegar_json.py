from urllib.request import urlopen
import json

versions_url = 'https://ddragon.leagueoflegends.com/api/versions.json'
respostas_versions = urlopen(versions_url)
versions_json = json.loads(respostas_versions.read())
ultimo_patch = versions_json[0]
print(ultimo_patch)

champions_json_url = (f'http://ddragon.leagueoflegends.com/cdn/{ultimo_patch}/data/en_US/champion.json')
respostas_champions = urlopen(champions_json_url)
champions_json = json.loads(respostas_champions.read())
champions_info = champions_json['data']
#info = champions_info['Aatrox']['key']
#print(info)

def pegarChampInfo(champ_name_pick,champ_name_ban):
        if champ_name_pick not in champions_info:
            print(f"Esse campeao nao exite: {champ_name_pick}")
        if champ_name_ban not in champions_info:
             print(f"Este campeao nao existe: {champ_name_ban}")
        else:
            champ_pick_id = champions_info[champ_name_pick]['key']
            champ_ban_id = champions_info[champ_name_ban]['key']
            print(f'Id do Pick: {champ_pick_id}, Id do Ban: {champ_ban_id}')
            return [champ_pick_id,champ_ban_id]
            


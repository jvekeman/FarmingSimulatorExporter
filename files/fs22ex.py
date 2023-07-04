from prometheus_client import start_http_server, Metric, REGISTRY
import time, sys
from bs4 import BeautifulSoup

# Version 1.0

class FarmingSimulatorExporter(object):
  def collect(self):
    pathToFiles = sys.argv[1]
    # Fetch the XML for vehicles
    vehicleFile = pathToFiles + '\\vehicles.xml'
    with open(vehicleFile, 'r') as f:
        data = f.read()
    vehicledata = BeautifulSoup(data, features="lxml")

    # Converting
    all_vehicles = vehicledata.find_all('vehicle')

    # Convert requests and duration to a summary in seconds
    ageMetric = Metric('fs_vehicles_age',
        'Gives the age of the vehicle and labels containing usefull information about the vehicle', 'summary')
    for vehicle in all_vehicles:
        if(vehicle.get('farmid') =='1'):
            path = vehicle.get('filename').split('/')
            if ('pallets' not in path):
                if(len(path[0].split('$'))>1):
                    name = path[1]
                else:
                    name = str(path[2] + ' ' + path[3])
                defaultLabels={'Price': vehicle.get('price'), 'operatingTime': vehicle.get('operatingtime'), 'Damage': vehicle.find('wearable').get('damage'), 'Name':name}
                lablesV=calculateFillLevelsAndLabels(defaultLabels, vehicle)
                ageMetric.add_sample('fs_vehicles_age',
                    value=vehicle.get('age'), labels=lablesV)
    yield ageMetric

    # Fetch the XML for save data
    savegameFile = pathToFiles + '\\careerSavegame.xml'
    with open(savegameFile, 'r') as f:
        data = f.read()
    careerdata = BeautifulSoup(data, features="lxml")
    saveName = careerdata.find('savegamename').contents[0]

    modsMetric = Metric('fs_total_amount_mods',
                    'The amount of enabled mods in savegame', 'gauge')
    modsMetric.add_sample('fs_total_amount_mods', value=len(careerdata.find_all("mod")), labels={'Name': saveName})
    yield modsMetric

    timeplayedMetric = Metric('fs_total_time_played',
                    'Amount of time played in savegame', 'summary')
    timeplayedMetric.add_sample('fs_total_time_played', value=careerdata.find('playtime').contents[0], labels={'Name': saveName})
    yield timeplayedMetric

    moneyMetric = Metric('fs_amount_of_money', 
                    'Amount of money in savegame', 'gauge')
    moneyMetric.add_sample('fs_amount_of_money', value=careerdata.find('money').contents[0], labels={'Name': saveName})
    yield moneyMetric

    farmLands = pathToFiles + '\\farmland.xml'
    with open(farmLands, 'r') as f:
        data = f.read()
    Bs_farmLands = BeautifulSoup(data, features="lxml")

    farmLandMetric = Metric('fs_farmlands',
                    'Owned: 1, NotOwned: 0', 'gauge')
    farmLand = Bs_farmLands.find_all('farmland')
    for land in farmLand:
        farmLandMetric.add_sample('fs_farmlands', value=land.get('farmid'), labels={'Farmland': land.get('id')})
    yield farmLandMetric

    missionFile = pathToFiles + '\\missions.xml'
    with open(missionFile, 'r') as f:
        data = f.read()
    missiondata = BeautifulSoup(data, features="lxml")
    missions = missiondata.find_all('mission')

    missionMetric = Metric('fs_mission',
                           'General info about available missions', 'gauge')
    for mission in missions:
        missionMetric.add_sample('fs_mission', value=mission.get('reward'), labels={'Type': mission.get('type'), 'Status': mission.get('status'), 'FieldID': mission.find('field').get('id')})
    yield missionMetric

def calculateFillLevelsAndLabels(defaultLabels, vehicle):
    lables = defaultLabels
    if vehicle.find('fillunit') is not None:
        for unit in vehicle.find_all('unit'):
            if (unit.get('filltype') != 'UNKNOWN') & (unit.get('filltype') != 'AIR'):
                lables[unit.get('filltype')] = vehicle.find('unit').get('filllevel')
    return lables    

if len(sys.argv) == 2:
    if (__name__ == '__main__'):
        start_http_server(9118)
        REGISTRY.register(FarmingSimulatorExporter())
        while True: time.sleep(1)
else:
    print("Unexpected argument, exiting...")
# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import requests, MASexsi, MASinjector, multiprocessing, os, time, MASsettings, random, json

url = "http://$$$$:5000"
settings = MASsettings.Settings()

def handleEXSi(id):
    time.sleep(random.randint(0, 30))
    print("Getting Node")
    noderequest = requests.get(url+"/node")
    print(noderequest.status_code)
    nodeid = noderequest.text
    httpheaders = {"X-Node-ID":str(nodeid)}
    continueprocessing = True
    print(nodeid)
    while continueprocessing:
        time.sleep(random.randint(0, 30))
        commandrequest = requests.get(url+"/commands", headers=httpheaders)
        commands = commandrequest.text.split(",")
        command = str(commands[0])
        print("Command Received: "+command)
        if command=="GenerateVM":
            print("GenerateVM")
            MASexsi.GenerateVM(nodeid)
            removecommandrequest = requests.post(url+"/commands", "GenerateVM".encode('utf-8'),headers=httpheaders)
            time.sleep(2)
        if command=="AddNIC":
            print("AddNIC")
            MASexsi.AddNIC(nodeid)
            removecommandrequest = requests.post(url+"/commands", "AddNIC".encode('utf-8'),headers=httpheaders)
            time.sleep(2)
        if command=="AddCD":
            print("AddCD")
            MASexsi.AddCD(nodeid)
            removecommandrequest = requests.post(url+"/commands", "AddCD".encode('utf-8'),headers=httpheaders)
            time.sleep(2)
        if command=="PowerOnVM":
            print("PowerOnVM")
            MASexsi.PowerOnVM(nodeid)
            removecommandrequest = requests.post(url+"/commands", "PowerOnVM".encode('utf-8'),headers=httpheaders)
            time.sleep(60)
        if command=="PushPayload":
            print("PushPayload")
            removecommandrequest = requests.post(url+"/commands", "PushPayload".encode('utf-8'),headers=httpheaders)
            MASinjector.PushPayload(nodeid)
        if command=="DeleteVM":
            print("DeleteVM")
            MASexsi.DeleteVM(nodeid)
            removecommandrequest = requests.post(url+"/commands", "DeleteVM".encode('utf-8'),headers=httpheaders)
            time.sleep(5)
            continueprocessing=False

if __name__ == '__main__':
    locationcount = settings.read("EXPERIMENT.RUNS_PER_LOCATION")
    stimulusruncount = settings.read("EXPERIMENT.RUNS_PER_STIMULUS")
    stimuli = settings.read("EXPERIMENT.STIMULI_TEMPLATE")
    regionfile = open("regions.json")
    regions = json.load(regionfile)
    regioncount = len(regions)
    stimulicount = len(stimuli)
    totalcount = (locationcount * regioncount) * (stimulicount * stimulusruncount)
    print("Total VM Count to initalize: "+str(totalcount))
    totalarray = []
    for count in range(0,totalcount):
        totalarray.append(count)
    pool = multiprocessing.Pool(processes=5)
    pool.map(handleEXSi, totalarray)
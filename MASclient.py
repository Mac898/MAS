# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import requests, MASexperiment, os, time, sys

url = "http://$$$.$$$.$$$.$$$:5000"
aptrequest = requests.get(url+"/aptpackages")
piprequest = requests.get(url+"/pippackages")

nodeid = sys.argv[1]
aptpackagelist = aptrequest.text.split(",")
pippackagelist = piprequest.text.split(",")

experiment = MASexperiment.SciExClientAutomaticExecution(nodeid, aptpackagelist, pippackagelist)
continueprocessing = True
httpheaders = {"X-Node-ID":str(nodeid)}

while continueprocessing:
    commandrequest = requests.get(url+"/commands", headers=httpheaders)
    commands = commandrequest.text.split(",")
    command = str(commands[0])
    print("Command Received: "+command)
    if command=="Install":
        print("Installing")
        experiment.install()
        removecommandrequest = requests.post(url+"/commands", "Install".encode('utf-8'),headers=httpheaders)
    if command=="StartX":
        print("StartX")
        experiment.startx()
        removecommandrequest = requests.post(url+"/commands", "StartX".encode('utf-8'),headers=httpheaders)
    if command=="JoinVPN":
        print("JoinVPN")
        vpnrequest = requests.get(url+"/vpnlocation", headers=httpheaders)
        vpn = vpnrequest.text
        experiment.joinVPN(vpn)
        removecommandrequest = requests.post(url+"/commands", "JoinVPN".encode('utf-8'),headers=httpheaders)
    if command=="LaunchFirefox":
        print("LaunchFirefox")
        experiment.launchFirefox()
        removecommandrequest = requests.post(url+"/commands", "LaunchFirefox".encode('utf-8'),headers=httpheaders)
    if command=="RunAutoCompleteTest":
        print("RunAutoCompleteTest")
        stimulusrequest = requests.get(url+"/stimulus", headers=httpheaders)
        stimulus = stimulusrequest.text
        text = experiment.runAutoCompleteTest(stimulus)
        resultrequest = requests.post(url+"/results",text.encode('utf-8'), headers=httpheaders)
        removecommandrequest = requests.post(url+"/commands", "RunAutoCompleteTest".encode('utf-8'),headers=httpheaders)
    if command=="CloseFirefox":
        print("CloseFirefox")
        experiment.closeFirefox()
        removecommandrequest = requests.post(url+"/commands", "CloseFirefox".encode('utf-8'),headers=httpheaders)
    if command=="LeaveVPN":
        print("LeaveVPN")
        experiment.leaveVPN()
        removecommandrequest = requests.post(url+"/commands", "LeaveVPN".encode('utf-8'),headers=httpheaders)
    if command=="ShutdownLinux":
        print("ShutdownLinux")
        removecommandrequest = requests.post(url+"/commands", "ShutdownLinux".encode('utf-8'),headers=httpheaders)
        continueprocessing = False
        os.system("shutdown now")
    time.sleep(5)
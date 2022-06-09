# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
from os import listdir
from os.path import isfile, join
import re, json

#static
regions = []
vpnc = "./vpn_connections"

for f in listdir(vpnc):
    if isfile(join(vpnc, f)):
        if ".ovpn" in f:
            m = re.search("$$$$-(\S+)-[abc0-9]{3}\.ovpn", f)
            region = m.group(1)
            regions.append(region)

regions = list(dict.fromkeys(regions))
rFile = open("regions.json", "w+")
json.dump(regions, rFile)
rFile.close()
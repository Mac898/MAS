# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import json

#settings class
class Settings:
    def read(self, variable):
        """Call settings in JSON-like syntax"""
        rfile = open("settings.json", "r")
        jfile = json.load(rfile)
        rfile.close()
        parts = variable.split(".")
        if len(parts) == 0:
            return jfile
        elif len(parts) == 1:
            return jfile[parts[0]]
        elif len(parts) == 2:
            return jfile[parts[0]][parts[1]]
        elif len(parts) == 3:
            return jfile[parts[0]][parts[1]][parts[2]]
        else:
            return "INVALID ARGUMENT"
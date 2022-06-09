# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import logging, subprocess, time, pytesseract, cv2, numpy, os, re
import MASsettings
from PIL import Image
try:
    import pyautogui
except Exception as e:
    logging.error("No PyAutoGUI Loaded | Exception: "+str(e))

class SciExClientAutomaticExecution:
    def __init__(self, nodeid, aptpackagelist, pippackagelist):
        self.nodeid = nodeid
        self.settings = MASsettings.Settings()
        logging.basicConfig(level=logging.DEBUG, filename="client.log", filemode="w")
        logging.getLogger().addHandler(logging.StreamHandler())
        self.log = logging.getLogger()
        try:
            self.sw, self.sh = pyautogui.size()
        except Exception as e:
            logging.debug(str(e))
        logging.info("SciExClientAutomaticExecution Initalized")

    def install(self):
        try:
            dns = subprocess.Popen(["echo", "'nameserver 1.1.1.1'", ">>", "/etc/resolv.conf"])
            dns.wait()
            aptupdate = subprocess.Popen(["apt", "update"])
            aptupdate.wait()
            aptcommand = ["apt", "install", "-yq"]
            aptcommand.extend(aptpackagelist)
            gui = subprocess.Popen(aptcommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            gui.wait()
            output = gui.stdout.read().decode("utf-8").split("\n")
            pipcommand = ["pip", "install"]
            aptcopipcommandmmand.extend(pippackagelist)
            pip = subprocess.Popen(aptcommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            pip.wait()
            pipoutout = pip.stdout.read().decode("utf-8").split("\n")
            for line in output:
                logging.debug("APT Install: "+str(line))
            for line in pipoutout:
                logging.debug("PIP Install: "+str(line))
        except Exception as e:
            logging.error("INSTALLGUI: "+str(e))

    def startx(self):
        try:
            x = subprocess.Popen()
            gui = subprocess.Popen(["startx"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            gui.wait()
            output = gui.stdout.read().decode("utf-8").split("\n")
            for line in output:
                logging.debug("StartX: "+str(line))
        except Exception as e:
            logging.error("StartX: "+str(e))

    def launchFirefox(self):
        try:
            self.firefox = subprocess.Popen(["firefox", "https://google.com"])
            time.sleep(8)
        except Exception as e:
            logging.error("Firefox launch error :"+str(e))

    def runAutoCompleteTest(self, stimulus):
        pyautogui.moveTo(0.50*self.sw, 0.5*self.sh)
        pyautogui.click()
        pyautogui.write(stimulus)
        time.sleep(1)
        im = pyautogui.screenshot()
        imc = im.crop((0.14*self.sw, 0.58*self.sh, 0.7*self.sw, 0.99*self.sh))
        imc_cv = numpy.array(imc)
        resized = cv2.resize(imc_cv, (0,0), fx = 4, fy = 4)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        cv2.imwrite("test.png", opening)
        text = pytesseract.image_to_string(opening, config="--psm 6")
        text.strip("\n\n")
        logging.info(text)
        return text

    def closeFirefox(self):
        try:
            time.sleep(2)
            self.firefox.terminate()
        except Exception as e:
            logging.error("Firefox close error"+str(e))

    def joinVPN(self, region):
        vpnspath = os.getcwd() + "/vpn_connections/"
        servers = "|".join(os.listdir(os.getcwd() + "/vpn_connections/"))
        server = re.search(region+'-([abc]\S\S)', servers).group(1)
        vpnpath = vpnspath + "$$$$-" +region+"-"+server+".ovpn"
        credsfile = os.getcwd() + "/" + self.settings.read("SETTINGS.VPN.FILE")
        try:
            self.vpn = subprocess.Popen(["openvpn", "--auth-nocache","--config", vpnpath, "--auth-user-pass", credsfile], cwd=vpnspath)
            time.sleep(10)
            logging.info("VPN Returned:" + str(self.vpn.returncode))
        except Exception:
            logging.error("VPN Launch Error")

    def leaveVPN(self):
        try:
            self.vpn.terminate()
            a = subprocess.Popen(["killall", "openvpn"])
            time.sleep(3)
            a.terminate()
        except Exception:
            logging.error("Failed to close VPN")

if __name__ == "__main__":
    e = SciExClientAutomaticExecution(9999, " ", " ")
    e.launchFirefox()
    e.runAutoCompleteTest("test")
    e.closeFirefox()
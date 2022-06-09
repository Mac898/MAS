# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import os, time
from fabric import Connection, Config
from MASsettings import Settings
from MASexsi import GetVMIPS

settings = Settings()
sshconfig = Config(overrides={'sudo': {'password': ""}})

def PushPayload(ID):
    IP = GetVMIPS(ID)[0]
    print("Pushing Payload for ID: "+str(ID)+" @ IP: "+str(IP))
    ssh = Connection(IP, user=settings.read("SETTINGS.VM.USER"), connect_kwargs={"key_filename":settings.read("SETTINGS.VM.SSH_KEY")}, config=sshconfig)
    ssh.put("/home/$$$/SciEx-AutoCompleteByLocation/client.tar", "/home/ubuntu/") #tar file is client code tarred.
    try:
        ssh.run("mkdir MASclient")
    except Exception:
        print("Folder already Exists")
    ssh.run("tar -xvf client.tar -C MASclient")
    ssh.run("echo 'nameserver 10.1.1.1' | sudo tee -a /etc/resolv.conf")
    ssh.run('cd '+settings.read("SETTINGS.VM.CLIENT_PATH"))
    time.sleep(10)
    ssh.run("sudo apt install ca-certificates")
    try:
        ssh.run('sudo apt update')
    except Exception:
        try:
            time.sleep(10)
            ssh.run('sudo apt update')
        except Exception:
            try:
                time.sleep(10)
                ssh.run('sudo apt update')
            except Exception:
                try:
                    time.sleep(10)
                    ssh.run('sudo apt update')
                except Exception:
                    try:
                        time.sleep(10)
                        ssh.run('sudo apt update')
                    except Exception:
                        time.sleep(10)
                        ssh.run('sudo apt update')
    ssh.run('sudo apt install -yq python3 dbus-x11 screen python3-pip python3-tk python3-dev tesseract-ocr libtesseract-dev firefox xorg openbox openvpn')
    try:
        ssh.run('sudo rm get-pip.py')
    except Exception:
        print("Did not need to remove get-pip.py")
    ssh.run('wget https://bootstrap.pypa.io/pip/3.5/get-pip.py')
    ssh.run('python3 get-pip.py')
    ssh.run('sudo pip3 install --upgrade pip==20.3.4')
    ssh.run('sudo pip3 install pytesseract==0.2.2 numpy==1.18.5 requests six opencv-python tesseract pyautogui --no-cache-dir')
    try:
        ssh.run('sudo killall startx && sudo killall openbox')
    except Exception:
        print("Startx and openbox kill not needed.")
    time.sleep(1)
    ssh.run('sudo startx 1>/dev/null 2>/dev/null &')
    ssh.run('sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1')
    ssh.run('sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1')
    ssh.run('sudo touch /root/.Xauthority')
    time.sleep(3)
    try:
        ssh.run('export DISPLAY=:0 && export HOME="/root/" && cd /home/ubuntu/MASclient && sudo python3 MASclient.py '+str(ID), pty=True)
    except Exception:
        return

if __name__ == "__main__":
    PushPayload(1)
# sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0 pywebview
# sudo python3 local/main/brainstorm/gui/web.py
import webview
import os
import subprocess
import requests

URL = "http://flyyrin.pythonanywhere.com/"

jsondata = {
    "gameongoing": True, 
    "winner": 0, 
    "player": 1,
    "game": {
        "p1": {
            "pieces": 0,
            "kings": 0,
            "captured": 0
        },
        "p2": {
            "pieces": 0,
            "kings": 0,
            "captured": 0
        }
    }
}

class Api:
    def __init__(self):
        pass

    def exit(self,nodig):
        print("Board uit")
        # subprocess.Popen("killall sh", shell=True, stdout=subprocess.PIPE)
        quit()
    
    def start(self,cp):
        np1,np2,cp1,cp2 = cp.split("&")
        print(np1,np2,cp1,cp2)
        requests.post(url = f"{URL}gameongoing", json = jsondata)
    
    def stop(self,nodig):
        print("Reset board")
        customdata = dict(jsondata)
        customdata["gameongoing"] = False
        requests.post(url = f"{URL}gameongoing", json = customdata)
    
if __name__ == '__main__':
    api = Api()
    window = webview.create_window('Start', os.path.join(os.getcwd(), "C:/Users/bounc/Documents/GitHub/GIP-2022-2023/local/main/brainstorm/gui/start.html"), js_api=api, fullscreen=True) # /home/rpi/Documents/GIP-2022-2023/local/main/brainstorm/gui/start.html
    webview.start()
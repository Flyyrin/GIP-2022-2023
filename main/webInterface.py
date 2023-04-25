import webview # sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0 pywebview
import os
import subprocess
import requests
import time

URL = "http://flyyrin.pythonanywhere.com/game"

def startWebInterface(queue):
    class Api:
        def __init__(self):
            pass

        def exit(self,nodig):
            requests.post(url = URL, params = {"type": "stop"})
            queue.put("exit")
            time.sleep(1)
            subprocess.Popen("killall sh", shell=True, stdout=subprocess.PIPE)
        
        def start(self,playerData):
            queue.put("start|"+playerData)
            requests.post(url = URL, params = {"type": "start"})

        def color(self,colorData):
            queue.put("color|"+colorData)
        
        def stop(self,nodig):
            queue.put("stop")
            requests.post(url = URL, params = {"type": "stop"})
        
    requests.post(url = URL, params = {"type": "stop"})
    api = Api()
    window = webview.create_window('Start', os.path.join(os.getcwd(), "/home/rpi/Documents/GIP-2022-2023/main/webInterface/start.html"), js_api=api, fullscreen=True)
    webview.start()
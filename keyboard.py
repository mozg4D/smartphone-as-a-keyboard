from flask import Flask, request
import ctypes
from ctypes import wintypes
import threading
import secrets
import os
import socket
import pyqrcode
import os.path

hllDll = ctypes.WinDLL("User32.dll")
user32 = ctypes.WinDLL('user32')
class KEYBDINPUT(ctypes.Structure): _fields_ = (("wVk", wintypes.WORD),("dwFlags", wintypes.DWORD),("dwExtraInfo", wintypes.WPARAM))
class INPUT(ctypes.Structure): _fields_ = (("type", wintypes.DWORD),("ki", KEYBDINPUT),("padding", ctypes.c_ubyte * 8))
def Press(key):   user32.SendInput(1, ctypes.byref(INPUT(type=1, ki=KEYBDINPUT(wVk=key))), 40)
def Release(key): user32.SendInput(1, ctypes.byref(INPUT(type=1, ki=KEYBDINPUT(wVk=key, dwFlags=2))), 40)

if(hllDll.GetKeyState(0x90)):
    Press(0x90)
    Release(0x90)

app = Flask(__name__, static_url_path='')
cancel_thread = shift_pressed = False
btn_code = ''
ip = socket.gethostbyname(socket.gethostname())
password = secrets.token_urlsafe(5)

if os.path.isfile('path.svg'):
    with open('path.txt') as f:
        path = f.readlines()[0]
        f.close()
        password = path[path.index(':5000/')+len(':5000/'):path.index('.htm')]
        p_ip = path[path.index('http://')+len('http://'):path.index(':5000')]
        if(p_ip != ip):
            path = 'http://'+ ip +':5000/'+ password +'.htm?p='+ password
            file = open("path.txt", "w") 
            file.write(path) 
            file.close()
            url = pyqrcode.create(path)
            url.svg('path.svg', scale=8)
else:
    path = 'http://'+ ip +':5000/'+ password +'.htm?p='+ password
    file = open("path.txt", "w") 
    file.write(path) 
    file.close()
    url = pyqrcode.create(path)
    url.svg('path.svg', scale=8)

def repeat_btn():
    global btn_code, cancel_thread, t
    t.cancel()
    if(not cancel_thread) :
        Release( int( '0x' + btn_code[1:3], 16 ) )
        Press(int( '0x' + btn_code[1:3], 16 ) )
        t=threading.Timer(.04, repeat_btn)
        t.start()

t=threading.Timer(1000, repeat_btn)
t.cancel()

@app.route('/'+ password +'.htm')
def send(): return app.send_static_file('index.htm')

@app.errorhandler(404)
def not_found(e):
    global btn_code, shift_pressed, cancel_thread, t
    cancel_thread=True
    t.cancel()
    btn_code=request.url.partition(':5000/'+password)[2]
    if(btn_code[1:] == ''): return ('', 204)
    if(btn_code[0:3]=='p10'): shift_pressed=True
    if(btn_code[0:3]=='u10'): shift_pressed=False
    if(btn_code[0] == 'p'):
        if(len(btn_code)==4 and shift_pressed==False): Press( int( '0x10', 16 ) )
        Press( int( '0x' + btn_code[1:3], 16 ) )
        if(btn_code[1:3] != '11' and btn_code[1:3] != '12' and btn_code[1:3] != '10'): #ctrl alt shift
            t.cancel()
            t=threading.Timer(.3, repeat_btn)       
            cancel_thread = False
            t.start()
    if(btn_code[0] == 'u'):
        if(len(btn_code)==4 and shift_pressed==False): Release( int( '0x10', 16 ) )
        Release( int( '0x' + btn_code[1:3], 16 ) )
    return ('', 204)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000, threads=1)
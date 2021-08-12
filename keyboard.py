from flask import Flask, request
import ctypes
import threading
import secrets
import os
import socket
import pyqrcode

user32 = ctypes.WinDLL('user32')
class KBDIN(ctypes.Structure): _fields_ = (("wVk", ctypes.c_ushort),("dwFlags", ctypes.c_ulong),("dwExtraInfo", ctypes.c_ulonglong))
class INPUT(ctypes.Structure): _fields_ = (("type", ctypes.c_ulong),("ki", KBDIN),("padding", ctypes.c_ubyte * 8))
def Press(key_code):   user32.SendInput(1, ctypes.byref(INPUT(type=1, ki=KBDIN(wVk=key_code))), 40)
def Release(key_code): user32.SendInput(1, ctypes.byref(INPUT(type=1, ki=KBDIN(wVk=key_code, dwFlags=2))), 40)

if(user32.GetKeyState(0x90)):
    Press(0x90)
    Release(0x90)

app = Flask(__name__, static_url_path='')
cancel_thread = sh = ct = al = False
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
    global btn_code, sh, ct, al, cancel_thread, t
    cancel_thread=True
    t.cancel()
    btn_code=request.url.partition(':5000/'+password)[2]
    if(btn_code[1:] == ''): return ('', 204)
    if(btn_code[0:3]=='p10'): sh=True
    if(btn_code[0:3]=='u10'): sh=False
    if(btn_code[0:3]=='p11'): ct=True
    if(btn_code[0:3]=='u11'): ct=False
    if(btn_code[0:3]=='p12'): al=True
    if(btn_code[0:3]=='u12'): al=False
    if(btn_code[0] == 'p'):
        if(ct and al and btn_code[1:3] == '08'): os.popen('%windir%\system32\\taskmgr.exe /7')
        if(len(btn_code)==4 and sh==False): Press( int( '0x10', 16 ) )
        Press( int( '0x' + btn_code[1:3], 16 ) )
        if(btn_code[1:3] != '11' and btn_code[1:3] != '12' and btn_code[1:3] != '10'): #ctrl alt shift
            t=threading.Timer(.3, repeat_btn)       
            cancel_thread = False
            t.start()
    if(btn_code[0] == 'u'):
        if(len(btn_code)==4 and sh==False): Release( int( '0x10', 16 ) )
        Release( int( '0x' + btn_code[1:3], 16 ) )
    return ('', 204)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000, threads=1)
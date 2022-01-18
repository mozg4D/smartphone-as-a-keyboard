import ctypes
import socket
import secrets
import os
import pyqrcode
import threading
import asyncio
import websockets

cancel_thread = sh = ct = al = False
btn_code = ''

user32 = ctypes.WinDLL('user32')
class KBDIN(ctypes.Structure): _fields_ = (("wVk", ctypes.c_ushort),("dwFlags", ctypes.c_ulong),("dwExtraInfo", ctypes.c_ulonglong))
class INPUT(ctypes.Structure): _fields_ = (("type", ctypes.c_ulong),("ki", KBDIN),("padding", ctypes.c_ubyte * 8))
def Press(key_code):   user32.SendInput(1, ctypes.byref(INPUT(type=1, ki=KBDIN(wVk=key_code))), 40)
def Release(key_code): user32.SendInput(1, ctypes.byref(INPUT(type=1, ki=KBDIN(wVk=key_code, dwFlags=2))), 40)

if(user32.GetKeyState(0x90)):
    Press(0x90)
    Release(0x90)

ip = socket.gethostbyname(socket.gethostname())
password = secrets.token_urlsafe(5)

if os.path.isfile('path.svg'):
    with open('path.txt') as f:
        path = f.readlines()[0]
        f.close()
        password = path[-7:]
        p_ip = path[7:path.index(':5000')]
        if(p_ip != ip):
            path = 'http://'+ ip +':5000/index.htm?p='+ password
            file = open("path.txt", "w") 
            file.write(path) 
            file.close()
            url = pyqrcode.create(path)
            url.svg('path.svg', scale=8)
else:
    path = 'http://'+ ip +':5000/index.htm?p='+ password
    file = open("path.txt", "w") 
    file.write(path) 
    file.close()
    url = pyqrcode.create(path)
    url.svg('path.svg', scale=8)

async def handler(websocket):
    while True:
        request = await websocket.recv()
        if request[:7] == password:
            global btn_code, sh, ct, al
            btn_code=request[7:]
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
            if(btn_code[0] == 'u'):
                if(len(btn_code)==4 and sh==False): Release( int( '0x10', 16 ) )
                Release( int( '0x' + btn_code[1:3], 16 ) )

async def main():
    async with websockets.serve(handler, ip, 8765, ping_interval=None):
        await asyncio.Future()

os.startfile("server.exe")
asyncio.run(main())
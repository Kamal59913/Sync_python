import socket
import netifaces
from netifaces import AF_INET
import os
from sys import platform
import sys
import threading
import time
import keyboard
import clipboard
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
flag = 0
global_port = 8000
if platform == "win32":
    import winreg as wr
    homedir = os.environ['APPDATA']
    homedir = homedir+"\sync.conf"
    def setup_windows():
        homedir = os.environ['APPDATA']
        homedir = homedir+"\sync.conf"
        config_file_pointer = open(homedir,"w")
        config_file_pointer.write("mode:server\n")
        iface_guids = netifaces.interfaces()
        iface_names = ['(unknown)' for i in range(len(iface_guids))]
        reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
        reg_key = wr.OpenKey(reg, 'SYSTEM\\CurrentControlSet\\Control\\Network\\{4d36e972-e325-11ce-bfc1-08002be10318}')
        for i in range(len(iface_guids)):
            try:
                reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + '\\Connection')
                iface_names[i] = wr.QueryValueEx(reg_subkey, 'Name')[0]
            except FileNotFoundError:
                pass
        i = 0 
        for item in iface_names:
            i = i+1
            if "Local" in item:
                a = netifaces.ifaddresses(iface_guids[i])
                if len(a)>1:
                    a = a[2]
                    a = a[0]
                    ip_addr = a['addr']
                    print(ip_addr)
                    break
        config_file_pointer.write("ip:"+ip_addr+"\n")
        project_directory = input("Enter the project directory path:")
        project_name = input("Enter the project name:")
        config_file_pointer.write("Source:"+project_directory+"\n")
        config_file_pointer.write("Project-Name:"+project_name)
        config_file_pointer.close()
    def get_ip_windows():
        iface_guids = netifaces.interfaces()
        iface_names = ['(unknown)' for i in range(len(iface_guids))]
        reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
        reg_key = wr.OpenKey(reg, 'SYSTEM\\CurrentControlSet\\Control\\Network\\{4d36e972-e325-11ce-bfc1-08002be10318}')
        for i in range(len(iface_guids)):
            try:
                reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + '\\Connection')
                iface_names[i] = wr.QueryValueEx(reg_subkey, 'Name')[0]
            except FileNotFoundError:
                pass
        i = 0 
        for item in iface_names:
            i = i+1
            if "Local" in item:
                a = netifaces.ifaddresses(iface_guids[i])
                if len(a)>1:
                    a = a[2]
                    a = a[0]
                    ip_addr = a['addr']
                    break
        return ip_addr
    def thread_ripper_windows(ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        status = s.connect_ex((ip,1337))
        if status == 0:
            f = open("ip.txt","w")
            f.write(ip)
        else:
            pass
    def run_scan_windows():
        i = 1
        ip = get_ip_windows()
        ip = ip.split(".")
        ip = ip[0]+"."+ip[1]+"."+ip[2]+"."
        while i<256:
            ip_temp = ip+str(i)
            i=i+1
            t = threading.Thread(target=thread_ripper_windows,args=(ip_temp,))
            t.start()
            ip_temp = ""
    def start_http():
        conf = open(homedir,"r")
        data = conf.readlines()
        conf.close()
        data = data[2]
        data = data.replace("Source:","")
        data = data.replace("\n","")
        os.chdir(data)
        print(data)
        os.system("python -m http.server "+str(global_port))
    def client_windows(mode):
        run_scan_windows()
        time.sleep(3)
        if mode == 0:
            while(1):
                print("Press escape to sync the files.")
                a = keyboard.read_key()
                if a =="esc":
                    f = open("ip.txt","r")
                    data = f.read()
                    ip=data
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((data,1337))
                    msg = "HELLO"
                    s.send(msg.encode("utf-8"))
                    data = s.recv(1024)
                    data = data.split(":")
                    os.rmdir(data[0])
    def server_windows():
        print("server started")
        while(1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = get_ip_windows()
            s.bind(('',1337))
            s.listen(5)
            while(1):
                c,addr = s.accept()
                data = c.recv(1024)
                data = str(data)
                data = data[2:len(data)-1]
                if data == "HELLO":
                    conf = open(homedir,"r")
                    data = conf.readlines()
                    conf.close()
                    data = data[3]
                    data = data.replace("\n","")
                    data = data.replace("Project-Name:","")
                    data_send = data+":"+str(global_port)
                    conf = open(homedir,"r")
                    data = conf.readlines()
                    conf.close()
                    data = data[2]
                    data = data.replace("Source:","")
                    data = data.replace("\n","")
                    os.chdir(data)
                    print(os.getcwd())
                    c.send(data_send.encode("utf-8"))
                    print("started")
                    c.close()
                elif data == "CLIPBOARD GET":
                    data = clipboard.paste()
                    c.send(data.encode("utf-8"))
                elif data == "CLIPBOARD PUT":
                    print("Got a clipbaord put request")
                    data = c.recv(4096)
                    data = data[2:len(data)-1]
                    data = str(data)
                    clipboard.copy(data)
                else:
                    ex = "BYEBYE"
                    c.send(ex.encode("utf-8"))
                    c.close()
else:
    def get_ip_linux():
        def_gw_device = netifaces.gateways()['default'][netifaces.AF_INET][1]
        print(def_gw_device)
        iface_guids = netifaces.interfaces()
        i = 0
        for iface in iface_guids:
            i = i+1
            if iface==def_gw_device:
                a = netifaces.ifaddresses(iface)[AF_INET][0]['addr']
                print(a)
        return a
    def thread_ripper_linux(ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        status = s.connect_ex((ip,1337))
        if status == 0:
            f = open("ip.txt","w")
            f.write(ip)
        else:
            pass
    def run_scan_linux():
        i = 1
        ip = get_ip_linux()
        ip = ip.split(".")
        ip = ip[0]+"."+ip[1]+"."+ip[2]+"."
        print(ip)
        while i<256:
            ip_temp = ip+str(i)
            i=i+1
            t = threading.Thread(target=thread_ripper_linux,args=(ip_temp,))
            t.start()
            ip_temp = ""
    def server_linux():
        print("server started")
        while(1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = get_ip_linux()
            s.bind(('',1337))
            s.listen(5)
            while(1):
                c,addr = s.accept()
                data = c.recv(1024)
                data = str(data)
                data = data[2:len(data)-1]
                if data == "HELLO":
                    conf = open(homedir,"r")
                    data = conf.readlines()
                    conf.close()
                    data = data[3]
                    data = data.replace("\n","")
                    data = data.replace("Project-Name:","")
                    data_send = data+":"+str(global_port)
                    conf = open(homedir,"r")
                    data = conf.readlines()
                    conf.close()
                    data = data[2]
                    data = data.replace("Source:","")
                    data = data.replace("\n","")
                    os.chdir(data)
                    print(os.getcwd())
                    c.send(data_send.encode("utf-8"))
                    print("started")
                    c.close()
                elif data == "CLIPBOARD GET":
                    data = clipboard.paste()
                    c.send(data.encode("utf-8"))
                elif data == "CLIPBOARD PUT":
                    data = c.recv(4096)
                    data = data[2:len(data)-1]
                    data = str(data)
                    clipboard.copy(data)
                else:
                    ex = "BYEBYE"
                    c.send(ex.encode("utf-8"))
                    c.close()
    def client_linux(mode):
        run_scan_linux()
        time.sleep(3)
        if mode == 0:
            while(1):
                print("Press escape to sync the files.")
                a = keyboard.read_key()
                if a =="esc":
                    f = open("ip.txt","r")
                    data = f.read()
                    ip=data
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((data,1337))
                    msg = "HELLO"
                    s.send(msg.encode("utf-8"))
                    data = s.recv(1024)
                    data = data.split(":")
                    os.system("rm -rf "+data[0])
                    os.system("mkdir "+data[0])
                    os.chdir(data[0])
                    os.system("pwd")
                    os.system("wget --recursive http://"+ip+":"+data[1]+" -nH -x -q")
        elif mode==1:
            f = open("ip.txt","r")
            data = f.read()
            ip=data
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((data,1337))
            msg = "HELLO"
            s.send(msg.encode("utf-8"))
            data = s.recv(1024)
            data = data.split(":")
            os.system("rm -rf "+data[0])
            os.system("mkdir "+data[0])
            os.chdir(data[0])
            os.system("pwd")
            os.system("wget --recursive http://"+ip+":"+data[1]+" -nH -x -q")
            s.close()
            while(1):
                print("Press escape to get clipboard data or press shift to send it and control to sync all the files ")
                a = keyboard.read_key()
                if a =="esc":
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((ip,1337))
                    msg = "CLIPBOARD GET"
                    #get clipboard of server
                    s.send(msg.encode("utf-8"))
                    data = s.recv(4096)
                    data = str(data)
                    print(data)
                    clipboard.copy(data)
                    s.close()
                elif a=="shift":
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((ip,1337))
                    #post clipboard data to server from client persepective . HEHE
                    msg = "CLIPBOARD PUT"
                    s.send(msg.encode("utf-8"))
                    text = clipboard.paste()
                    s.send(text.encode("utf-8"))
                    s.close()
                elif a=="ctrl":
                    f = open("ip.txt","r")
                    data = f.read()
                    ip=data
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((data,1337))
                    msg = "HELLO"
                    s.send(msg.encode("utf-8"))
                    data = s.recv(1024)
                    data = data.split(":")
                    os.system("wget --recursive http://"+ip+":"+data[1]+" -nH -x -q")
                    s.close()
    #linux shit here
if len(sys.argv)==1:
    print("Upgrade your programming game")
    print("Use this to sync your project files,clipboard,etc")
    print("Usage:python sync.py setup [USE ONLY IF YOU WANT TO RUN IT IN SERVER MODE]")
    print("--server-start-single: This will load the config files and start the sync server")
    print("--run-single: This will run the client")
    print("--run-multi")
    print("Deafaulting to client mode")
elif len(sys.argv)>1:
    if sys.argv[1] == "setup":
        if platform == "win32":
            setup_windows()
        else:
            print("Run linux function")
    elif sys.argv[1] == "server-start":
        if platform == "win32":
            t = threading.Thread(target=start_http)
            t.start()
            server_windows()
        else:
            t = threading.Thread(target=start_http)
            t.start()
            server_linux()
    elif sys.argv[1] == "--run-single":
        if platform == "win32":
            client_windows(1)
        else:
            client_linux(1)
    elif sys.argv[1] == "--run-multi":
        if platform == "win32":
            client_windows(0)
        else:
            client_linux(0)
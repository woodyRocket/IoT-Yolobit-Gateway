# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import sys
# import random
import time
import serial.tools.list_ports
from Adafruit_IO import MQTTClient

AIO_FEED_ID = ["home.sh-humid","home.sh-lumos","home.sh-temp","home.sh-led"]
# home.sh-humid
# home.sh-lumos
# home.sh-temp

AIO_USERNAME = "MDPbuzzin"
AIO_KEY = "aio_hWTR38fNuLyN40YpPQgycAWFTdIe"


def connected(client):
    print("Connected successfully ...")
    for feed in AIO_FEED_ID:
        client.subscribe(feed)


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribed ...")


def disconnected(client):
    print("Disconnected ...")
    sys.exit(1)


def message(client, feed_id, payload):
    print("Input from " + feed_id + " loading: " + payload)
    if isYolobitConnected:
        if (feed_id == "home.sh-led"):
            if payload == "1":
                writeData("LEDON")
            else:
                writeData("LEDOFF")


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB-SERIAL CH340" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort


# ser = serial.Serial(port=getPort(), baudrate=115200)
isYolobitConnected = False
if getPort() != "None":
    ser = serial.Serial(port=getPort(), baudrate=115200)
    isYolobitConnected = True


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    if splitData[1] == "TEMP":
        client.publish("home.sh-temp", splitData[2])
    elif splitData[1] == "HUMI":
        client.publish("home.sh-humid",splitData[2])
    elif splitData[1] == "LUMO":
        client.publish("home.sh-lumos",splitData[2])
    elif splitData[1] == "MOVE":
        client.publish("home.sh-moved",splitData[2])


mess = ""


def readSerial():
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        global mess
        mess += ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end + 1:]


def writeData(data):
    ser.write((str(data) + "#").encode())


while True:
    # value = random.randint(0, 100)
    # print("Updating: ", value)
    # client.publish(AIO_TEMP_ID, value)
    if isYolobitConnected:
        readSerial()
    time.sleep(1)

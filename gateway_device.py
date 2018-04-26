import RPi.GPIO as GPIO
import time
import datetime
import bluetooth
from logentries import LogentriesHandler
import logging
import paho.mqtt.client as mqtt

received_data = ""

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("topic/test")


def on_message(client, userdata, msg):
    global received_data
    received_data = msg.payload.decode()


client = mqtt.Client()
client.connect("192.168.0.12", 1883, 120)

client.on_connect = on_connect
client.loop_start()
startTime = datetime.datetime.utcnow()

error = 0


server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

port = 1
server_sock.bind(("",port))
server_sock.listen(1)

log = logging.getLogger('logentries')
log.setLevel(logging.INFO)

log.addHandler(LogentriesHandler('d867b896-24ed-49f1-958d-1548da94e8e7'))


client_sock,address = server_sock.accept()
print "Accepted connection from ",address


# for i in range(0, 3600):
#     data.append(GPIO.input(4))



def bin2dec(string_num):
    return str(int(string_num, 2))

def bin2float(string_num):
    return str(float(int(string_num, 2)))



def read():
    data = []

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    GPIO.output(4, GPIO.HIGH)
    time.sleep(0.025)
    GPIO.output(4, GPIO.LOW)
    time.sleep(0.02)

    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for i in range(0, 3600):
        data.append(GPIO.input(4))

    bit_count = 0
    tmp = 0
    count = 0
    HumidityBit = ""
    TemperatureBit = ""
    crc = ""

    try:
        while data[count] == 1:
            tmp = 1
            count = count + 1

        for i in range(0, 32):

            bit_count = 0

            while data[count] == 0:
                tmp = 1
                count = count + 1

            while data[count] == 1:
                bit_count = bit_count + 1
                count = count + 1

            if bit_count > 16:
                if i >= 0 and i < 8:
                    HumidityBit = HumidityBit + "1"
                if i >= 16 and i < 24:
                    TemperatureBit = TemperatureBit + "1"
            else:
                if i >= 0 and i < 8:
                    HumidityBit = HumidityBit + "0"
                if i >= 16 and i < 24:
                    TemperatureBit = TemperatureBit + "0"

    except:

        time.sleep(3)
        read()

        # exit(0)

    try:
        for i in range(0, 8):
            bit_count = 0

            while data[count] == 0:
                tmp = 1
                count = count + 1

            while data[count] == 1:
                bit_count = bit_count + 1
                count = count + 1

            if bit_count > 16:
                crc = crc + "1"
            else:
                crc = crc + "0"
    except:

        time.sleep(3)
        read()


        # print "ERR_RANGE"
        # exit(0)

    current_humidity = bin2dec(HumidityBit)
    current_temperature = bin2float(TemperatureBit)


    # Disabling this check because it returns false always. Might be a problem with the hardware.

    # if float(Humidity) + float(Temperature) - int(bin2dec(crc)) == 0:
    #     print "Humidity:" + Humidity + "%"
    #     print "Temperature:" + Temperature + "C"
    # else:
    #     print "ERR_CRC"


    current_time = str(datetime.datetime.utcnow())

    # print "Temperature = " + current_temperature + ", " + "Humidity = " + current_humidity + "%"
    # report = ""
    # if int(current_temperature) > 18 and int(current_temperature) < 22 and int(current_humidity) < 80:

    report = current_time + " SensorID = Burhanuddin" + " Temperature = " + current_temperature + ", " + "Humidity = " + current_humidity


    # print(report)

    return report

    # a = open('Log.txt','a')
    # a.write(report + '\n')
    # a.close()


while True:

    current_data = read()
    print current_data

    currentTime = datetime.datetime.utcnow()
    difference = (currentTime - startTime).total_seconds()


    if difference < 120:

        client.on_message = on_message


    elif difference >= 120 and difference < 240:

        received_data = client_sock.recv(1024)

    else:

        startTime = currentTime

    print received_data

    log.info(current_data)
    log.info(received_data)

    time.sleep(5)





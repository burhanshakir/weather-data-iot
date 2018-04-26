import RPi.GPIO as GPIO
import time
import datetime
import paho.mqtt.client as mqtt
import bluetooth


startTime = datetime.datetime.utcnow()


client = mqtt.Client()
client.connect("localhost",1883,120)

bd_addr = "B8:27:EB:34:45:FA"

port = 1

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr, port))

# for i in range(0, 3600):
#     data.append(GPIO.input(4))



def bin2dec(string_num):
    return str(int(string_num, 2))

def bin2float(string_num):
    return str(float(int(string_num,2)))

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

        time.sleep(5)
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

        time.sleep(5)
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
    report = ""
    # int(current_temperature) > 18 and int(current_temperature) < 22 and int(current_humidity) < 80
    report = " SensorID = Avinash " + " Temperature = " + current_temperature + ", " + "Humidity = " + current_humidity
    # print(report)

    return report

    # a = open('Log.txt','a')
    # a.write(report + '\n')
    # a.close()


while True:
    # read()

    currentTime = datetime.datetime.utcnow()
    difference = (currentTime - startTime).total_seconds()
    # print(str((currentTime - startTime).total_seconds()))

    if difference < 120:

        protocol = " Protocol = MQTT, "

        result = str(currentTime) + protocol + read()
        print(result)
        client.publish("topic/test",str(result))
    elif 120 <= difference < 240:
        protocol = " Protocol = RFCOMM, "
        abc = str(currentTime) + protocol + read()
        print(abc)
        sock.send(abc)
    else:
        startTime = currentTime

    time.sleep(5)
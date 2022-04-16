#!/usr/bin/env python3
import serial
import time

from Crypto.Cipher import AES
from binascii import hexlify, unhexlify

from threading import Thread
import paho.mqtt.client as mqtt

from decouple import config

isConnected = False;
isConnecting = False;

ivPart1 = '2D4C00000000010E'
lastRead = 0

aesStr = None           # AES-Key der EnergieAG 
readEveryXSecs = 7      # Alle z.B. 7 Sekunden Werte auswerten
mqttHost = None         # IP Adresse des MQTT Brokers
mqttPort = None         # MQTT Port
mqttQOS = None          # MQTT QOS
mqttClientID = None     # ID des Clients (Freitext)
mqttTopic = None        # Topic in das die Werte publiziert werden sollen
mqttUser = None         # MQTT Benutzername
mqttPass = None         # MQTT Kennwort

TTY_PATH = None
TTY_BAUD = None
TTY_BYTES = None
TTY_PARITY = None
TTY_STOPBITS = None
TTY_TIMEOUT = None

def setConfigVars():
    global aesStr
    global readEveryXSecs
    global mqttHost, mqttPort, mqttQOS, mqttClientID, mqttTopic, mqttUser, mqttPass
    global TTY_PATH, TTY_BAUD, TTY_BYTES, TTY_PARITY, TTY_STOPBITS, TTY_TIMEOUT
    
    aesStr = config('AES_PASSWORD', cast=str)
    readEveryXSecs = config('READ_EVERY_X_SECONDS', cast=int)
    mqttHost = config('MQTT_HOST', cast=str)
    mqttPort = config('MQTT_PORT', cast=int)
    mqttQOS = config('MQTT_QOS', cast=int)
    mqttClientID = config('MQTT_CLIENTID', cast=str)
    mqttTopic = config('MQTT_TOPIC', cast=str)
    mqttUser = config('MQTT_USER', cast=str)
    mqttPass = config('MQTT_PASS', cast=str)
    TTY_PATH = config('TTY_PATH', cast=str)
    TTY_BAUD = config('TTY_BAUD', cast=int)
    TTY_BYTES = config('TTY_BYTES', cast=int)
    TTY_PARITY = config('TTY_PARITY', cast=str)
    TTY_STOPBITS = config('TTY_STOPBITS', cast=int)
    TTY_TIMEOUT = config('TTY_TIMEOUT', cast=int)

def getReverseHexValue(array, start, bytesToRead):
    wertArr = array[start: start+bytesToRead]
    wertArr.reverse()
    return wertArr
    
#
# datenArrayVonZaehler ist ein Array mit "Hexwerten" (in lesbaren bytes)
#    
def satzAuswerten(datenArrayVonZaehler):

    try:
        #print(datenArrayVonZaehler)
        encStr = ''.join(map(str, datenArrayVonZaehler[19:-2]))
        ivPart2 = datenArrayVonZaehler[15] + datenArrayVonZaehler[15] + datenArrayVonZaehler[15] + datenArrayVonZaehler[15] + datenArrayVonZaehler[15] + datenArrayVonZaehler[15] + datenArrayVonZaehler[15] + datenArrayVonZaehler[15]
        #print(encStr)
        ivStr = ivPart1 + ivPart2
        #print(ivKey)
        
        aesHex = unhexlify(aesStr)
        ivHex = unhexlify(ivStr)
        encHex = unhexlify(encStr)

        cipher = AES.new(aesHex, AES.MODE_CBC, ivHex)
        ciphertext = cipher.decrypt(encHex)
        decryptedBytes = hexlify(ciphertext)
        decryptedStr = decryptedBytes.decode()

        inhaltArr = []
        for i in range(0, len(decryptedStr)-2, 2):
            inhaltArr.append(decryptedStr[i:i+2])

        # Gesamtleistung
        wertHex = getReverseHexValue(inhaltArr, 12, 4);
        energieAp = int(''.join(wertHex), base=16)/1000
        print("#1 (Energie A+) aktuelle kWh: ",energieAp)
        
        wertHex = getReverseHexValue(inhaltArr, 19, 4);
        energieAm = int(''.join(wertHex), base=16)/1000
        print("#2 (Energie A-): ",energieAm)
        
        wertHex = getReverseHexValue(inhaltArr, 28, 4);
        energieRp = int(''.join(wertHex), base=16)
        print("#3 (Energie R+): ",energieRp)
        
        wertHex = getReverseHexValue(inhaltArr, 38, 4);
        energieRm = int(''.join(wertHex), base=16)
        print("#4 (Energie R-): ",energieRm)
        
        wertHex = getReverseHexValue(inhaltArr, 44, 4);
        wirkleistungPp = int(''.join(wertHex), base=16)
        print("#5 (Wirkleistung P+): ",wirkleistungPp)
        
        wertHex = getReverseHexValue(inhaltArr, 51, 4);
        wirkleistungPm = int(''.join(wertHex), base=16)
        print("#6 (Wirkleistung P-): ",wirkleistungPm)
        
        wertHex = getReverseHexValue(inhaltArr, 58, 4);
        blindleistungQp = int(''.join(wertHex), base=16)
        print("#7 (Blindleistung Q+): ",blindleistungQp)
        
        wertHex = getReverseHexValue(inhaltArr, 66, 4);
        blindleistungQm = int(''.join(wertHex), base=16)
        print("#8 (Blindleistung Q-): ",blindleistungQm)
        
        wertHex = getReverseHexValue(inhaltArr, 74, 4);
        inkasso = int(''.join(wertHex), base=16)
        print("#9 (Inkasso): ",inkasso)
        
        print('-----------------------------------------------')
        
        client.publish(mqttTopic+'EnergieAp', energieAp, qos=mqttQOS)
        client.publish(mqttTopic+'EnergieAm', energieAm, qos=mqttQOS)
        client.publish(mqttTopic+'EnergieRp', energieRp, qos=mqttQOS)
        client.publish(mqttTopic+'EnergieRm', energieRm, qos=mqttQOS)
        client.publish(mqttTopic+'WirkleistungPp', wirkleistungPp, qos=mqttQOS)
        client.publish(mqttTopic+'WirkleistungPm', wirkleistungPm, qos=mqttQOS)
        client.publish(mqttTopic+'BlindleistungQp', blindleistungQp, qos=mqttQOS)
        client.publish(mqttTopic+'BlindleistungQm', blindleistungQm, qos=mqttQOS)
        client.publish(mqttTopic+'Inkasso', inkasso, qos=mqttQOS)
                    
        return 1
    except:
        print('Fehler beim Auswerten der Daten')
        return None
    

if __name__ == '__main__':

    setConfigVars()

    #print('Verbinde zu ' + mqttHost + ':' + str(mqttPort) + ' als ' + mqttUser + ' mit Passwort ' + mqttPass + ' ClientID: ' + mqttClientID)
    
    client = mqtt.Client(client_id=mqttClientID)
    client.username_pw_set(mqttUser, mqttPass)
    client.connect(mqttHost, mqttPort)
    
    #ser = serial.Serial('/dev/ttyAMA0', 300, timeout=1)
    #ser.reset_input_buffer()
    #ser.write(b"/?!\r\n")
    #ser.write(b"\x06\x30\x35\x31\x0D\x0A\x06050\r\n")
    ser = serial.Serial(TTY_PATH, baudrate=TTY_BAUD, bytesize=TTY_BYTES, parity=TTY_PARITY, stopbits=TTY_STOPBITS, timeout=TTY_TIMEOUT)
    ser.reset_input_buffer()
    
    print("Warte auf Verbindungsmöglichkeit")
    
    while True:
        if ser.inWaiting() > 0:
            print("anstehende Länge: ", ser.inWaiting())
            
            #if not isConnected: 
            
            if ser.inWaiting() == 5: 
                # sieht nach Verbindungsmöglichkeit aus
                line = ser.readline()
                if line.hex() == '1040f03016':
                    isConnected = False
                    print("versuche, in Kommunikation einzuhaken ...")
                    #time.sleep(0.2)
                    ser.write(b'\xe5')
                    time.sleep(1)
                    continue
                    
            if not isConnected:
                if ser.inWaiting() < 5:
                    # da muss noch mehr kommen - Zeit geben und nochmal versuchen
                    #ser.reset_input_buffer()
                    print(ser.inWaiting())
                    time.sleep(0.2)
                    continue
                else:
                    # mehr Daten = es kommt etwas = verbunden!
                    print("verbunden!")
                    isConnected = True
                    
                
                
            if ser.inWaiting() == 101: 
                if time.perf_counter() - lastRead > readEveryXSecs:
                    arr = []
                    while ser.inWaiting() > 0:
                        arr.append(ser.read().hex())
                    
                    t = Thread(target=satzAuswerten, args=(arr,))
                    t.start()
                    #satzAuswerten(arr)
                    lastRead = time.perf_counter()

                time.sleep(0.2)
                ser.reset_input_buffer()
                ser.write(b'\xe5')
                
            else:
            
                # Daten einfach wegschmeißen - kommen schon wieder
                ser.reset_input_buffer()
                
                # trotzdem bestätigen, damit die Verbindung nicht wegbricht
                ser.write(b'\xe5')
                
                #if ser.inWaiting() >= 101:
                #    ser.reset_input_buffer()
                #else:
                #    time.sleep(0.2)
                #    continue
        time.sleep(0.2)
        client.loop()
        
        
    
    

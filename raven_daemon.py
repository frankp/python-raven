#!/usr/bin/python
import logging
import time
import serial
import xml.etree.ElementTree as ET
import mosquitto

#third party libs
from daemon import runner

class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/raven.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        while True:
            #Main code goes here ...
            try:
                ser = serial.Serial("/dev/serial/by-id/usb-Rainforest_RFA-Z106-RA-PC_RAVEn_v2.3.21-if00-port0",115200, timeout=0.5)
            except Exception as e:
                logger.error(e)
                exit()

            logger.info("connected to: " + ser.portstr)
            logger.info("Sending Command to RAVEN: " + ser.portstr)
            ser.write("<Command><Name>get_instantaneous_demand</Name></Command>")
            client = mosquitto.Mosquitto("test-client")
            client.connect("10.54.0.20")

            while True:
                data = ser.read(1000)
                if len(data) > 0:
                    try:
                        tree = ET.fromstring(data)
                        Demand = float(int(tree.find('Demand').text,16))
                        Divisor = float(int(tree.find('Divisor').text,16))
                        Multiplier = float(int(tree.find('Multiplier').text,16))
                        logger.info("Demand: " + str(Demand) + ", Divisor: " + str(Divisor) + ", Multiplier: " + str(Multiplier))
                        fDemand = float( Demand / Divisor)
                        logger.info("Demand: " + str(fDemand))
                        client.publish("home/energy/demand", str(fDemand), 1)
                    except Exception as e:
                            logger.error(e)
                    time.sleep(5)

app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/raven.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()
#!/usr/bin/env python

import sys
import serial
import time
import xml.etree.ElementTree as ET
import re
import mosquitto
import logging as log

####################

# serDevice = "/dev/serial/by-id/usb-Rainforest_RFA-Z106-RA-PC_RAVEn_v2.3.21-if00-port0"
serDevice = "/dev/ttyUSB0"

# mozIP = "10.54.0.20"
mozIP = "127.0.0.1"

####################

# Logging setup
log.basicConfig(filename='raven.log',level=log.DEBUG)

# Various Regex's
reStartTag = re.compile('^<[a-zA-Z0-9]+>') # to find a start XML tag (at very beginning of line)
reEndTag = re.compile('^<\/[a-zA-Z0-9]+>') # to find an end XML tag (at very beginning of line)

def sendCommand(serialport, command):
  '''Given a command it will be formatted in XML and written to serialport for RAVEn device'''
  # Sends a simple command, such as initialize, get_instantaneous_demand, etc.
  output = ("<Command>\n  <Name>%s</Name>\n</Command>" % command)
  log.info("Issuing command: " + command
  serialport.write(output)
  time.sleep(0.5) # allow this command to sink in

def getCurrentSummationKWh(xmltree):
  '''Returns a single float value for the SummationDelivered from a Summation response from RAVEn'''
  # Get the Current Summation (Meter Reading)
  fReading = float(int(xmltree.find('SummationDelivered').text,16))
  fResult = calculateRAVEnNumber(xmltree, fReading)
  return formatRAVEnDigits(xmltree, fResult)

def getInstantDemandKWh(xmltree):
  '''Returns a single float value for the Demand from an Instantaneous Demand response from RAVEn'''
  # Get the Instantaneous Demand
  fDemand = float(int(xmltree.find('Demand').text,16))
  fResult = calculateRAVEnNumber(xmltree, fDemand)
  return formatRAVEnDigits(xmltree, fResult)

def calculateRAVEnNumber(xmltree, value):
  '''Calculates a float value from RAVEn using Multiplier and Divisor in XML response'''
  # Get calculation parameters from XML - Multiplier, Divisor
  fDivisor = float(int(xmltree.find('Divisor').text,16))
  fMultiplier = float(int(xmltree.find('Multiplier').text,16))
  if (fMultiplier > 0 and fDivisor > 0):
    fResult = float( (value * fMultiplier) / fDivisor)
  elif (fMultiplier > 0):
    fResult = float(value * fMultiplier)
  else: # (Divisor > 0) or anything else
    fResult = float(value / fDivisor)
  return fResult

def formatRAVEnDigits(xmltree, value):
  '''Formats a float value according to DigitsRight, DigitsLeft and SuppressLeadingZero settings from RAVEn XML response'''
  # Get formatting parameters from XML - DigitsRight, DigitsLeft
  iDigitsRight = int(xmltree.find('DigitsRight').text,16)
  iDigitsLeft = int(xmltree.find('DigitsLeft').text,16)
  sResult = ("{:0%d.%df}" % (iDigitsLeft+iDigitsRight+1,iDigitsRight)).format(value)
  # Suppress Leading Zeros if specified in XML
  if xmltree.find('SuppressLeadingZero').text == 'Y':
    while sResult[0] == '0':
      sResult = sResult[1:]
  return sResult

# Callback for MQTT Client
#TODO: This isn't working??
def onMosquittoConnect(rc):
  '''Callback for Mosquitto connection - not working at the moment!'''
  if rc == 0:
    print "connected to MQTT ok"

def main():
  # open serial port
  ser = serial.Serial(serDevice, 115200, serial.EIGHTBITS, serial.PARITY_NONE, timeout=0.5)
  try:
    ser.open()
    ser.flushInput()
    ser.flushOutput()
    print("connected to: " + ser.portstr)
  except Exception as e:
    print "cannot open serial port: " + str(e)
    exit()
  
  # send initialize command to RAVEn (pg.9 of XML API Doc)
  #TODO: For some reason this command causes the error "Unknown command"?
  #sendCommand(ser, "initialise" )

  # setup mosquitto connection
  moz = mosquitto.Mosquitto("raven-usb-dongle", True)
  moz.on_connect = onMosquittoConnect
  moz.connect(mozIP)

  # Other commands to play with in the future!
  #sendCommand(ser, "get_meter_info")
  #sendCommand(ser, "get_connection_status")

  rawxml = ""

  while True:
    # wait for /n terminated line on serial port (up to timeout)
    rawline = ser.readline()
    log.debug("Received string from serial: [[" + rawline + "]]")
    # remove null bytes that creep in immediately after connecting
    rawline = rawline.strip('\0')
    # only bother if this isn't a blank line
    if len(rawline) > 0:
      # start tag
      if reStartTag.match(rawline):
        rawxml = rawline
        log.debug("Start XML Tag found: " + rawline)
      # end tag
      elif reEndTag.match(rawline):
        rawxml = rawxml + rawline
        log.debug("End XML Tag Fragment found: " + rawline)
        try:
          xmltree = ET.fromstring(rawxml)
          #TODO: Eventually move this branching tree into a function or lookup table
          if xmltree.tag == 'CurrentSummationDelivered':
            moz.publish("home/energy/summation", getCurrentSummationKWh(xmltree), 1)
            print getCurrentSummationKWh(xmltree)
          elif xmltree.tag == 'InstantaneousDemand':
            moz.publish("home/energy/demand", getInstantDemandKWh(xmltree), 1)
            print getInstantDemandKWh(xmltree)
          else:
            log.warning("*** Unrecognised (not implemented) XML Fragment")
            log.warning(rawxml)
        except Exception as e:
          log.error("Exception triggered: " + str(e))
        # reset rawxml
        rawxml = ""
      # if it starts with a space, it's inside the fragment
      else:
        rawxml = rawxml + rawline
        log.debug("Normal inner XML Fragment: " + rawline)
    else:
      log.debug("Skipped")

  #TODO: never gets called?
  ser.close()

if __name__ == '__main__':
  main()

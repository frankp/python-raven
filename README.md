
Overview
========

This little project is just some musings around getting some readings from a Smart Electricity Meter via a small USB device that is using Zigbee and parsing and publishing the resulting data via a Mosquitto server (MQTT).

It is the first foray into exploring much further into being able to get various bits and pieces talking in the home, for the ultimate purpose of saving energy - or just having fun trying to anyway.

Resources
=========

Here are some links from around the place connected or used with this project:

RAVEn USB Smart Meter Device
----------------------------
Product information on the RAVEn(tm) Radio Adapter for Viewing Energy:
http://fastnetworks.com.au/index.php/rainforestautomation/raven-ihd

Technical information on how to get the USB device talking with Linux:
http://www.ftdichip.com/Support/Documents/TechnicalNotes/TN_101_Customising_FTDI_VID_PID_In_Linux%28FT_000081%29.pdf

The XML API Documentation for communicating with it:
http://www.rainforestautomation.com/sites/default/files/download/rfa-z106/raven_xml_api_r127.pdf

Mosquitto Message Broker - MQTT
-------------------------------
An introduction to what MQTT is and how it might be useful for home automation stuff in the future:
http://en.wikipedia.org/wiki/MQ_Telemetry_Transport

The open source MQTT message broker implementation we are using (on Ubuntu):
http://mosquitto.org/ and the Python library http://mosquitto.org/documentation/python/

Python Stuff
------------
Talking to Serial devices:
http://pyserial.sourceforge.net/pyserial_api.html


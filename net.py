import os
import sys
import clr
import SensorDroidPlot

mainPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

dllFileName = 'TarCo.SensorDroid.dll'
# dllFolder = mainPath + '\SensorDroid\\'

# print(dllFolder+dllFileName)

sys.path.append(dllFolder)
clr.AddReference(dllFileName)
from TarCo.SensorDroid import Client # pylint: disable=unused-import

import SensorDroidPlot # pylint: disable=unused-import

cliPlot = SensorDroidPlot.ClientPlot()

def ConnectionUpdatedEventHandler(sender, e):
    if e is not None:
        if e.Connected:
            print("Connected")
        else:
            print("Disonnected")

def SensorsReceivedEventHandler(sender, e):
    global plotSensors
    plotSensors = True
#
# def CameraReceivedEventHandler(sender, e):
#     global showImage
#     showImage = True


client = Client("Any")

client.ConnectionUpdated += ConnectionUpdatedEventHandler
client.SensorsReceived += SensorsReceivedEventHandler
# client.ImageReceived += CameraReceivedEventHandler

client.SensorsSampleRate = 100
# client.CameraResolution = 15

client.Connect()

plotSensors = False
showImage = False

while True:
    if client.Connected:
        if plotSensors and client.DataCurrent is not None:
            cliPlot.plotSensors(client.DataCurrent)
            plotSensors = False
        # if showImage and client.Image is not None:
        #     cliPlot.showImage(client.Image.Data)
        #     showImage = False

input("Press ENTER to exit")

client.Close()

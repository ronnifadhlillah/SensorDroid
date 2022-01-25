import asyncore
import socket
import threading
import time
import os

# SensorDroid Client Python.
# Thank you for tarCo for providing the core.

class Client:

    @property
    def connected(self):
        return self._connected
    @connected.setter
    def connected(self, value):
        self._connected = value

    @property
    def address(self):
        return self._address
    @address.setter
    def address(self, value):
        self._address = value

    @property
    def name(self):
        return self._name

    @property
    def info(self):
        return self._info

    @property
    def controlling(self):
        return self._controlling

    @property
    def ipLocal(self):
        return self._ipLocal

    __portBaseDefault = 53121
    __sensorsPortDevice = 0
    __cameraPortDevice = 0

    @property
    def channel(self):
        return self._channel
    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            if value == -2:
                self.checkConnect();
            if value == -1:
                self._sensorsPort = 0;
                self._cameraPort = 0;
                self.checkConnect();
            elif value >= 0:
                sensorsPortT, cameraPortT = self.getPorts(value);
                self.connectSensors(sensorsPortT)
                self.connectCamera(cameraPortT)

    @property
    def sensorsPort(self):
        return self.__sensorsPortDevice
    @sensorsPort.setter
    def sensorsPort(self, value):
        self._sensorsPort = value
        self.channel = -2

    @property
    def sensorsPort(self):
        return self.__sensorsPortDevice
    @sensorsPort.setter
    def sensorsPort(self, value):
        self._sensorsPort = value
        self.channel = -2

    @property
    def cameraPort(self):
        return self.__cameraPortDevice
    @cameraPort.setter
    def cameraPort(self, value):
        self._cameraPort = value

    @property
    def sensorsSampleRate(self):
        return self._sensorsSampleRate
    @sensorsSampleRate.setter
    def sensorsSampleRate(self, value):
        self._sensorsSampleRate = value

    @property
    def cameraResolution(self):
        return self._cameraResolution
    @cameraResolution.setter
    def cameraResolution(self, value):
        self._cameraResolution = value

    @property
    def discoveredDevices():
        return Client._discoveredDevices

    @property
    def devicesDiscovered():
        return Client._devicesDiscovered

    @devicesDiscovered.setter
    def devicesDiscovered(value):
        Client._devicesDiscovered.removeAt(0)
        Client._devicesDiscovered.append(value)

    @property
    def connectionUpdated(self):
        return self._connectionUpdated
    @connectionUpdated.setter
    def connectionUpdated(self, value):
        self._connectionUpdated.removeAt(0)
        self._connectionUpdated.append(value)

    @property
    def sensorsReceived(self):
        return self._sensorsReceived
    @sensorsReceived.setter
    def sensorsReceived(self, value):
        self._sensorsReceived.removeAt(0)
        self._sensorsReceived.append(value)

    @property
    def imageReceived(self):
        return self._imageReceived
    @imageReceived.setter
    def imageReceived(self, value):
        self._imageReceived.removeAt(0)
        self._imageReceived.append(value)

    @property
    def dataCurrent(self):
        return self._dataCurrent

    @property
    def image(self):
        return self._image

    _name = None
    _info = None
    _controlling = None
    _discoveredDevices = None
    _dataCurrent = None
    _image = None

    __udpDiscovery = None
    __udpMain = None
    __udpSensors = None
    __udpCamera = None

    __ipLocalDiscovery = None

    __clients = []


    def __init__(self, address):

        self.connected = False
        self.address = address
        self._ipLocal = Client.getLocalIP(address)

        self._channel = -1
        self._sensorsPort = 0;
        self._cameraPort = 0;
        self.checkConnect()

        self.sensorsSampleRate = 100
        self.cameraResolution = 13

        self._connectionUpdated = Event()
        self._connectionUpdated()

        self._sensorsReceived = Event()
        self._sensorsReceived()

        self._imageReceived = Event()
        self._imageReceived()

        Client.__clients.append(self)

    @staticmethod
    def getLocalIP(address):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((address, 1))
            IP = s.getsockname()[0]
        except:
            try:
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except:
                IP = ''
        finally:
            s.close()
        return IP

    @staticmethod
    def devicesDiscoveredHandler(addr, data):
        dataMain = data.decode('utf-8')
        if "SensorDroidDevice" in dataMain:
            if addr not in Client._discoveredDevices:
                 Client._discoveredDevices.append(addr)
                 Client.devicesDiscovered(Client._discoveredDevices)



    def getMainMsg(self):

        msg = ""
        msg += "@connect$" + str(1)
        msg += "@clientName$" + socket.gethostname()
        msg += "@clientIP$" + self.ipLocal
        msg += "@sensorsSampleRate$" + str(self.sensorsSampleRate)
        msg += "@cameraResolution$" + str(self.cameraResolution)

        #msg += "@timestamp$" + millisStr;
        #msg += "@deviceLatency$" + Latency.LatencyClient.ToString("0");
        #msg += "@clientInfo$" + "";
        msg += "@sensorsPort$" + str(self._sensorsPort);
        msg += "@cameraPort$" + str(self._cameraPort);

        return msg

    def connectionUpdatedHandler(self, addr, data):
        dataMain = data.decode('utf-8')
        if self.connected !=  self.__udpMain.connected:
            self.connected = self.__udpMain.connected
            self.connectionUpdated(self, dataMain)
        self.__udpMain.send(self.getMainMsg())

        self._info = ""

        dataMainM = dataMain.split("@")
        for i in range(0, len(dataMainM)):
            try:
                dataMainA = dataMainM[i].split("$")

                if len(dataMainA) > 1:
                    if dataMainA[0] == "deviceName":
                        self._info += dataMainA[1]

                if len(dataMainA) > 1:
                    if dataMainA[0] == "deviceModel":
                        self._name = dataMainA[1]

                if len(dataMainA) > 1:
                    if dataMainA[0] == "deviceOS":
                        self._info += " - " + dataMainA[1]

                if len(dataMainA) > 1:
                    if dataMainA[0] == "mainClient":
                        if self.address in dataMainA[1]:
                            self._controlling = True
                        else:
                            self._controlling = False

                if not self._controlling:
                    if len(dataMainA) > 1:
                        if dataMainA[0] == "sensorsPort":
                            self.__sensorsPortDevice = int(dataMainA[1])
                            if self._sensorsPort != self.__sensorsPortDevice:
                                self.connectSensors(self.__sensorsPortDevice)

                    if len(dataMainA) > 1:
                        if dataMainA[0] == "cameraPort":
                            self.__cameraPortDevice = int(dataMainA[1])
                            if self._cameraPort != self.__cameraPortDevice:
                                self.connectCamera(self.__cameraPortDevice)

                pass

            except Exception as e:
                pass

        pass

    def sensorsReceivedHandler(self, addr, data):
        self._dataCurrent = SensorsData(data.decode('utf-8'))
        self.sensorsReceived(self, self.dataCurrent)

    def imageReceivedHandler(self, addr, data):
        self._image = data[14:]
        self.imageReceived(self, self.image)

    @staticmethod
    def startDiscovery(address="Any"):
        if (Client.__udpDiscovery == None):
            Client.__ipLocalDiscovery = Client.getLocalIP(address)
            Client.__udpDiscovery = AsyncoreSocketUDP(Client.__ipLocalDiscovery, "Any", 53120)
            Client.__udpDiscovery.isCheck = True
            Client.__udpDiscovery.dataRcvEvent.append(Client.devicesDiscoveredHandler)

            Client._discoveredDevices =[]

            loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
            loop_thread.daemon = True
            loop_thread.start()

    def connect(self):
        isAsync = True

        if isAsync:
            self.__udpMain = AsyncoreSocketUDP(self.ipLocal, self.address, self.__portBaseDefault)
            self.__udpMain.isCheck = True
            self.__udpMain.dataRcvEvent.append(self.connectionUpdatedHandler)

            self.checkConnect()

            loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
            loop_thread.daemon = True
            loop_thread.start()

        else:
            self.__udpMain = UDP(self.ipLocal, self.address, self.__portBaseDefault)
            self.__udpMain.start()

            while self.__udpMain.Connected:
                self.__udpMain.send(self.getMainMsg())
                self.__udpMain.receive()

            self.__udpSensors = UDP(self.ipLocal, self.address, self.sensorsPort)
            self.__udpSensors.start()

            self.__udpCamera = UDP(self.ipLocal, self.address, self.cameraPort)
            self.__udpCamera.start()

            while True:
                time.sleep(0.001)

                self.__udpMain.send(self.getMainMsg())
                self.__udpMain.receive()
                if self.__udpMain.data is not None:
                    self.__udpMain.data = None

                self.__udpSensors.send("1")
                self.__udpSensors.receive()
                if self.__udpSensors.data is not None:
                    dataCurrent = SensorsData(self.__udpSensors.data.decode('utf-8'))
                    self.sensorsReceived(dataCurrent)
                    self.__udpSensors.data = None

                self.__udpCamera.send("1")
                self.__udpCamera.receive()
                if self.__udpCamera.data is not None:
                    self.imageReceived(self.u__udpCamera.data[14:])
                    self.__udpCamera.data = None

    def checkConnect(self):
            self.checkPortsAutomatic();

            if self._sensorsPort > 0:
                self.connectSensors(self._sensorsPort)

            if self._cameraPort > 0:
                self.connectCamera(self._cameraPort)

    def checkPortsAutomatic(self):
        if self.channel == -1 and self._sensorsPort == 0 and self._cameraPort == 0:
            for i in range(0, 999):
                sensPort, camPort = self.getPorts(i)
                sensorsPortT, cameraPortT = self.getPorts(i);
                found = self.find(lambda x: x.port == sensorsPortT or x.port == cameraPortT, AsyncoreSocketUDP.listSockets)
                if found == None:
                    self.connectSensors(sensorsPortT)
                    self.connectCamera(cameraPortT)
                    break

    def find(self, pred, coll):
        for x in coll:
            if pred(x):
                return x

    def getPorts(self, channel):
        return (self.__portBaseDefault + 1) + 2 * (channel), (self.__portBaseDefault + 2) + 2 * (channel)

    def connectSensors(self, port):
        if port == 0:
            port = self.__portBaseDefault + 1

        if self.__udpSensors == None or (port > 0 and self._sensorsPort != port):
            if self.__udpSensors != None:
                self.__udpSensors.stop()
            self.__udpSensors = AsyncoreSocketUDP(self.ipLocal, self.address, port)
            self.__udpSensors.dataRcvEvent.append(self.sensorsReceivedHandler)
            self._sensorsPort = port

    def connectCamera(self, port):
        if port == 0:
            port = self.__portBaseDefault + 2

        if self.__udpCamera == None or (port > 0 and self._cameraPort != port):
            if self.__udpCamera != None:
                self.__udpCamera.stop()
            self.__udpCamera = AsyncoreSocketUDP(self.ipLocal, self.address, port)
            self.__udpCamera.dataRcvEvent.append(self.imageReceivedHandler)
            self._cameraPort = port


    def close(self):
        self.connected = False
        self.__udpMain.stop()
        self.__udpSensors.stop()
        self.__udpCamera.stop()

    def closeAll():
        for cli in Client.__clients:
            cli.close()

class AsyncoreSocketUDP(asyncore.dispatcher_with_send):
    connected = False
    ipLocal = None
    __ipBroadcast = None
    ipRemote = None
    __ipRemoteValid = False
    port = -1
    data = None
    dataRcvEvent = None
    isCheck = False
    __checkCount = 0
    __checkCountMax = 15

    listSockets = []

    def __init__(self, ipLocal, ipRemote, port):
        self.ipLocal = ipLocal
        if os.name != "nt":
            self.ipLocal = '';
        self.ipRemote = ipRemote
        self.port = port

        self.__ipBroadcast = self.ipLocal[:self.ipLocal.rfind(".")] + ".255"

        try:
            socket.inet_aton(self.ipRemote)
            self.__ipRemoteValid = True
        except socket.error:
            self.__ipRemoteValid = False

        self.dataRcvEvent = Event()
        self.dataRcvEvent()

        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((self.ipLocal, self.port))

        AsyncoreSocketUDP.listSockets.append(self)

    def handle_read(self):
        if self.isCheck:
            time.sleep(0.001)
            self.__checkCount += 1
            if self.__checkCount >= self.__checkCountMax:
                self.__checkCount = 0
                self.connected = False

        try:
            data, addr = self.socket.recvfrom(65000)
            if str(addr[0]) == self.ipRemote or self.__ipRemoteValid == False:
                    self.connected = True
                    self.__checkCount = 0
                    self.data = data
                    self.dataRcvEvent(addr[0], data)
        except Exception as e:
            pass

    def writable(self):
        return False # don't want write notifies

    def start(self):
        self.send("1")
        asyncore.loop()

    def send(self, msg):
        try:
            sendIp = self.ipRemote

            if self.__ipRemoteValid == False and self.__ipBroadcast != None:
                sendIp = self.__ipBroadcast

            self.socket.sendto(bytes(msg, 'utf-8'), (sendIp, self.port))
        except Exception as e:
            pass

    def stop(self):
        AsyncoreSocketUDP.listSockets.remove(self)
        self.connected = False
        self.socket.close

class UDP:
    Connected = False
    ipLocal = None
    ipRemote = None
    port = -1
    data = None
    sock = None
    dataRcvEvent = None

    def __init__(self, ipLocal, ipRemote, port):
        self.ipLocal = ipLocal
        self.ipRemote = ipRemote
        self.port = port

        self.dataRcvEvent = Event()
        self.dataRcvEvent()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def start(self):

        if self.ipLocal is None or self.ipRemote is None or self.port == -1:
            return

        while self.connected == False:
            try:
                self.sock.bind((self.ipLocal, self.port))
                break
            except:
                pass

        self.sock.sendto(b"1", (self.ipRemote, self.port))

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(65000)
            if str(addr[0]) == self.ipRemote:
                    self.connected = True
                    self.data = data
                    self.dataRcvEvent(data)
        except:
            pass

    def send(self, msg):
        try:
            self.sock.sendto(bytes(msg, 'utf-8'), (self.ipRemote, self.port))
        except:
            pass

    def stop(self):
        self.connected = False
        self.sock.close


class Event(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)

    def removeAt(self, index):
        if index < len(self):
            self.remove(self[index])


class SensorsData:
    Timestamp = None
    Info = None
    Acceleration = None
    Orientation = None
    Proximity = None
    Magnetic = None
    Light = None
    Pressure = None
    Steps = None
    Temperature = None
    Humidity = None
    Location = None

    DataByIndex= [Acceleration, Orientation, Proximity, Magnetic, Light, Pressure, Steps, Temperature, Humidity, Location]

    def __init__(self, data):
        self.extractData(data)
        pass


    def extractData(self, data):
        dataSensorsM = data.split("@")
        for i in range(4, len(self.DataByIndex) + 4):
            try:
                dataSensors = dataSensorsM[i].split("$")
                node = DataNode(dataSensors)

                index = i-4
                self.DataByIndex[index] = node

                if index == 0:
                    self.Acceleration = node
                elif index == 1:
                    self.Orientation = node
                elif index == 2:
                    self.Proximity = node
                elif index == 3:
                    self.Magnetic = node
                elif index == 4:
                    self.Light = node
                elif index == 5:
                    self.Pressure = node
                elif index == 6:
                    self.Steps = node
                elif index == 7:
                    self.Temperature = node
                elif index == 8:
                    self.Humidity = node
                elif index == 9:
                    self.Location = node

            except Exception as e:
                pass
        pass

class DataNode:
    Values = None
    def __init__(self, dataValues):
        self.Values = DataNodeValue(dataValues)
        pass

class DataNodeValue:
    Values = []
    AsDouble = None
    AsString = None

    def __init__(self, dataValues):
        self.Values = []
        for i in range(1, len(dataValues)):
            try:
                self.Values.append(float(dataValues[i]))
            except:
                break

        self.AsDouble = self.AsDouble()
        self.AsString = self.AsString()

        pass

    def AsDouble(self):
        return self.Values

    def AsString(self):
        strV = ""
        for i in range(len(self.Values)):
            value = self.Values[i]
            strV += str(value)
            if i < len(self.Values)-1:
                strV += ",\t"
        return strV

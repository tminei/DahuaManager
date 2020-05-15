import shutil

import requests
from requests.auth import HTTPDigestAuth


class DahuaManager:
    login = 'admin'
    password = 'admin1234'
    url = "http://fizik.sytes.net:8080"
    session = requests.session()

    def auth(self):
        self.session.auth = HTTPDigestAuth(self.login, self.password)

    def getMaxExtraStreamCounts(self):
        response = self.session.get(self.url + "/cgi-bin/magicBox.cgi?action=getProductDefinition&name=MaxExtraStream")
        if response.status_code == 200:
            return response.text[response.text.find("=") + 1:]

    def getSnapshot(self, channel, filename):
        channel = int(channel)
        if channel > 4 or channel < 1:
            channel = 1
        response = self.session.get(self.url + "/cgi-bin/snapshot.cgi?channel=" + str(channel), stream=True)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    def getColor(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=VideoColor")
        cnt = 0
        colorDict = {}
        if response.status_code == 200:
            splitstr = response.text.strip().split()
            for i in splitstr:
                cnt += 1
                channelNo = i[i.find("[") + 1:i.find("]")]
                colorConfigNo = i[i.find("][") + 2:i.find("=")][:i[i.find("][") + 2:i.find("=")].find(".") - 1]
                if i[23:i.find("=")] != '':
                    try:
                        len(colorDict[channelNo])
                    except:
                        colorDict[channelNo] = {}
                    try:
                        len(colorDict[channelNo][colorConfigNo])
                    except:
                        colorDict[channelNo][colorConfigNo] = {}
                    colorDict[channelNo][colorConfigNo][i[23:i.find("=")]] = i[i.find("=")+1:]
                    if i[23:i.find("=")] == "TimeSection":
                        colorDict[channelNo][colorConfigNo][i[23:i.find("=")]] += " "
                        colorDict[channelNo][colorConfigNo][i[23:i.find("=")]] += splitstr[cnt]
            return colorDict
        else:
            return 1

    def setColor(self, param, channel, config, value,):
        available = ["brightness", "contrast", "hue", "saturation", "timeSection", "b", "c", "h", "s", "t"]
        if param not in available:
            return 1
        if param == "s" or param == "saturation":
            param = "VideoColor["+str(channel)+"]["+str(config)+"].Saturation"
        elif param == "b" or param == "brightness":
            param = "VideoColor["+str(channel)+"]["+str(config)+"].Brightness"
        elif param == "h" or param == "hue":
            param = "VideoColor["+str(channel)+"]["+str(config)+"].Hue"
        elif param == "t" or param == "timeSection":
            param = "VideoColor["+str(channel)+"]["+str(config)+"].TimeSection"
        if param != "VideoColor["+str(channel)+"]["+str(config)+"].TimeSection" and value not in range(0, 101):
            return 2
        # print("/cgi-bin/configManager.cgi?action=setConfig&" + param + "=" + str(value))
        response = self.session.get(
            self.url + "/cgi-bin/configManager.cgi?action=setConfig&" + param + "=" + str(value))
        if response.status_code == 200:
            return 0
        else:
            return 1

    def sessionClose(self):
        self.session.close()


mng = DahuaManager()

mng.auth()

mng.getSnapshot(1, "test.png")
mng.setColor("b", 0, 0, 100)
clr = mng.getColor()
print(clr)
mng.getSnapshot(1, "a.png")

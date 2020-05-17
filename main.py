import shutil  # for save img cap (opencv heavy)
import json  # for buckup/restore
import requests
from requests.auth import HTTPDigestAuth


# s is set
# g is get
# b is backup
# r is restore

class DahuaManager:
    login = 'admin'
    password = 'admin'
    url = "http"
    session = requests.session()

    def auth(self):
        self.session.auth = HTTPDigestAuth(self.login, self.password)

    def deauth(self):
        self.session.close()

    def bVideoInOptionsConfig(self, filename):
        config = self.gVideoInOptionsConfig()
        jsonconfig = json.dumps(config)
        with open(filename, "w") as file:
            file.write(jsonconfig)
        return 0

    def sBasicConfig(self, *paramList):
        # inteface is first item in *paramList tuple; ex:(eth0, DefaultGateway, 192.168.1.1)
        validParam = []
        goodParam = []
        availableParam = {
            "baseLevel": [
                "DefaultInterface", "Domain", "Hostname"
            ],
            "interfaceLevel": [
                "DefaultGateway", "DhcpEnable", "DnsServers[0]", "DnsServers[1]", "IPAddress", "MTU", "PhysicalAddress"
            ]
        }
        for param in paramList:
            if type(param) is tuple:
                validParam.append(param)
        for param in validParam:
            if len(param) == 2:
                if param[0] in availableParam["baseLevel"]:
                    goodParam.append(param)
            if len(param) == 3:
                if param[1] in availableParam["interfaceLevel"]:
                    goodParam.append(param)
        if len(goodParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"

            for i in goodParam:
                if len(i) == 2:
                    URL += "&Network." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&Network." + i[0] + "." + i[1] + "=" + i[2]
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def sColor(self, param, channel, config, value):
        available = ["brightness", "contrast", "hue", "saturation", "timeSection", "b", "c", "h", "s", "t"]
        # b, c, h, s, t is alias for brightness, contrast, hue, saturation, timeSection
        if param not in available:
            return 1
        if param == "s" or param == "saturation":
            param = "VideoColor[" + str(channel) + "][" + str(config) + "].Saturation"
        elif param == "b" or param == "brightness":
            param = "VideoColor[" + str(channel) + "][" + str(config) + "].Brightness"
        elif param == "h" or param == "hue":
            param = "VideoColor[" + str(channel) + "][" + str(config) + "].Hue"
        elif param == "t" or param == "timeSection":
            param = "VideoColor[" + str(channel) + "][" + str(config) + "].TimeSection"
        if param != "VideoColor[" + str(channel) + "][" + str(config) + "].TimeSection" and value not in range(0, 101):
            return 2
        response = self.session.get(
            self.url + "/cgi-bin/configManager.cgi?action=setConfig&" + param + "=" + str(value))
        if response.status_code == 200:
            return 0
        else:
            return 1

    def sVideoInOptionsConfig(self, channelNo, *paramList):
        validParam = []
        goodParam = []
        availableParam = {
            "singleLevel": ["Backlight", "DayNightColor", "ExposureMode", "ExposureSpeed", "ExposureValue1",
                            "ExposureValue2", "ExternalSync", "ExternalSyncPhase" "FlashControl", "Flip", "Gain",
                            "GainBlue", "GainRed", "GainGreen", "GainAuto", "IrisAuto", "Mirror", "WhiteBalance",
                            "ReferenceLevel", "Rotate90", "SignalFormat", "AntiFlicker", "GlareInhibition"],
            "capLevel": ["FlashControl", "NightOptions", "NormalOptions"],
            "flashControl": ["Pole", "Value", "PreValue", "Mode"],
            "dayNight": ["BrightnessThreshold", "IrisAuto", "SunriseHour", "SunriseMinute", "SunriseSecond",
                         "SunsetHour", "SunsetMinute", "SunsetSecond", "SwitchMode", "Profile", "ExposureSpeed",
                         "ExposureValue1", "ExposureValue2", "Gain", "GainAuto", "GainBlue", "GainGreen", "GainRed",
                         "WhiteBalance", "ReferenceLevel", "ExternalSyncPhase", "AntiFlicker", "Backlight",
                         "DayNightColor", "ExposureMode", "GlareInhibition", "Mirror", "Flip", "Rotate90"]}
        for param in paramList:
            if type(param) is tuple:
                validParam.append(param)
        for param in validParam:
            if len(param) == 2:
                if param[0] in availableParam["singleLevel"]:
                    goodParam.append(param)
            if len(param) == 3:
                if param[0] in availableParam["capLevel"]:
                    if param[0] == availableParam["capLevel"][0]:
                        if param[1] in availableParam["flashControl"]:
                            goodParam.append(param)
                    elif param[0] == availableParam["capLevel"][1] or param[0] == availableParam["capLevel"][2]:
                        if param[1] in availableParam["dayNight"]:
                            goodParam.append(param)
        if len(goodParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
            for i in goodParam:
                if len(i) == 2:
                    URL += "&VideoInOptions[" + str(channelNo) + "]." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&VideoInOptions[" + str(channelNo) + "]." + i[0] + "." + i[1] + "=" + i[2]
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def sNTPConfig(self, *paramList):
        validParam = []
        goodParam = []
        availableParam = ["Address", "Enable", "Port", "TimeZone"]
        for param in paramList:
            if type(param) is tuple:
                validParam.append(param)
        for param in validParam:
            if len(param) == 2:
                if param[0] in availableParam:
                    goodParam.append(param)
        if len(goodParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
            for i in goodParam:
                if len(i) == 2:
                    URL += "&NTP." + i[0] + "=" + i[1]
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def gVideoInputCaps(self, channel):
        response = self.session.get(
            self.url + "/cgi-bin/devVideoInput.cgi?action=getCaps&channel=" + str(channel))
        if response.status_code == 200:
            caps = {}
            splitstr = response.text.strip().split("\r")
            for i in splitstr:
                print(i[i.find(".") + 1:i.find("=")])
                caps[i[i.find(".") + 1:i.find("=")]] = i[i.find("=") + 1:]
            return caps
        else:
            return response.status_code

    def gVideoInOptionsConfig(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=VideoInOptions")
        if response.status_code == 200:
            VideoInOptions = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                i = i[20:]
                j = i[4:i.find("=")]
                level0 = i[i.find("[") + 1:i.find("]")]
                try:
                    len(VideoInOptions[level0])
                except:
                    VideoInOptions[level0] = {}
                lvlcnt = i[:i.find("=")].count(".")
                val = i[i.find("=") + 1:]
                if lvlcnt > 1:
                    j = j.split(".")
                    try:
                        len(VideoInOptions[level0][j[0]])
                    except:
                        VideoInOptions[level0][j[0]] = {}
                    if lvlcnt == 2:
                        if "[" not in j[1]:
                            try:
                                len(VideoInOptions[level0][j[0]][j[1]])
                            except:
                                VideoInOptions[level0][j[0]][j[1]] = val
                        else:
                            m = j[1][:j[1].find("[")]
                            try:
                                len(VideoInOptions[level0][j[0]][m])
                            except:
                                VideoInOptions[level0][j[0]][m] = {}
                            level1 = str(j[1][j[1].find("[") + 1:j[1].find("]")])
                            try:
                                len(VideoInOptions[level0][j[0]][m][level1])
                            except:
                                VideoInOptions[level0][j[0]][m][level1] = val
                    if lvlcnt == 3:
                        try:
                            len(VideoInOptions[level0][j[0]][j[1]])
                        except:
                            VideoInOptions[level0][j[0]][j[1]] = {}
                        try:
                            len(VideoInOptions[level0][j[0]][j[1]][j[2]])
                        except:
                            VideoInOptions[level0][j[0]][j[1]][j[2]] = val
                else:
                    if "[" not in j:
                        try:
                            len(VideoInOptions[level0][j])
                        except:
                            VideoInOptions[level0][j] = val
                    else:
                        m = j[:j.find("[")]
                        try:
                            len(VideoInOptions[level0][m])
                        except:
                            VideoInOptions[level0][m] = {}
                        level1 = str(j[j.find("[") + 1:j.find("]")])
                        try:
                            len(VideoInOptions[level0][m][level1])
                        except:
                            VideoInOptions[level0][m][level1] = val

            return VideoInOptions
        else:
            return response.status_code

    def gMaxExtraStreamCounts(self):
        response = self.session.get(self.url + "/cgi-bin/magicBox.cgi?action=getProductDefinition&name=MaxExtraStream")
        if response.status_code == 200:
            return response.text[response.text.find("=") + 1:]
        else:
            return response.status_code

    def gSnapshot(self, channel, filename):
        channel = int(channel)
        if channel > 4 or channel < 1:
            channel = 1
        response = self.session.get(self.url + "/cgi-bin/snapshot.cgi?channel=" + str(channel), stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        else:
            return response.status_code

    def gColor(self):
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
                    colorDict[channelNo][colorConfigNo][i[23:i.find("=")]] = i[i.find("=") + 1:]
                    if i[23:i.find("=")] == "TimeSection":
                        colorDict[channelNo][colorConfigNo][i[23:i.find("=")]] += " "
                        colorDict[channelNo][colorConfigNo][i[23:i.find("=")]] += splitstr[cnt]
            return colorDict
        else:
            return response.status_code

    def gNTPConfig(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=NTP")
        if response.status_code == 200:
            NTP = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                name = i[i.find("NTP.") + 4:i.find("=")]
                val = i[i.find("=") + 1:]
                try:
                    len(NTP[name])
                except:
                    NTP[name] = val
            return NTP
        else:
            return response.status_code

    def gBasicConfig(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=Network")
        if response.status_code == 200:
            basicConfig = {}
            raw = response.text.strip().splitlines()
            short = []
            for i in raw:
                short.append(i[14:])
            for i in short:
                param = i[:i.find("=")]
                val = i[i.find("=") + 1:]
                if "." not in param:
                    basicConfig[param] = val
                elif "[" not in param:
                    interface = param[:param.find(".")]
                    try:
                        len(basicConfig[interface])
                    except:
                        basicConfig[interface] = {}
                    basicConfig[interface][param[param.find(".") + 1:i.find("=")]] = val
                elif "[" in param:
                    interface = param[:param.find(".")]
                    try:
                        len(basicConfig[interface])
                    except:
                        basicConfig[interface] = {}
                    num = param[param.find("[") + 1:param.find("]")]
                    try:
                        len(basicConfig[interface][param[param.find(".") + 1:i.find("[") - 1]])
                    except:
                        basicConfig[interface][param[param.find(".") + 1:i.find("[") - 1]] = {}
                    try:
                        len(basicConfig[interface][param[param.find(".") + 1:i.find("[") - 1]][num])
                    except:
                        basicConfig[interface][param[param.find(".") + 1:i.find("[") - 1]][num] = val
            return basicConfig
        else:
            return response.status_code


mng = DahuaManager()

mng.auth()

# mng.gSnapshot(1, "test.png")
# mng.sColor("b", 0, 0, 100)
# clr = mng.gColor()
# print(clr)
# mng.gSnapshot(1, "b.png")
# mng.sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"),
#                           ("Flip", "true"))
# mng.gSnapshot(1, "a.png")
# mng.sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"),
#                           ("Flip", "false"))
# mng.gSnapshot(1, "a2.png")
# print(mng.gVideoInputCaps(channel=1))
# mng.bVideoInOptionsConfig("test.json")
# mng.sBasicConfig(("Domain", "dahua"), ("eth0", "DnsServers[1]", "8.8.4.4"))
# print(mng.gBasicConfig())
mng.sNTPConfig(("Address", "pool.ntp.org"), ("TimeZone", "3"))

mng.deauth()

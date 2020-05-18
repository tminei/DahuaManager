import shutil  # for save img cap (opencv heavy)
import json  # for backup/restore
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

    def sRTSPConfig(self, *paramList):
        # if RTP level first param is RTP
        validParam = []
        goodParam = []
        availableParam = {
            "baseLevel": [
                "Enable", "Port"
            ],
            "RTPLevel": [
                "StartPort", "EndPort"
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
                if param[0] != "RTP":
                    continue
                if param[1] in availableParam["RTPLevel"]:
                    goodParam.append(param)
        if len(goodParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"

            for i in goodParam:
                if len(i) == 2:
                    URL += "&RTSP." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&RTSP." + i[0] + "." + i[1] + "=" + i[2]
            # response = self.session.get(URL)
            # if response.status_code == 200:
            #     return 0
            # else:
            #     return response.status_code
            print(URL)
        else:
            return 1

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

    def sMotionDetectConfig(self, channelNo, *paramList):
        validParam = []
        for param in paramList:
            if type(param) is tuple:
                validParam.append(param)
        if len(validParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
            for i in validParam:
                if len(i) == 2:
                    URL += "&MotionDetect[" + str(channelNo) + "]." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&MotionDetect[" + str(channelNo) + "]." + i[0] + "." + i[1] + "=" + i[2]
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

    def sChannelTitleConfig(self, channel, name):
        if int(channel) < 0:
            channel = 0
        URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig&ChannelTitle[" + str(channel) + "].Name=" + str(
            name)
        response = self.session.get(URL)
        if response.status_code == 200:
            return 0
        else:
            return response.status_code

    def gChannelTitleConfig(self):
        response = self.session.get(
            self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=ChannelTitle")
        if response.status_code == 200:
            title = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                num = i[i.find("[") + 1:i.find("]")]
                val = i[i.find("=") + 1:]
                try:
                    len(title[num])
                except:
                    title[num] = val
            return title
        else:
            return response.status_code

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

    def gMotionDetectConfig(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=MotionDetect")
        if response.status_code == 200:
            motionConfig = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                pretty = i[18:]
                levelAll = pretty[pretty.find("]") + 2:pretty.find("=")]
                levelCount = levelAll.count(".")
                val = pretty[pretty.find("=") + 1:]
                channel = pretty[pretty.find("[") + 1:pretty.find("]")]
                if pretty.count("[") == 3 and "MotionDetectWindow" in pretty:
                    regionLevel = pretty[23:]
                    motionDetectWindowLevel = regionLevel[:regionLevel.find("]")]
                    regionLevelName = regionLevel[regionLevel.find(".") + 1: regionLevel.find("[")]
                    regionLevelNameNum = regionLevel[9:]
                    regionLevelNameNum = regionLevelNameNum[
                                         regionLevelNameNum.find("[") + 1:regionLevelNameNum.find("]")]
                    try:
                        len(motionConfig[channel])
                    except:
                        motionConfig[channel] = {}
                    try:
                        len(motionConfig[channel]["MotionDetectWindow"])
                    except:
                        motionConfig[channel]["MotionDetectWindow"] = {}
                    try:
                        len(motionConfig[channel]["MotionDetectWindow"][motionDetectWindowLevel])
                    except:
                        motionConfig[channel]["MotionDetectWindow"][motionDetectWindowLevel] = {}
                    try:
                        len(motionConfig[channel]["MotionDetectWindow"][motionDetectWindowLevel][regionLevelName])
                    except:
                        motionConfig[channel]["MotionDetectWindow"][motionDetectWindowLevel][regionLevelName] = {}
                    try:
                        len(motionConfig[channel]["MotionDetectWindow"][motionDetectWindowLevel][regionLevelName][
                                regionLevelNameNum])
                    except:
                        motionConfig[channel]["MotionDetectWindow"][motionDetectWindowLevel][regionLevelName][
                            regionLevelNameNum] = val

                try:
                    len(motionConfig[channel])
                except:
                    motionConfig[channel] = {}
                if levelCount == 0:
                    if "[" not in levelAll:
                        try:
                            len(motionConfig[channel][levelAll])
                        except:
                            motionConfig[channel][levelAll] = val
                    elif "[" in levelAll:
                        level0 = levelAll[:levelAll.find("[")]
                        level1 = levelAll[levelAll.find("[") + 1:levelAll.find("]")]
                        try:
                            len(motionConfig[channel][level0])
                        except:
                            motionConfig[channel][level0] = {}
                        try:
                            len(motionConfig[channel][level0][level1])
                        except:
                            motionConfig[channel][level0][level1] = val
                elif levelCount == 1:
                    if levelAll.count("[") == 0:
                        level0 = levelAll[:levelAll.find(".")]
                        level1 = levelAll[levelAll.find(".") + 1:]
                        try:
                            len(motionConfig[channel][level0])
                        except:
                            motionConfig[channel][level0] = {}
                        try:
                            len(motionConfig[channel][level0][level1])
                        except:
                            motionConfig[channel][level0][level1] = val
                    if levelAll.count("[") == 1:
                        level0 = levelAll[:levelAll.find(".")]
                        level1 = levelAll[levelAll.find(".") + 1:]
                        if level0.count("[") == 0:
                            try:
                                len(motionConfig[channel][level0])
                            except:
                                motionConfig[channel][level0] = {}
                            level1true = level1[:level1.find("[")]
                            level1sub0 = level1[level1.find("[") + 1:level1.find("]")]
                            try:
                                len(motionConfig[channel][level0][level1true])
                            except:
                                motionConfig[channel][level0][level1true] = {}
                            try:
                                len(motionConfig[channel][level0][level1true][level1sub0])
                            except:
                                motionConfig[channel][level0][level1true][level1sub0] = val
                        elif level0.count("[") == 1:
                            level0true = level0[:level0.find("[")]
                            try:
                                len(motionConfig[channel][level0true])
                            except:
                                motionConfig[channel][level0true] = {}
                            level0sub0 = level0[level0.find("[") + 1:level0.find("]")]
                            try:
                                len(motionConfig[channel][level0true][level0sub0])
                            except:
                                motionConfig[channel][level0true][level0sub0] = {}
                            try:
                                len(motionConfig[channel][level0true][level0sub0][level1])
                            except:
                                motionConfig[channel][level0true][level0sub0][level1] = val
                    elif levelAll.count("[") == 2:
                        level0 = levelAll[:levelAll.find(".")]
                        level1 = levelAll[levelAll.find(".") + 1:]
                        if level0.count("[") == 0:
                            try:
                                len(motionConfig[channel][level0])
                            except:
                                motionConfig[channel][level0] = {}
                            level1true = level1[:level1.find("[")]
                            try:
                                len(motionConfig[channel][level0][level1true])
                            except:
                                motionConfig[channel][level0][level1true] = {}
                            level1subAll = level1[level1.find("[") + 1:-1]
                            level1sub0 = level1subAll[:level1subAll.find("]")]
                            level1sub1 = level1subAll[level1subAll.find("[") + 1:]
                            try:
                                len(motionConfig[channel][level0][level1true][level1sub0])
                            except:
                                motionConfig[channel][level0][level1true][level1sub0] = {}
                            try:
                                len(motionConfig[channel][level0][level1true][level1sub0][level1sub1])
                            except:
                                motionConfig[channel][level0][level1true][level1sub0][level1sub1] = val
                elif levelCount == 2:
                    try:
                        len(motionConfig[channel]["EventHandler"])
                    except:
                        motionConfig[channel]["EventHandler"] = {}
                    levelAllPretty = levelAll[13:]
                    level0 = levelAllPretty[:levelAllPretty.find(".")]
                    level1 = levelAllPretty[levelAllPretty.find(".") + 1:]
                    try:
                        len(motionConfig[channel]["EventHandler"][level0])
                    except:
                        motionConfig[channel]["EventHandler"][level0] = {}
                    try:
                        len(motionConfig[channel]["EventHandler"][level0][level1])
                    except:
                        motionConfig[channel]["EventHandler"][level0][level1] = val
            print(motionConfig)
        else:
            return response.status_code

    def gRTSPConfig(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=RTSP")
        if response.status_code == 200:
            RTSPConfig = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                pretty = i[11:]
                name = pretty[:pretty.find("=")]
                val = pretty[pretty.find("=") + 1:]
                if "." not in name:
                    try:
                        len(RTSPConfig[name])
                    except:
                        RTSPConfig[name] = val
                elif "." in name:
                    firstName = name[:name.find(".")]
                    secondName = name[name.find(".") + 1:]
                    try:
                        len(RTSPConfig[firstName])
                    except:
                        RTSPConfig[firstName] = {}
                    try:
                        len(RTSPConfig[firstName][secondName])
                    except:
                        RTSPConfig[firstName][secondName] = val
            return RTSPConfig
        else:
            return response.status_code


mng = DahuaManager()

mng.auth()

# mng.gSnapshot(1, "test.png")
# mng.sColor("b", 0, 0, 100)
# clr = mng.gColor()
# print(clr)
mng.gSnapshot(1, "b.png")
# mng.sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"),
#                           ("Flip", "true"))
# mng.sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"),
#                           ("Flip", "false"))
# mng.gSnapshot(1, "a2.png")
# print(mng.gVideoInputCaps(channel=1))
# mng.bVideoInOptionsConfig("test.json")
# mng.sBasicConfig(("Domain", "dahua"), ("eth0", "DnsServers[1]", "8.8.4.4"))
# print(mng.gBasicConfig())
# print(mng.gNTPConfig())
# mng.sNTPConfig(("Address", "pool.ntp.org"), ("TimeZone", "3"))
# print(mng.gNTPConfig())
# mng.sNTPConfig(("Address", "pool.ntp.org"), ("TimeZone", "2"))
# print(mng.gNTPConfig())
# print(mng.gRTSPConfig())
# print(mng.gChannelTitleConfig())
# mng.sChannelTitleConfig("0", "Lorem ipsum dolor sit amet")
# print(mng.gChannelTitleConfig())
# mng.gSnapshot(1, "a.png")
mng.sMotionDetectConfig("0", ("Enable", "true"), ("PtzManualEnable", "true"))
mng.gMotionDetectConfig()
mng.deauth()

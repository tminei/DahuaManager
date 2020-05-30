import json  # for backup/restore
import shutil  # for save img cap (opencv heavy)

import requests
from requests.auth import HTTPDigestAuth

login = ""
password = ""
url = ""


# s is set
# g is get
# b is backup
# r is restore

class DahuaManager:
    login = login
    password = password
    url = url
    session = requests.session()

    def auth(self):
        self.session.auth = HTTPDigestAuth(self.login, self.password)

    def deauth(self):
        self.session.close()

    def sysInit(self, operation):
        if operation == "reboot":
            response = self.session.get(self.url + "/cgi-bin/magicBox.cgi?action=reboot")
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        elif operation == "shutdown":
            response = self.session.get(self.url + "/cgi-bin/magicBox.cgi?action=shutdown")
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def sysInfo(self, operation):
        if operation == "GetDeviceType" or operation == "DeviceType" or operation == "DevType" or operation == "GetDevType" or str(
                operation) == "0":
            action = "getDeviceType"
        elif operation == "GetHardwareVersion" or operation == "HardwareVersion" or operation == "HardVer" or str(
                operation) == "1":
            action = "getHardwareVersion"
        elif operation == "GetSerialNo" or operation == "SerialNo" or str(operation) == "2":
            action = "getSerialNo"
        elif operation == "GetMachineName" or operation == "GetName" or str(operation) == "3":
            action = "getMachineName"
        elif operation == "GetSystemInfo" or operation == "SysInfo" or operation == "GetInfo" or operation == "Info" or str(
                operation) == "4":
            action = "getSystemInfo"
        elif operation == "GetVendor" or operation == "Vendor" or str(operation) == "5":
            action = "getVendor"
        elif operation == "GetSoftwareVersion" or operation == "SoftVer" or str(operation) == "6":
            action = "getSoftwareVersion"
        elif operation == "GetOnvifVersion" or operation == "Onvif" or operation == "OnvifVer" or str(operation) == "7":
            action = "getOnvifVersion"
        else:
            return 1
        response = self.session.get(self.url + "/cgi-bin/magicBox.cgi?action=" + action)

        if response.status_code == 200:
            data = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                if len(i) > 1:
                    name = i[:i.find("=")]
                    val = i[i.find("=") + 1:]
                    try:
                        len(data[name])
                    except:
                        data[name] = val
                else:
                    data["NaN"] = "NaN"
            return data
        else:
            return response.status_code

    def bVideoInOptionsConfig(self, filename):
        config = self.gVideoInOptionsConfig()
        jsonconfig = json.dumps(config)
        with open(filename, "w") as file:
            file.write(jsonconfig)
        return 0

    def sCurrentTime(self, time):
        # time must be array of Y M D h m s
        # Ex: sCurrentTime(["2020","5","18","19","20","5"])
        if len(time) == 6:
            if len(time[0]) == 4:
                if len(time[1]) == 2 or len(time[1]) == 1 and len(time[2]) == 2 or len(time[1]) == 2 and len(
                        time[3]) == 2 or len(time[3]) == 1 and len(time[4]) == 2 or len(time[4]) == 1 and len(
                    time[5]) == 2 or len(time[5]) == 1:
                    if len(time[3]) == 1:
                        time[3] = "0" + str(time[3])
                    if len(time[4]) == 1:
                        time[4] = "0" + str(time[4])
                    if len(time[5]) == 1:
                        time[5] = "0" + str(time[5])
                    URL = self.url + "/cgi-bin/global.cgi?action=setCurrentTime&time=" + time[0] + "-" + time[1] + "-" + \
                          time[2] + "%20" + time[3] + ":" + time[4] + ":" + time[5]
                    response = self.session.get(URL)
                    if response.status_code == 200:
                        return 0
                    else:
                        return response.status_code

                else:
                    return 3
            else:
                return 2
        else:
            return 1

    def sRTSPConfig(self, *params):
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
        for param in params:
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
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def sBasicConfig(self, *params):
        # interface is first item in *params tuple; ex:(eth0, DefaultGateway, 192.168.1.1)
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
        for param in params:
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

    def sMotionDetectConfig(self, channelNo, *params):
        validParam = []
        for param in params:
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

    def sVideoWidgetConfig(self, channelNo, *params):
        validParam = []
        for param in params:
            if type(param) is tuple:
                validParam.append(param)
        if len(validParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
            for i in validParam:
                if len(i) == 2:
                    URL += "&VideoWidget[" + str(channelNo) + "]." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&VideoWidget[" + str(channelNo) + "]." + i[0] + "." + i[1] + "=" + i[2]
                if len(i) == 4:
                    URL += "&VideoWidget[" + str(channelNo) + "]." + i[0] + "." + i[1] + "." + i[2] + "=" + i[4]
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def sBlindDetectConfig(self, channelNo, *params):
        validParam = []
        for param in params:
            if type(param) is tuple:
                validParam.append(param)
        if len(validParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
            for i in validParam:
                if len(i) == 2:
                    URL += "&BlindDetect[" + str(channelNo) + "]." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&BlindDetect[" + str(channelNo) + "]." + i[0] + "." + i[1] + "=" + i[2]
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

    def sNTPConfig(self, *params):
        validParam = []
        goodParam = []
        availableParam = ["Address", "Enable", "Port", "TimeZone"]
        for param in params:
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

    def sLocalesConfig(self, *params):
        validParam = []
        for param in params:
            if type(param) is tuple:
                validParam.append(param)
        if len(validParam) > 0:
            URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
            for i in validParam:
                if len(i) == 2:
                    URL += "&Locales." + i[0] + "=" + i[1]
                if len(i) == 3:
                    URL += "&Locales." + i[0] + "." + i[1] + "=" + i[2]
            response = self.session.get(URL)
            if response.status_code == 200:
                return 0
            else:
                return response.status_code
        else:
            return 1

        pass

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

    def gLocalesConfig(self):
        response = self.session.get(
            self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=Locales")
        if response.status_code == 200:
            localesConfig = {}
            raw = response.text.strip().splitlines()
            for i in raw:
                pretty = i[14:]
                name = pretty[:pretty.find("=")]
                val = pretty[pretty.find("=") + 1:]
                if name.count(".") == 0:
                    try:
                        len(localesConfig[name])
                    except:
                        localesConfig[name] = val
                elif name.count(".") > 0:
                    level0 = name[:name.find(".")]
                    level1 = name[name.find(".") + 1:]
                    try:
                        len(localesConfig[level0])
                    except:
                        localesConfig[level0] = {}
                    try:
                        len(localesConfig[level0][level1])
                    except:
                        localesConfig[level0][level1] = val
            return localesConfig
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
            return motionConfig
        else:
            return response.status_code

    def gCurrentTime(self):
        response = self.session.get(self.url + "/cgi-bin/global.cgi?action=getCurrentTime")
        timeArr = {}
        if response.status_code == 200:
            raw = response.text.strip().splitlines()
            timeFull = raw[0]
            timeFull = timeFull[timeFull.find("=") + 1:]
            Y = timeFull[0:4]
            M = timeFull[5:7]
            D = timeFull[8:10]
            h = timeFull[11:13]
            m = timeFull[14:16]
            s = timeFull[17:19]
            timeArr["full"] = timeFull
            timeArr["Y"] = Y
            timeArr["M"] = M
            timeArr["D"] = D
            timeArr["h"] = h
            timeArr["m"] = m
            timeArr["s"] = s
            return timeArr
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

    def gVideoWidgetConfig(self):
        VideoWidget = {}
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=VideoWidget")
        if response.status_code == 200:
            raw = response.text.strip().splitlines()
            for i in raw:
                pretty = i[18:]
                lvl0 = pretty[:pretty.find("]")]
                pretty = pretty[pretty.find("]") + 2:]
                try:
                    len(VideoWidget[lvl0])
                except:
                    VideoWidget[lvl0] = {}
                if pretty.count(".") == 0 and pretty.count("[") == 0:
                    lvl1 = pretty[:pretty.find("=")]
                    val = pretty[pretty.find("=") + 1:]
                    try:
                        len(VideoWidget[lvl0][lvl1])
                    except:
                        VideoWidget[lvl0][lvl1] = val
                elif pretty.count(".") > 0:
                    if pretty.count("[") == 0:
                        lvl1 = pretty[:pretty.find(".")]
                        lvl2 = pretty[pretty.find(".") + 1:pretty.find("=")]
                        val = pretty[pretty.find("=") + 1:]
                        try:
                            len(VideoWidget[lvl0][lvl1])
                        except:
                            VideoWidget[lvl0][lvl1] = {}
                        try:
                            len(VideoWidget[lvl0][lvl1][lvl2])
                        except:
                            VideoWidget[lvl0][lvl1][lvl2] = val
                    elif pretty.count("[") == 1:
                        if pretty.find("]") > pretty.find("."):
                            lvl1 = pretty[:pretty.find(".")]
                            lvl2 = pretty[pretty.find(".") + 1:pretty.find("[")]
                            lvl3 = pretty[pretty.find("[") + 1:pretty.find("]")]
                            val = pretty[pretty.find("=") + 1:]
                            try:
                                len(VideoWidget[lvl0][lvl1])
                            except:
                                VideoWidget[lvl0][lvl1] = {}
                            try:
                                len(VideoWidget[lvl0][lvl1][lvl2])
                            except:
                                VideoWidget[lvl0][lvl1][lvl2] = {}
                            try:
                                len(VideoWidget[lvl0][lvl1][lvl2][lvl3])
                            except:
                                VideoWidget[lvl0][lvl1][lvl2][lvl3] = val
                        else:
                            lvl1 = pretty[:pretty.find("[")]
                            lvl2 = pretty[pretty.find("[") + 1:pretty.find("]")]
                            lvl3 = pretty[pretty.find(".") + 1:pretty.find("=")]
                            val = pretty[pretty.find("=") + 1:]
                            try:
                                len(VideoWidget[lvl0][lvl1])
                            except:
                                VideoWidget[lvl0][lvl1] = {}
                            try:
                                len(VideoWidget[lvl0][lvl1][lvl2])
                            except:
                                VideoWidget[lvl0][lvl1][lvl2] = {}
                            try:
                                len(VideoWidget[lvl0][lvl1][lvl2][lvl3])
                            except:
                                VideoWidget[lvl0][lvl1][lvl2][lvl3] = val
                    else:
                        lvl1 = pretty[:pretty.find("[")]
                        lvl2 = pretty[pretty.find("[") + 1:pretty.find("]")]
                        subpretty = pretty[pretty.find("."):pretty.find("=")]
                        val = pretty[pretty.find("=") + 1:]
                        lvl3 = subpretty[subpretty.find(".") + 1:subpretty.find("[")]
                        lvl4 = subpretty[subpretty.find("[") + 1:subpretty.find("]")]
                        try:
                            len(VideoWidget[lvl0][lvl1])
                        except:
                            VideoWidget[lvl0][lvl1] = {}
                        try:
                            len(VideoWidget[lvl0][lvl1][lvl2])
                        except:
                            VideoWidget[lvl0][lvl1][lvl2] = {}
                        try:
                            len(VideoWidget[lvl0][lvl1][lvl2][lvl3])
                        except:
                            VideoWidget[lvl0][lvl1][lvl2][lvl3] = {}
                        try:
                            len(VideoWidget[lvl0][lvl1][lvl2][lvl3][lvl4])
                        except:
                            VideoWidget[lvl0][lvl1][lvl2][lvl3][lvl4] = val
            return VideoWidget
        else:
            return response.status_code

    def gBlindDetectConfig(self):
        blindConfig = {}
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=BlindDetect")
        if response.status_code == 200:
            raw = response.text.strip().splitlines()
            for i in raw:
                pretty = i[18:]
                levelAll = pretty[pretty.find("]") + 2:pretty.find("=")]
                levelCount = levelAll.count(".")
                val = pretty[pretty.find("=") + 1:]
                channel = pretty[pretty.find("[") + 1:pretty.find("]")]
                if pretty.count("[") == 3 and "BlindDetectWindow" in pretty:
                    regionLevel = pretty[23:]
                    blindDetectWindowLevel = regionLevel[:regionLevel.find("]")]
                    regionLevelName = regionLevel[regionLevel.find(".") + 1: regionLevel.find("[")]
                    regionLevelNameNum = regionLevel[9:]
                    regionLevelNameNum = regionLevelNameNum[
                                         regionLevelNameNum.find("[") + 1:regionLevelNameNum.find("]")]
                    try:
                        len(blindConfig[channel])
                    except:
                        blindConfig[channel] = {}
                    try:
                        len(blindConfig[channel]["BlindDetectWindow"])
                    except:
                        blindConfig[channel]["BlindDetectWindow"] = {}
                    try:
                        len(blindConfig[channel]["BlindDetectWindow"][blindDetectWindowLevel])
                    except:
                        blindConfig[channel]["BlindDetectWindow"][blindDetectWindowLevel] = {}
                    try:
                        len(blindConfig[channel]["BlindDetectWindow"][blindDetectWindowLevel][regionLevelName])
                    except:
                        blindConfig[channel]["BlindDetectWindow"][blindDetectWindowLevel][regionLevelName] = {}
                    try:
                        len(blindConfig[channel]["BlindDetectWindow"][blindDetectWindowLevel][regionLevelName][
                                regionLevelNameNum])
                    except:
                        blindConfig[channel]["BlindDetectWindow"][blindDetectWindowLevel][regionLevelName][
                            regionLevelNameNum] = val

                try:
                    len(blindConfig[channel])
                except:
                    blindConfig[channel] = {}
                if levelCount == 0:
                    if "[" not in levelAll:
                        try:
                            len(blindConfig[channel][levelAll])
                        except:
                            blindConfig[channel][levelAll] = val
                    elif "[" in levelAll:
                        level0 = levelAll[:levelAll.find("[")]
                        level1 = levelAll[levelAll.find("[") + 1:levelAll.find("]")]
                        try:
                            len(blindConfig[channel][level0])
                        except:
                            blindConfig[channel][level0] = {}
                        try:
                            len(blindConfig[channel][level0][level1])
                        except:
                            blindConfig[channel][level0][level1] = val
                elif levelCount == 1:
                    if levelAll.count("[") == 0:
                        level0 = levelAll[:levelAll.find(".")]
                        level1 = levelAll[levelAll.find(".") + 1:]
                        try:
                            len(blindConfig[channel][level0])
                        except:
                            blindConfig[channel][level0] = {}
                        try:
                            len(blindConfig[channel][level0][level1])
                        except:
                            blindConfig[channel][level0][level1] = val
                    if levelAll.count("[") == 1:
                        level0 = levelAll[:levelAll.find(".")]
                        level1 = levelAll[levelAll.find(".") + 1:]
                        if level0.count("[") == 0:
                            try:
                                len(blindConfig[channel][level0])
                            except:
                                blindConfig[channel][level0] = {}
                            level1true = level1[:level1.find("[")]
                            level1sub0 = level1[level1.find("[") + 1:level1.find("]")]
                            try:
                                len(blindConfig[channel][level0][level1true])
                            except:
                                blindConfig[channel][level0][level1true] = {}
                            try:
                                len(blindConfig[channel][level0][level1true][level1sub0])
                            except:
                                blindConfig[channel][level0][level1true][level1sub0] = val
                        elif level0.count("[") == 1:
                            level0true = level0[:level0.find("[")]
                            try:
                                len(blindConfig[channel][level0true])
                            except:
                                blindConfig[channel][level0true] = {}
                            level0sub0 = level0[level0.find("[") + 1:level0.find("]")]
                            try:
                                len(blindConfig[channel][level0true][level0sub0])
                            except:
                                blindConfig[channel][level0true][level0sub0] = {}
                            try:
                                len(blindConfig[channel][level0true][level0sub0][level1])
                            except:
                                blindConfig[channel][level0true][level0sub0][level1] = val
                    elif levelAll.count("[") == 2:
                        level0 = levelAll[:levelAll.find(".")]
                        level1 = levelAll[levelAll.find(".") + 1:]
                        if level0.count("[") == 0:
                            try:
                                len(blindConfig[channel][level0])
                            except:
                                blindConfig[channel][level0] = {}
                            level1true = level1[:level1.find("[")]
                            try:
                                len(blindConfig[channel][level0][level1true])
                            except:
                                blindConfig[channel][level0][level1true] = {}
                            level1subAll = level1[level1.find("[") + 1:-1]
                            level1sub0 = level1subAll[:level1subAll.find("]")]
                            level1sub1 = level1subAll[level1subAll.find("[") + 1:]
                            try:
                                len(blindConfig[channel][level0][level1true][level1sub0])
                            except:
                                blindConfig[channel][level0][level1true][level1sub0] = {}
                            try:
                                len(blindConfig[channel][level0][level1true][level1sub0][level1sub1])
                            except:
                                blindConfig[channel][level0][level1true][level1sub0][level1sub1] = val
                elif levelCount == 2:
                    try:
                        len(blindConfig[channel]["EventHandler"])
                    except:
                        blindConfig[channel]["EventHandler"] = {}
                    levelAllPretty = levelAll[13:]
                    level0 = levelAllPretty[:levelAllPretty.find(".")]
                    level1 = levelAllPretty[levelAllPretty.find(".") + 1:]
                    try:
                        len(blindConfig[channel]["EventHandler"][level0])
                    except:
                        blindConfig[channel]["EventHandler"][level0] = {}
                    try:
                        len(blindConfig[channel]["EventHandler"][level0][level1])
                    except:
                        blindConfig[channel]["EventHandler"][level0][level1] = val
            return blindConfig
        else:
            return response.status_code

    def regMng(self, channel, target, window, mode, *p1p2):
        URL = self.url + "/cgi-bin/configManager.cgi?action=setConfig"
        if type(p1p2) is tuple and len(p1p2) == 2 and type(p1p2[0]) is tuple and type(p1p2[1]) is tuple and len(
                p1p2[1]) == 2 and len(p1p2[0]) == 2:
            p1 = p1p2[0]
            p2 = p1p2[1]
            if int(p1[0]) > 17 or int(p1[1]) > 21 or int(p1[0]) < 0 or int(p1[1]) < 0 or int(p2[0]) > 17 or int(
                    p2[1]) > 21 or int(p2[0]) < 0 or int(p2[1]) < 0:
                return 2
            else:

                size = p2[0] - p1[0], p2[1] - p1[1]
                powsum = 0
                for i in range(0, size[0] + 1):
                    powsum += (2 ** (22 - (p1[0] + i)))
                tempList = []
                for j in range(p1[1], p2[1]):
                    if target == "motion":
                        if mode == "fill":
                            URL += "&MotionDetect[{0}].MotionDetectWindow[{1}].Region[{2}]={3}".format(channel, window,
                                                                                                       j, powsum)
                        elif mode == "remove":
                            URL += "&MotionDetect[{0}].MotionDetectWindow[{1}].Region[{2}]={3}".format(channel, window,
                                                                                                       j, 0)

        elif mode == "clear":
            for k in range(0, 18):
                URL += "&MotionDetect[{0}].MotionDetectWindow[{1}].Region[{2}]=0".format(channel, window, k)

        response = self.session.get(URL)
        if response.status_code == 200:
            return 0
        else:
            return response.status_code


mng = DahuaManager()
mng.auth()
# mng.regMng(0, "motion", 0, "clear")
# mng.regMng(0, "motion", 0, "fill", (0, 3), (10, 10))
# while True:
#     mng.sChannelTitleConfig("0", time.time())
#     time.sleep(1)
mng.sVideoWidgetConfig("0", ("CustomTitle[0]", "Text", "0|1|1|1|1"), ("CustomTitle[1]", "TextAlign", "1"),("CustomTitle[1]", "Rect[0]", "5319"), ("CustomTitle[1]", "Rect[1]", "7445"), ("CustomTitle[1]", "Rect[3]", "7929"),("CustomTitle[1]", "Rect[4]", "7862"))
mng.gSnapshot("0", "test.png")
print(mng.gVideoWidgetConfig())
mng.deauth()

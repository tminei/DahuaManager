    def gVideoInOptionsConfig(self):
        response = self.session.get(self.url + "/cgi-bin/configManager.cgi?action=getConfig&name=VideoInOptions")
        if response.status_code == 200:
            VideoInOptions = {}
            print(response.text)
            raw = response.text.strip().splitlines()
            cnt = 0
            for i in raw:
                raw[cnt] = i[6:]
                cnt += 1
            for i in raw:
                try:
                    len(VideoInOptions[i[i.find("VideoInOptions[") + 15:i.find("]")]])
                except:
                    VideoInOptions[i[i.find("VideoInOptions[") + 15:i.find("]")]] = {}
                structSize = len(i[18:].split("."))
                if structSize > 1:
                    print(i[18:].split("."))
                    level0 = str(i[i.find("VideoInOptions[") + 15:i.find("]")])
                    level1 = str(i[18:].split(".")[0])
                    try:
                        len(VideoInOptions[level0][level1])
                    except:
                        VideoInOptions[i[i.find("VideoInOptions[") + 15:i.find("]")]][i[18:].split(".")[0]] = {}
                if structSize > 2:
                    level0 = str(i[i.find("VideoInOptions[") + 15:i.find("]")])
                    level1 = str(i[18:].split(".")[0])
                    level2 = str(i[18:].split(".")[1])
                    if "=" not in i[18:].split(".")[1] and "[" not in i[18:].split(".")[2]:
                        try:
                            len(VideoInOptions[level0][level1][level2])
                        except:
                            VideoInOptions[level0][level1][level2] = {}
                    elif "=" in i[18:].split(".")[1]:
                        string = i[18:].split(".")[1]
                        try:
                            len(VideoInOptions[level0][level1][string[:string.find("=")]])
                        except:
                            VideoInOptions[level0][level1][string[:string.find("=")]] = string[string.find("=")+1:]
                        print("DDD "+ i[18:].split(".")[1])
                if structSize == 1:
                    level0 = str(i[i.find("VideoInOptions[") + 15:i.find("]")])
                    for j in i[18:].split("."):
                        if "[" not in j:
                            level1 = j[:j.find("=")]
                            VideoInOptions[level0][level1] = j[j.find("=") + 1:]
                        elif "[" in j:
                            level1 = j[:j.find("[")]
                            try:
                                len(VideoInOptions[level0][level1])
                            except:
                                VideoInOptions[level0][level1] = {}
                            level2 = str(j[j.find("[")+1:j.find("]")])
                            try:
                                len(VideoInOptions[level0][level1][level2])
                            except:
                                VideoInOptions[level0][level1][level2] = str(j[j.find("=")+1:])
                    # if "[" not in i[18:].split("."):
                    #     print(i[18:].split("."))
                    #     # level1 = str(i[18:].split(".")).find()
                    #     # VideoInOptions[level0][level1] = 123
                    #     # print(i[18:].split("."))

            print(raw)
            print(VideoInOptions)

# PYTHON DAHUA MANAGER MANUAL
# Preparation
## Links
[DAHUA API](https://dipp.dahuasecurity.com/integrationProtocols/112)

## Dependencies
    pip3 install shutil
    pip3 install requests

# API documentation
## Shortening method names
* s is set
* g is get
* b is backup
* r is restore

## Description of methods

## System methods

**sysInit**(operation) (9.8.{1-2} in Dahua manual)

Accepts *reboot* and *shutdown* values. Reboot or shutdown the camera, depending on the value.<hr>

**sysInfo** (operation) (9.8.{3-10})
Get system info.

%operation% can be:

GetDeviceType (shortcut: 0)

GetHardwareVersion (1)

GetSerialNo (2)

GetMachineName (3)

GetSystemInfo (4)

GetVendor (5)

GetSoftwareVersion(6)

GetOnvifVersion (7) **Warning** return 400 if no Onvif version.
<hr>

## Management methods

**auth**() method is needed for the authentication. 
You always need to start working with it and finish with the deauth method.
<hr>

**deauth**() method close connections. Always finish your work with the camera using this method.
<hr>

**bVideoInOptionsConfig**(filename). Backup data, recived gVideoInOptionsConfig() method as json in %filename%

## Setting methods

**sColor**(param, channel, config, value) (4.2.2 in Dahua manual)
Method is used to set Brightness, Contrast, Hue, Saturation, TimeSection parametrs. You can use allias b, c, h, s and t.
<hr>

**sVideoInOptionsConfig**(channelNo, params) (4.3.3)
Allows setting the SetVideoInOptionsConfig parameters. 
Example:
```
sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"), ("Flip", "false"))
```
In 0 ChannelNo set FlashControl.Mode=1; Mirror=true; NormalOptions.Rotate90=1; Flip=false

<hr>

**sCurrentTime**(time)
%time% is ***array*** of Y M D h m s

**Example:**

```
mng.sCurrentTime(["2020", "5", "18", "19", "42", "05"]) (9.2.2)
```

Possible errors:

-> 1 -- array size not equality 6.

-> 2 -- year format is not equal to 4 digits.

-> 3 -- wrong M D h m s format.

<hr>

**sBasicConfig**(params) (5.2.2)
A method that allows you to change the default network settings.
```
Comment: interface is network interface name, such as eth0, eth1...
```
params is tuples with two or three points inside:
2 parametrs: parametr, value.
**ex: ("Domain", "dahua")**

3 parametrs: interface, parametr, value.
**ex:(eth0, DefaultGateway, 192.168.1.1)**
### Attachment: Dahua manual has an error:
It says:
```
"NetWork.DefaultInterface"
```
But the correct request must be:
```
"Network.DefaultInterface" (w in lower case).
```

<hr>

**sNTPConfig**(params) (5.8.2)
Set NTP config.

**Example:**

```
mng.sNTPConfig(("Address", "pool.ntp.org"), ("TimeZone", "2"))
```
Set Address="pool.ntp.org" and TimeZone=2


<hr>

**sRTSPConfig**(params) (5.8.2)
Set RTSP config.

### ATTENTION!

Before change this parametrs *RTSP.Port, RTSP.RTP.EndPort, RTSP.RTP.StartPort*, **NEED** disable RTSP:

**Example:**
```
mng.sRTSPConfig(("Enable", "false"))
time.sleep(1)
cnt = 0
while True:
    time.sleep(1)
    test = mng.gRTSPConfig()
    if test['Enable'] == "false":
        break
    elif cnt == 3:
        cnt = 0
        mng.sRTSPConfig(("Enable", "false"))
    cnt += 1
mng.sRTSPConfig(("Port", "554"))
mng.sRTSPConfig(("Enable", "true"))
```
**If the server is started, the parameters will not be changed.**


<hr>

**sChannelTitleConfig**(channel, name) (4.7.2)
Change %channel% title to %name%.

**Example:**

mng.sChannelTitleConfig("0", "Lorem ipsum dolor sit amet")

<hr>

**sMotionDetectConfig**(channelNo, params) (6.3.2)
Set motion detect config.

**Example:**

mng.sMotionDetectConfig("0", ("Enable", "true"), ("PtzManualEnable", "true"))

<hr>

**sBlindDetectConfig**(channelNo, params) (6.4.1)
Set blind detect config.

**Example:**

mng.sBlindDetectConfig("0", ("Enable", "true"))

<hr>

**sLocalesConfig**(params) (9.3.2)
Set locales config.

**Example:**

mng.sLocalesConfig(("DSTEnable", "true"))



## Receiving methods

**gVideoInputCaps**(channel) (4.3.1 in Dahua manual)
Get video input capabilities, *channelNo* is video in channel index.
<hr>

**gLocalesConfig**() (9.3.1)

**Example:**

print(mng.gLocalesConfig())

**Output:** 

```
{'DSTEnable': 'false', 'DSTEnd': {'Day': '0', 'Hour': '0', 'Minute': '0', 'Month': '10', 'Week': '-1', 'Year': '2020'}, 'DSTStart': {'Day': '0', 'Hour': '0', 'Minute': '0', 'Month': '3', 'Week': '-1', 'Year': '2020'}, 'TimeFormat': 'yyyy-MM-dd HH:mm:ss'}
```
<hr>

**gVideoInOptionsConfig**() (4.3.2)
Video in options contain Backlight, ExposureSpeed, DayNightColor. DayOptions, NightOptions, NormalOptions and so on

Example output(part):
```
q = {'0': {'AlarmDayNightColorMode': '0', 'AntiFlicker': '0', 'AutoSyncPhase': 'false', 'Backlight': '0',
       'BacklightRegion': {'0': '3096', '1': '3096', '2': '5096', '3': '5096'}, 'ColorTemperatureLevel': '100',
       'DayNightColor': '1', 'DayNightSensitivity': '2', 'DayNightSwitchDelay': '6', 'DoubleExposure': '0',
       'DuskOptions': {'ExternalSyncPhase': '125'}, 'ExposureCompensation': '50', 'ExposureIris': '50',
       'ExposureMode': '0', 'ExposureSpeed': '0', 'ExposureValue1': '40', 'ExposureValue2': '40', 'ExternalSync': '0',
       'ExternalSyncPhase': '125', 'FlashControl': {'Mode': '0', 'Pole': '0', 'PreValue': '40', 'Value': '0'},
       'Flip': 'false', 'FocusMode': '0', 'FocusRect': {'0': '0', '1': '0', '2': '8191', '3': '8191'}, 'Gain': '50',
       'GainAuto': 'true', 'GainBlue': '50', 'GainGreen': '50', 'GainMax': '50', 'GainMin': '0', 'GainRed': '50',
       'GlareInhibition': '0', 'InfraRed': 'false', 'InfraRedLevel': '0', 'IrisAuto': 'true',
       'IrisAutoSensitivity': '50', 'Mirror': 'false', . . . }}

```
<hr>

**gMaxExtraStreamCounts**() (4.1.2) Does exactly what the title says.

<hr>

**gCurrentTime**() (9.2.1)

Get current time.

The output would be about this:
```
{'full': '2020-05-18 19:42:46', 'Y': '2020', 'M': '05', 'D': '18', 'h': '19', 'm': '42', 's': '46'}
```
Where %full% - full time in YMDhms format, %Y% - year, %M% - month, %D% - day, "h" - hour, "m" - minute, "s" - seconds 
<hr>

**gColor**() (4.2.1) return dict of **channelNo** dicts of **configNo** dicts of Brightness, Contrast, Hue, Saturation, TimeSection parametrs.

<hr>

**gSnapshot**(channel, filename) (4.1.3)
Get snapshot of %channel% and save it in %filename%.
%%channel%% can be 1,2,3 or 4.

<hr>

**gBasicConfig**() (5.2.1)
Get the basic network setting.

**Example output:**
```
{'DefaultInterface': 'eth0', 'Domain': 'dahua', 'Hostname': 'IPC', 'eth0': {'DefaultGateway': '192.168.1.1', 'DhcpEnable': 'false', 'DnsServer': {'0': '8.8.8.8', '1': '8.8.4.4'}, 'EnableDhcpReservedIP': 'false', 'IPAddress': '192.168.1.2', 'MTU': '1500', 'PhysicalAddress': 'aa:bb:cc:dd:ee:ff', 'SubnetMask': '255.255.255.0'}}
```

<hr>

**gNTPConfig**() (5.8.1)
Get NTP config

**Example output:**

```
{'Address': 'pool.ntp.org', 'Enable': 'true', 'Port': '123', 'TimeZone': '6', 'UpdatePeriod': '10'}
```

<hr>

**gRTSPConfig**() (5.9.1)
Get RTSP config.

**Example output:**

```
table.RTSP.Enable=false
table.RTSP.Port=554
table.RTSP.RTP.EndPort=40000
table.RTSP.RTP.StartPort=20000
```

<hr>

**gChannelTitleConfig**() (4.7.1)
Gets the titles of all channels.

**Example:**

```
print(mng.gChannelTitleConfig())
mng.sChannelTitleConfig("0", "Lorem ipsum dolor sit amet")
print(mng.gChannelTitleConfig())
```

**Output:**

```
{'0': 'Test'}
{'0': 'Lorem ipsum dolor sit amet'}
```

<hr>

**gMotionDetectConfig**() (6.3.2)
Get current motion detect config:


[Example output](https://pastebin.com/GVhNJ0vd) (Huge!)

<hr>

**gMotionDetectConfig**() (6.3.2)
Get current motion detect config:

<hr>

**gBlindnDetectConfig**() (6.4.2)

Output same type as motion detect config



## Hint

All setting and receiving methods return response status code if response error (ex: return 401 if auth error)

## Examples:

```
mng = DahuaManager()

mng.auth()

mng.gSnapshot(1, "test.png")
mng.sColor("b", 0, 0, 100)
print(mng.gColor())
mng.gSnapshot(1, "b.png")
mng.sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"), ("Flip", "true"))
mng.gSnapshot(1, "a.png")
mng.sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"), ("Flip", "false"))
mng.gSnapshot(1, "a2.png")
print(mng.gVideoInputCaps(channel=1))
mng.bVideoInOptionsConfig("test.json")
mng.deauth()
```



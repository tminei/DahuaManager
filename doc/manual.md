# PYTHON DAHUA MANAGER MANUAL
## Preparation
### Links
[DAHUA API](https://dipp.dahuasecurity.com/integrationProtocols/112)

### Dependencies
    pip3 install shutil
    pip3 install requests

## API documentation
### Shortening method names
* s is set
* g is get
* b is backup
* r is restore

### Description of methods

### Management methods

**auth**() method is needed for the authentication. 
You always need to start working with it and finish with the deauth method.

**deauth**() method close connections. Always finish your work with the camera using this method.

**bVideoInOptionsConfig**(filename). Backup data, recived gVideoInOptionsConfig() method as json in %filename%

### Setting methods

**sColor**(param, channel, config, value) (4.2.2 in Dahua manual)
Method is used to set Brightness, Contrast, Hue, Saturation, TimeSection parametrs. You can use allias b, c, h, s and t.

**sVideoInOptionsConfig**(channelNo, paramList) (4.3.3)
Allows setting the SetVideoInOptionsConfig parameters. 
Example:
```
sVideoInOptionsConfig(0, ("FlashControl", "Mode", "1"), ("Mirror", "true"), ("NormalOptions", "Rotate90", "1"), ("Flip", "false"))
```
In 0 ChannelNo set FlashControl.Mode=1; Mirror=true; NormalOptions.Rotate90=1; Flip=false


### Receiving methods

**gVideoInputCaps**(channel) (4.3.1 in Dahua manual)
Get video input capabilities, *channelNo* is video in channel index.

**gVideoInOptionsConfig**() (4.3.2)
Video in options contain Backlight, ExposureSpeed, DayNightColor. DayOptions, NightOptions, NormalOptions and so on

Exampe of output(part):
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

**gMaxExtraStreamCounts**() (4.1.2) Does exactly what the title says.

**gColor**() (4.2.1) return dict of **channelNo** dicts of **configNo** dicts of Brightness, Contrast, Hue, Saturation, TimeSection parametrs.

**gSnapshot**(channel, filename) (4.1.3)
Get snapshot of %channel% and save it in %filename%.
%%channel%% can be 1,2,3 or 4.

### Hint

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


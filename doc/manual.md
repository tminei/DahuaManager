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
* b is buckup
* r is restore

### Description of methods

```**auth** method is needed for the authentication. 
You always need to start working with it and finish with the deauth method.```

```**sColor** (param, channel, config, value) (4.2.2 in Dahua manual) method  is used to set Brightness Contrast Hue Saturation TimeSection parametrs. You can use allias b, c, h, s and t.```

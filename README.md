# OctoPrint-RTMPStreamer
**Overview:** Plugin that adds a tab to OctoPrint for viewing, starting, and stopping a re-encoded stream to any RTMP server.

**Details:** Based on the work found [here](https://blog.alexellis.io/live-stream-with-docker/).

**Notes:** 
- Plugin requires that OctoPrint's webcam stream uses a full url path including the ip address, ie `http://192.168.1.2/webcam/?action=stream`
- Only tested streaming to Twitch from a Pi3.
- Plugin does not provide a streaming application, it just re-encodes the mjpg stream (included with ocotpi) to a flv stream and transmits to configured RTMP server url.
- Although resolution is configurable in the plugin, the mjpg input stream being re-encoded may have a lower resolution and therefore not really be as high as you set it in the plugin settings.

<img src="https://raw.githubusercontent.com/jneilliii/Octoprint-RTMPStreamer/master/tab_screenshot.jpg">

## Prerequisites for Streaming
Follow the instructions found [here](docker_instructions.md) to install and configure docker/ffmpeg for use with this plugin for Live streaming. This is not necessary if you just want to view a url in an iframe on a tab.

## Setup
Once the prerequisites are met and the test command is successfull enter the resolution, stream url, and view url in the RTMP Streamer settings.

<img src="https://raw.githubusercontent.com/jneilliii/Octoprint-RTMPStreamer/master/settings_screenshot.jpg">

Don't forget to change your webcam stream url to a fully qualified url using the ip address of your pi like

http://192.168.1.101/webcam/?action=stream instead of /webcam/?action=stream

## TODO:
* [ ] Additional testing.
* [X] Proper error messaging for debugging (e.g. no fully qualified url provided)

## Get Help

If you experience issues with this plugin or need assistance please use the issue tracker by clicking issues above.

### Additional Plugins

Check out my other plugins [here](https://plugins.octoprint.org/by_author/#jneilliii)

### Sponsors
- Andreas Lindermayr
- [@Mearman](https://github.com/Mearman)
- [@TxBillbr](https://github.com/TxBillbr)
- Gerald Dachs
- [@TheTuxKeeper](https://github.com/thetuxkeeper)

### Support My Efforts
I, jneilliii, programmed this plugin for fun and do my best effort to support those that have issues with it, please return the favor and leave me a tip or become a Patron if you find this plugin helpful and want me to continue future development.

[![Patreon](patreon-with-text-new.png)](https://www.patreon.com/jneilliii) [![paypal](paypal-with-text.png)](https://paypal.me/jneilliii)

<small>No paypal.me? Send funds via PayPal to jneilliii&#64;gmail&#46;com</small>

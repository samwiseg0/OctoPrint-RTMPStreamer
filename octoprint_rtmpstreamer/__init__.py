# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import os
import signal
import subprocess
from octoprint.server import user_permission

FFMPEG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'ffmpeg')

class rtmpstreamer(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.SimpleApiPlugin,
                   octoprint.plugin.EventHandlerPlugin):

    def __init__(self):
        self.ffmpeg = None

    ##~~ StartupPlugin
    def on_after_startup(self):
        self._logger.info("OctoPrint-RTMPStreamer loaded!")
        if self._settings.get(["auto_start_on_power_up"]) and self._settings.get(["stream_url"]) != "":
            self._logger.info("Auto starting stream on start up.")
            self.startStream()

    ##~~ TemplatePlugin
    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    ##~~ AssetPlugin
    def get_assets(self):
        return dict(
            js=["js/rtmpstreamer.js"],
            css=["css/rtmpstreamer.css"]
        )

    ##-- EventHandlerPlugin
    def on_event(self, event, payload):
        if event == "PrintStarted" and self._settings.get(["auto_start"]):
            self.startStream()

        if event in ["PrintDone", "PrintCancelled"] and self._settings.get(["auto_start"]):
            self.stopStream()

    ##~~ SettingsPlugin
    def get_settings_defaults(self):
        return dict(view_url="", stream_url="", stream_resolution="640x480", stream_framerate="5", streaming=False,
                    auto_start=False, auto_start_on_power_up=False)

    ##~~ SimpleApiPlugin
    def get_api_commands(self):
        return dict(startStream=[], stopStream=[], checkStream=[])

    def on_api_command(self, command, data):
        if not user_permission.can():
            from flask import make_response
            return make_response("Insufficient rights", 403)

        if command == 'startStream':
            self._logger.info("Start stream command received.")
            self.startStream()
            return
        if command == 'stopStream':
            self._logger.info("Stop stream command received.")
            self.stopStream()
        if command == 'checkStream':
            self._logger.info("Checking stream status.")
            if self.ffmpeg:
                self._plugin_manager.send_plugin_message(self._identifier, dict(status=True, streaming=True))
            else:
                self._plugin_manager.send_plugin_message(self._identifier, dict(status=True, streaming=False))

    ##~~ General Functions
    def startStream(self):
        if self._settings.global_get(["webcam", "stream"]).startswith("/"):
            self._plugin_manager.send_plugin_message(self._identifier, dict(
                error="Webcam stream url is incorrect.  Please configure OctoPrint's Webcam & Timelapse url to include "
                      "fullly qualified url, like http://192.168.0.2/webcam/?action=stream", status=True, streaming=False))
            return

        if not self.ffmpeg:
            filters = []
            if self._settings.global_get(["webcam", "flipH"]):
                filters.append("hflip")
            if self._settings.global_get(["webcam", "flipV"]):
                filters.append("vflip")
            if self._settings.global_get(["webcam", "rotate90"]):
                filters.append("transpose=cclock")
            if len(filters) == 0:
                filters.append("null")
            try:
                # Define settings variables
                webcam_stream = str(self._settings.global_get(["webcam", "stream"]))
                stream_resolution = str(self._settings.get(["stream_resolution"]))
                framerate = str(self._settings.get(["stream_framerate"]))
                rtmp_stream_url = str(self._settings.get(["stream_url"]))
                # Define the FFMPEG command to run
                ffmpeg_cmd = '{} -re -f mjpeg -framerate {} -i {} -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i ' \
                             '/dev/zero -acodec aac -ab 128k -strict experimental -s {} -vcodec h264 -pix_fmt yuv420p ' \
                             '-g 10 -vb 4000k -framerate {} -f flv -filter:v {} {}'.format(FFMPEG,
                                                                                          framerate,
                                                                                          webcam_stream,
                                                                                          stream_resolution,
                                                                                          framerate,
                                                                                          filters,
                                                                                          rtmp_stream_url)
                # Start the ffmpeg subprocess
                self.ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)
                self._plugin_manager.send_plugin_message(self._identifier, dict(status=True, streaming=True))
            except Exception as e:
                self._plugin_manager.send_plugin_message(self._identifier,
                                                         dict(error=str(e), status=True, streaming=False))

    def stopStream(self):
        if self.ffmpeg:
            try:
                os.killpg(os.getpgid(self.ffmpeg.pid), signal.SIGTERM)
                self.ffmpeg = None
                self._plugin_manager.send_plugin_message(self._identifier, dict(status=True, streaming=False))
            except Exception as e:
                self._plugin_manager.send_plugin_message(self._identifier,
                                                         dict(error=str(e), status=True, streaming=False))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(status=True, streaming=False))

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            rtmpstreamer=dict(
                displayName="RTMP Streamer",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="jneilliii",
                repo="OctoPrint-RTMPStreamer",
                current=self._plugin_version,
                stable_branch=dict(
                    name="Stable", branch="master", comittish=["master"]
                ),
                prerelease_branches=[
                    dict(
                        name="Release Candidate",
                        branch="rc",
                        comittish=["rc", "master"],
                    )
                ],

                # update method: pip
                pip="https://github.com/jneilliii/OctoPrint-RTMPStreamer/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "RTMP Streamer"
__plugin_pythoncompat__ = "<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = rtmpstreamer()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

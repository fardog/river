import json
import cgi
import time
import os
from collections import defaultdict

from twisted.web import resource

from river.config import config


class HTTPListener(resource.Resource):
    isLeaf = True
    numberRequests = 0

    def __init__(self):
        pass

    def render_GET(self, request):
        self.numberRequests += 1
        request.setHeader("content-type", "application/json")
        return json.dumps({'request_num': self.numberRequests, })

    def render_POST(self, request):
        self.numberRequests += 1
        request.setHeader("content-type", "application/json")

        command = defaultdict(list)
        command['status'] = 0
        for k, v in request.args.items():
            command[k] = cgi.escape(v[0])

        action_function = self.action(command['command'])
        if action_function:
            action_result = action_function(command)
        else:
            action_result = None

        return json.dumps({'request_num': self.numberRequests,
                           'command': command,
                           'result': action_result,
                          })

    def get_timecode(self, command):
        """ Returns the current server timecode """
        return {'timecode': time.time(), }

    def get_configuration(self, command):
        """
        Returns server configuration information to a remote streamer.
        Future: Returns exact configuration for each discreet device.
        """
        return {'ntp_server': config.get("Server", "ntp_master"), }

    def action(self, command):
        return {'timecode': self.get_timecode,
                'configuration': self.get_configuration,
                }.get(command, None)

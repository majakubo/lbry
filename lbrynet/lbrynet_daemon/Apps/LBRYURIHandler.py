import os
import json
import webbrowser
import sys
from time import sleep
import subprocess

from jsonrpc.proxy import JSONRPCProxy

API_CONNECTION_STRING = "http://localhost:5279/lbryapi"
UI_ADDRESS = "http://localhost:5279"


class LBRYURIHandler(object):
    def __init__(self):
        self.started_daemon = False
        self.start_timeout = 0
        self.daemon = JSONRPCProxy.from_url(API_CONNECTION_STRING)

    def check_status(self):
        status = None
        try:
            status = json.loads(self.daemon.is_running())['result']
            if self.start_timeout < 30 and not status:
                sleep(1)
                self.start_timeout += 1
                self.check_status()
            elif status:
                return True
            else:
                exit(1)
        except:
            if self.start_timeout < 30:
                sleep(1)
                self.start_timeout += 1
                self.check_status()
            else:
                exit(1)

    def handle(self, lbry_name):
        lbry_process = [d for d in subprocess.Popen(['ps','aux'], stdout=subprocess.PIPE).stdout.readlines()
                            if 'LBRY.app' in d]
        try:
            status = json.loads(self.daemon.is_running())['result']
        except:
            pass

        if lbry_process:
            self.check_status()
            started = False
        else:
            os.system("open /Applications/LBRY.app")
            self.check_status()
            started = True

        if lbry_name == "lbry" or lbry_name == "" and not started:
            webbrowser.get('safari').open(UI_ADDRESS)
        else:
            r = json.loads(self.daemon.get({'name': lbry_name}))
            if r['code'] == 200:
                path = r['result']['path'].encode('utf-8')
                extension = os.path.splitext(path)[1]
                if extension in ['mp4', 'flv', 'mov', 'ogv']:
                    webbrowser.get('safari').open(UI_ADDRESS + "/view?name=" + lbry_name)
                else:
                    webbrowser.get('safari').open('file://' + path)
            else:
                webbrowser.get('safari').open('http://lbry.io/get')


def main(args):
    if len(args) != 1:
        args = ['lbry://lbry']

    name = args[0][7:]
    LBRYURIHandler().handle(lbry_name=name)


if __name__ == "__main__":
   main(sys.argv[1:])

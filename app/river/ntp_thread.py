import signal
import datetime
import time
import uuid
import ntplib

from .status_codes import status_code
from .config import config


def ntp_thread(stop_semaphore, lock, instructions, s):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    ntp_master = config.get("Server", "ntp_master")
    if not ntp_master:
        ntp_master = "127.0.0.1"

    while(stop_semaphore.value < 2):
        s.value = status_code.REMOTE_QUERY

        print("[%s] getting clock" % __name__)
        c = ntplib.NTPClient()
        try:
            response = c.request(ntp_master, version=3)
            print("[%s] clock offset %s" % (__name__, response.offset))
        except ntplib.NTPException:
            print("[%s] Error: Couldn't reach NTP Server." % (__name__))

        s.value = status_code.IDLE

        if instructions.poll(config.getint("Server", "ntp_master_poll_time")):
            instruction = instructions.recv()
        else:
            instruction = None

        #if we get a kill signal, die
        if type(instruction) is str and instruction == "kill":
            print("[%s]: Caught kill instruction, dying." % __name__)
            return

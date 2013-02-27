from multiprocessing import Process, Value, Lock, Pipe
import signal
import os

from twisted.web import server
from twisted.internet import reactor

from .http import HTTPListener
from river.utilities import get_open_port
from river.config import config
from river.ntp_thread import ntp_thread
from river.zeroconf import ZeroconfService


def run():
    stop_semaphore = Value('i', 0)
    lock = Lock()

    # define the NTP synchronization thread
    ntp_status = Value('i', 0)
    ntp_parent_conn, ntp_child_conn = Pipe()
    ntp_process = Process(target=ntp_thread,
                          args=(stop_semaphore,
                                lock,
                                ntp_child_conn,
                                ntp_status))
    ntp_process.daemon = True

    if config.getboolean("Server", "randomized_control_port"):
        port = get_open_port()
    else:
        port = config.getint("Server", "control_port")

    service = ZeroconfService(name="River",
                              stype="_river-control._tcp",
                              port=port)

    # define and set our signal handlers
    def signal_handler(signum, frame):
        lock.acquire()
        print("[%s]: Caught kill instruction, dying." % __name__)

        # if we haven't already been told to stop
        if stop_semaphore.value != 2:
            stop_semaphore.value = 2
            service.unpublish()

            ntp_parent_conn.send("kill")
            if reactor.running:
                reactor.stop()

        lock.release()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # announce ourselves via zeroconf
    service.publish()

    # start our NTP sync process
    ntp_process.start()

    # start our HTTP listener
    reactor.listenTCP(port, server.Site(HTTPListener()))
    print ("[%s]: Listening on port %s" % (__name__, port))
    reactor.run()

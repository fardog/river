from multiprocessing import Process, Queue, Pipe, Lock, Value

from river.zeroconf import ZeroconfClient
from river.ntp_thread import ntp_thread
from .listener import listener


def service_found(*args):
    print("[%s] Resolved service %s at %s:%s" %
          (__name__, args[2], args[7], args[8]))

    stop_semaphore = Value('i', 0)
    lock = Lock()

    # define the listener thread
    listener_status = Value('i', 0)
    listener_parent_conn, listener_child_conn = Pipe()
    listener_process = Process(target=listener,
                               args=(stop_semaphore,
                                     lock,
                                     listener_parent_conn,
                                     {'name': args[2],
                                      'address': args[7],
                                      'port': args[8],
                                     },
                                     listener_status))

    print("[%s] Starting up Listener thread" % (__name__))
    listener_process.start()

    listener_process.join()


def run():
    print("[%s] Starting up Zeroconf Listener" % (__name__))
    zconf = ZeroconfClient(stype="_river-control._tcp",
                           reply_handler=service_found)

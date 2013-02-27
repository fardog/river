import signal
import time
import requests
import numpy
import pyaudio
import ntplib
import math
from multiprocessing import Queue

from river.status_codes import status_code
from river.config import config
from river.utilities import sine, silence


def query_configuration(name, address, port):
    r = requests.post("http://%s:%s" % (address, port),
                      params={'command': "configuration"})
    data = r.json()
    ntp_server = data["result"]["ntp_server"]
    if not ntp_server:
        ntp_server = address

    sin_chunks = []
    sin_chunks.append(sine(440, 1, 22500))
    sin_chunk = numpy.concatenate(sin_chunks) * 0.25
    sin_output_chunk = sin_chunk.astype(numpy.float32).tostring()

    silence_chunks = []
    silence_chunks.append(silence(0.05, 22500))
    silence_chunk = numpy.concatenate(silence_chunks) * 0.25
    silence_output_chunk = silence_chunk.astype(numpy.float32).tostring()

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=22500, output=1)

    last = 0
    print("[ntp-sync] getting clock")
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    print("[ntp-sync] clock offset %s" % response.offset)

    while True:
        curtime = int(math.floor(time.time() + response.offset))
        if (curtime % 5) == 0 and curtime > last:
            print curtime
            print("beep")
            last = curtime
            stream.write(sin_output_chunk)
        else:
            stream.write(silence_output_chunk)

    stream.close()
    p.terminate()


def listener(stop_semaphore, lock, instructions, server, s):
    print("[%s] Connecting server named %s." % (__name__, server["name"]))
    query_configuration(server["name"], server["address"], server["port"])

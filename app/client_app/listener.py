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

    DEFAULT_LENGTH = 1
    SAMPLE_RATE = 22500

    sin_chunks = []
    sin_chunks.append(sine(440, DEFAULT_LENGTH, SAMPLE_RATE))
    sin_chunk = numpy.concatenate(sin_chunks) * 0.25
    sin_output_chunk = sin_chunk.astype(numpy.float32).tostring()

    silence_chunks = []
    silence_chunks.append(silence(DEFAULT_LENGTH, SAMPLE_RATE))
    silence_chunk = numpy.concatenate(silence_chunks) * 0.25
    silence_output_chunk = silence_chunk.astype(numpy.float32).tostring()

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=1)

    last = 0
    print("[ntp-sync] getting clock")
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    print("[ntp-sync] clock offset %s" % response.offset)

    while True:
        current_time = time.time() + response.offset
        floored_time = int(math.floor(current_time))
        remaining_time = 5 - (current_time - floored_time + (floored_time % 5))

        if (floored_time % 5) == 0 and floored_time > last:
            print floored_time
            print("beep")
            last = floored_time
            stream.write(sin_output_chunk)
        elif remaining_time < DEFAULT_LENGTH:
            print ("remaining time: %s" % remaining_time)
            samples_to_play = SAMPLE_RATE * 4 - (int(math.ceil((DEFAULT_LENGTH - remaining_time) * (SAMPLE_RATE * 4))))
            print ("playing %s samples" % samples_to_play)
            stream.write(silence_output_chunk[:samples_to_play])
            print ("floored time: %s" % floored_time)
        else:
            stream.write(silence_output_chunk)

    stream.close()
    p.terminate()


def listener(stop_semaphore, lock, instructions, server, s):
    print("[%s] Connecting server named %s." % (__name__, server["name"]))
    query_configuration(server["name"], server["address"], server["port"])

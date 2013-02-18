import math
import numpy
import pyaudio
import time
import ntplib


def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return numpy.sin(numpy.arange(length) * factor)


chunks = []
chunks.append(sine(440, 1, 44100))

chunk = numpy.concatenate(chunks) * 0.25

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)

last = 0
print("[ntp-sync] getting clock")
c = ntplib.NTPClient()
response = c.request('pool.ntp.org', version=3)
print("[ntp-sync] clock offset %s" % response.offset)

while True:
    curtime = int(round(time.time() + response.offset))
    if (curtime % 5) == 0 and curtime > last:
        print curtime
        print("beep")
        last = curtime
        stream.write(chunk.astype(numpy.float32).tostring())

stream.close()
p.terminate()

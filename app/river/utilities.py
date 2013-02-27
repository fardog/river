import math
import numpy


def get_open_port():
    """
    Get a currently unbound TCP Port number
    http://stackoverflow.com/questions/2838244/get-open-tcp-port-in-python
    """
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return numpy.sin(numpy.arange(length) * factor)


def silence(length, rate):
    length = int(length * rate)
    return numpy.zeros(length, dtype=numpy.float32)

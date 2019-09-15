import time
import re
import socket


class Cache(object):
    
    def __init__(self):
        self.data = {}
    
    def Get(self, key, timeout=5):
        if key not in self.data:
            return None
        (expiration, data) = self.data[key]
        if time.time() > expiration + (timeout * 1000):
            del self.data[key]
            return None
        return data
    
    def Insert(self, key, data):
        self.data[key] = (time.time(), data)


def IsValidIPv4(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.')
    except socket.error:
        return False
    return True


def IsValidMacAddress(mac):
    return re.match('[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$', mac.lower())
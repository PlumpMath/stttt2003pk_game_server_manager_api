
import socket,sys,os
import time
import hashlib
import struct,subprocess
import urllib,urllib2
import threading
import random

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        key = '1234'

        self.s = socket.socket()
        self.s.bind(('0.0.0.0', 9999))
        self.s.listen(1)
        print 'ready'

        try:
            while True:
                self.cs, self.address = self.s.accept()
                self.cs.settimeout(5)
                print 'got connected from',self.address

                #send the author info
                md5_hash = hashlib.md5(("%s%s") % (time.time(),random.randint(0,100))).hexdigest()
                self.cs.send(md5_hash[0:30])

                check_code = self.cs.recv(22)
                #print check_code
                check_code_true = hashlib.md5(key + md5_hash[0:20]).hexdigest()[10:]
                #print check_code_true

                if check_code == check_code_true:
                    print 'auth ok'
                else:
                    self.cs.close()
                    print 'auth failed connection closed'

        except KeyboardInterrupt:
            self.s.close()
            sys.exit()

if __name__ == '__main__':
    Server()

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
                try:
                    #send the author info
                    md5_hash = hashlib.md5(("%s%s") % (time.time(),random.randint(0,100))).hexdigest()
                    self.cs.send(md5_hash[0:30])

                    check_code = self.cs.recv(22)
                    #print check_code
                    check_code_true = hashlib.md5(key + md5_hash[0:20]).hexdigest()[10:]
                    #print check_code_true

                    if check_code == check_code_true:
                        print 'auth ok'

                        job_type = self.__read_ShortInt()
                        print 'job_type:%d'%job_type

                        if not isinstance(job_type, int):
                            self.cs.close()

                        if job_type == 1:

                            joblist_id = self.__read_Int()
                            command = self.__read_Char()

                            print joblist_id
                            print command

                        self.cs.close()

                    else:
                        self.cs.close()
                        print 'auth failed connection closed'
                except socket.timeout:
                    print 'timeout'
                    self.cs.close()

        except KeyboardInterrupt:
            self.s.close()
            sys.exit()

    def __read_ShortInt(self):
        try:
            sint, = struct.unpack('!H',self.cs.recv(2))
            return sint
        except:
            return None

    def __read_Int(self):
        try:
            int, = struct.unpack('!I',self.cs.recv(4))
            return int
        except:
            return None

    def __read_Char(self):
        try:
            char_len, = struct.unpack('!I', self.cs.recv(4))
            char_fmt = "!%ds" %char_len
            char, = struct.unpack(char_fmt, self.cs.recv(char_len))
            return char
        except:
            return None

if __name__ == '__main__':
    Server()
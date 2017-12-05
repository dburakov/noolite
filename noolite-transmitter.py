# -*- coding=utf-8 -*-

import sys
import serial
from subprocess import call
from urlparse import urlparse
import logging
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


logger = logging.getLogger(__name__)
PORT_NUMBER = 8080


class SerialPort(object):
    READ_MESSAGE_LENGTH = 17
    CHECK_BIT_MAX_RANGE = 8
    CHECK_BIT_MASK = 0xFF
    CHECK_BIT_POSITION = 15
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600, timeout=1):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.serial.flushInput()
        self.serial.flushOutput()
        
    def publish(self, command):
        check_bit = 0
        for i in range(0, self.CHECK_BIT_MAX_RANGE):
            check_bit += command[i]
        check_bit = check_bit & self.CHECK_BIT_MASK
        command[self.CHECK_BIT_POSITION] = check_bit
        
        buffer = bytearray(command)
        self.serial.write(buffer)
        logger.debug('Serial data written: %s', command)
        
    def close(self):
        self.serial.close()
            

class RequestHandler(BaseHTTPRequestHandler):    
    def parseQuery(self, path):
        query = urlparse(path).query
        if not query:
            return {}
        query_components = dict(qc.split("=") for qc in query.split("&"))
        return query_components
    
    def do_GET(self):
        params = self.parseQuery(self.path)
        port = SerialPort()
        cmd = int(params.get('cmd', 0))
        ch = int(params.get('ch', 0))
        mode = int(params.get('mode', 0))
        ctr = int(params.get('ctr', 0))
        command = [171,mode,ctr,0,ch,cmd,0,0,0,0,0,0,0,0,0,0,172]
        port.publish(command)
        port.close()
        
        help_text = """
            USAGE: 
            
            switch on light (channel 3): http://192.168.100.200:8080/?ch=3&cmd=3
            start binding on channel 5: http://192.168.100.200:8080/?ch=5&mode=1&ctr=3
            erase binding on channel 2: http://192.168.100.200:8080/?ch=2&mode=1&ctr=5
            
            BINDED CHANNELS:
            1 - mpc play
            3 - light
            5 - kitchen-sensor-scenary
            6 - hall-toilet-left-bottom
            
            BINDED COMMANDS:
            2 - on
            0 - off
            3 - slow on  
            1 - slow off
            15 - bind             
        """
        self.send_response(200)
        self.end_headers()        
        self.wfile.write(help_text)
        return

            
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    log = logging.StreamHandler(sys.stdout)
    log.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(log)
    
    try:
        server = HTTPServer(('', PORT_NUMBER), RequestHandler)
        print 'Started httpserver on port ' , PORT_NUMBER
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()

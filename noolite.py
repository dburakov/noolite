# -*- coding=utf-8 -*-

import sys
import serial
from subprocess import call
import logging

logger = logging.getLogger(__name__)


class EventHook(object):
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

class SerialPort(object):
    READ_MESSAGE_LENGTH = 17
    CHECK_BIT_MAX_RANGE = 8
    CHECK_BIT_MASK = 0xFF
    CHECK_BIT_POSITION = 15
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600, timeout=1):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.serial.flushInput()
        self.serial.flushOutput()
        self.onMessage = EventHook()
        
    def publish(self, command):
        check_bit = 0
        for i in range(0, self.CHECK_BIT_MAX_RANGE):
            check_bit += command[i]
        check_bit = check_bit & self.CHECK_BIT_MASK
        command[self.CHECK_BIT_POSITION] = check_bit
        
        buffer = bytearray(command)
        self.serial.write(buffer)
        logger.debug('Serial data written: %s', repr(buffer))
        
    def consume(self):
        while True:
            data = self.serial.read(self.READ_MESSAGE_LENGTH)
            if data:
                logger.debug('Serial data received: %s', repr(data))
                self.onMessage.fire(list(data))
        
    def close(self):
        self.serial.close()
            

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    log = logging.StreamHandler(sys.stdout)
    log.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(log)

    port = SerialPort()
    
    ch = 0 
    cmd = 15 # bind 
    cmd = 2 # on
    cmd = 0 # off
    cmd = 1 # slow off
    cmd = 3 # slow on    
    # command = [171,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,172] # service mode
    command = [171,0,0,0,ch,cmd,0,0,0,0,0,0,0,0,0,0,172] # transmit mode
    # command = [171,1,3,0,1,0,0,0,0,0,0,0,0,0,0,0,172] # ch1 - receiver
    # command = [171,1,3,0,2,0,0,0,0,0,0,0,0,0,0,0,172] # ch2 - receiver    
    # port.publish(command)
    
    def command_handler(command):
        cmd_num = ord(command[4])
        logger.info('Command received: %s', cmd_num)
        if cmd_num == 1:
            call(["mpc", "play"])
        if cmd_num == 2:
            call(["mpc", "pause"])
    
    port.onMessage += command_handler

    try:
        port.consume()
    except KeyboardInterrupt:
        logger.error('Interrupted by keyboard')
        port.close()

# -*- coding=utf-8 -*-

from datetime import datetime, timedelta
import sys
import serial
from subprocess import call
import logging

logger = logging.getLogger(__name__)
LAST_COMMAND_TIME = datetime.now() - timedelta(days=1)


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
            data = list(map(ord,data))
            if data:
                logger.debug('Serial data received: %s', data)
                self.onMessage.fire(data)
        
    def close(self):
        self.serial.close()
            

if __name__ == "__main__":
    CMD_CLICK = 4
    CMD_HOLD = 5
    CMD_REALEASE = 10
    CMD_DBL_CLICK = 101
    
    logger.setLevel(logging.DEBUG)
    log = logging.StreamHandler(sys.stdout)
    log.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(log)

    port = SerialPort()
    
    def command_handler(command):
        global LAST_COMMAND_TIME
        cmd_num = command[4]
        cmd_mode = command[5]
        if (datetime.now() - LAST_COMMAND_TIME).total_seconds() < 1:
            cmd_mode = CMD_DBL_CLICK
            logger.info('DOWBLE-CLICK!')
            
        LAST_COMMAND_TIME = datetime.now()
        logger.info('Command received: %s', cmd_num)
        
        if cmd_mode == CMD_DBL_CLICK:
            if cmd_num == 1:
                call(["mpc", "next"])
        
        if cmd_mode == CMD_CLICK:
            if cmd_num == 1:
                call(["mpc", "play"])
            if cmd_num == 2:
                call(["mpc", "pause"])
        
        if cmd_mode == CMD_HOLD:
            if cmd_num == 1:
                call(["mpc", "volume", "+5"])
            if cmd_num == 2:
                call(["mpc", "volume", "-5"])
    
    port.onMessage += command_handler

    try:
        port.consume()
    except KeyboardInterrupt:
        logger.error('Interrupted by keyboard')
        port.close()

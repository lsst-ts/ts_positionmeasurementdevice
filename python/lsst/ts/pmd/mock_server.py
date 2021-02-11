import logging
import queue
import math

import serial


class MockSerial(serial.Serial):
    def __init__(
        self,
        port,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=3,
        xonxoff=False,
        rtscts=False,
        write_timeout=None,
        dsrdtr=False,
        inter_byte_timeout=None,
        exclusive=None,
    ):
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            xonxoff=xonxoff,
            rtscts=rtscts,
            write_timeout=write_timeout,
            dsrdtr=dsrdtr,
            inter_byte_timeout=inter_byte_timeout,
            exclusive=exclusive,
        )
        self.log = logging.getLogger(__name__)

        self.device = MockMitutoyoHub()
        self.message_queue = queue.Queue()

        self.log.info("Mock Serial created.")

    def read_until(self, character):
        self.log.info("Reading from queue.")
        if not self.message_queue.empty():
            msg = self.message_queue.get()
            return msg.encode()
        raise Exception("Port timed out.")

    def write(self, data):
        self.log.info(data)
        msg = self.device.parse_message(data)
        self.log.debug(msg)
        self.message_queue.put(msg)
        self.log.info("Putting into queue")


class MockMitutoyoHub:
    def __init__(self):
        self.slot_1_position = 0.00009
        self.slot_2_position = math.nan
        self.slot_3_position = math.nan
        self.slot_4_position = math.nan
        self.slot_5_position = math.nan
        self.slot_6_position = math.nan
        self.slot_7_position = math.nan
        self.slot_8_position = math.nan
        self.commands = {
            "1": self.get_slot_1_position,
            "2": self.get_slot_2_position,
            "3": self.get_slot_3_position,
            "4": self.get_slot_4_position,
            "5": self.get_slot_5_position,
            "6": self.get_slot_6_position,
            "7": self.get_slot_7_position,
            "8": self.get_slot_8_position,
        }
        self.log = logging.getLogger(__name__)

    def parse_message(self, msg):
        self.log.info(msg)
        msg = msg.decode().rstrip("\r\n")
        self.log.info(msg)
        if msg in self.commands.keys():
            reply = self.commands[msg]()
            if reply is not None:
                self.log.info(reply)
                return reply
        raise NotImplementedError(f"{msg} not implemented.")

    def get_slot_1_position(self):
        return f"1:{self.slot_1_position:+f}\r"

    def get_slot_2_position(self):
        if not math.isnan(self.slot_2_position):
            return f"2:{self.slot_2_position:+f}\r"
        else:
            return "\r"

    def get_slot_3_position(self):
        if not math.isnan(self.slot_3_position):
            return f"3:{self.slot_3_position:+f}\r"
        else:
            return "\r"

    def get_slot_4_position(self):
        if not math.isnan(self.slot_4_position):
            return f"4:{self.slot_4_position:+f}\r"
        else:
            return "\r"

    def get_slot_5_position(self):
        if not math.isnan(self.slot_5_position):
            return f"5:{self.slot_5_position:+f}\r"
        else:
            return "\r"

    def get_slot_6_position(self):
        if not math.isnan(self.slot_6_position):
            return f"6:{self.slot_6_position:+f}\r"
        else:
            return "\r"

    def get_slot_7_position(self):
        if not math.isnan(self.slot_7_position):
            return f"7:{self.slot_7_position:+f}\r"
        else:
            return "\r"

    def get_slot_8_position(self):
        if not math.isnan(self.slot_8_position):
            return f"8:{self.slot_8_position:+f}\r"
        else:
            return "\r"

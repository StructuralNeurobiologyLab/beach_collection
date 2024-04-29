# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 17:11:30 2023

@author: laura
"""

import serial

class LeicaMicrotomeController:
    def __init__(self, port='COM4', baudrate=19200, timeout=0.1):
        self.dev = serial.Serial(port, baudrate, timeout=timeout)
        print(self.dev)

        #self.dev.open()

    def _calculate_checksum(self, command):
        data = command[1:]
        byte_pairs = [data[i:i+2] for i in range(0, len(data), 2)]
        byte_sum = sum(int(byte, 16) for byte in byte_pairs)
        checksum = (0x100 - (byte_sum % 0x100)) % 0x100
        return format(checksum, '02X')

    def _send_command(self, command):
        comout = command + self._calculate_checksum(command) + "\r"
        comoutbyte = bytes(comout, 'utf-8')
        self.dev.write(comoutbyte)
        return self.dev.readline()

    # System Commands
    def software_reset(self):
        return self._send_command('!81F0')

    def get_part_id(self):
        return self._send_command('!81F1')
    
    def login(self):
        return self._send_command('!81F2')

    def get_version(self):
        return self._send_command('!81F5')

    # Feedrate Motor Control
    def get_feedrate(self):
        return self._send_command(f'!4123FF')
    
    def set_feedrate(self, rate4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!412301{rate4dig}')

    # Similar methods for controlling stage movement (North/South and East/West)
    # Movement N/S
    def stop_NS_motor(self):
        return self._send_command('!413000')
    
    def set_NS_position(self, pos6dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!413001{pos6dig}')
    
    def steps_S_direction(self, S4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!413006{S4dig}')
    
    def steps_N_direction(self, N4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!413007{N4dig}')
    
    def NS_middleposition(self):
        return self._send_command('!41300A01')
    
    # Movement O/W
    def stop_OW_motor(self):
        return self._send_command('!414000')
    
    def set_OW_position(self, pos6dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!414001{pos6dig}')
    
    def steps_O_direction(self, S4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!414006{S4dig}')
    
    def steps_W_direction(self, N4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!414007{N4dig}')
    
    def OW_middleposition(self):
        return self._send_command('!41400A01')
     
    # Cutting motor
    def cutting_motor_off(self):
        return self._send_command('!512000')
    
    def cutting_motor_on(self):
        return self._send_command('!512001')
    
    def cutting_motor_status(self):
        return self._send_command('!5120FF')
    
    def set_cutting_speed(self, c10um4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!5130FF{c10um4dig}')

    def get_cutting_speed(self):
        # Example rate format: '01FFFF'
        return self._send_command(f'!5130FF')

    def set_return_speed(self, r10um4dig):
        # Example rate format: '01FFFF'
        return self._send_command(f'!513101{r10um4dig}')

    def get_return_speed(self):
        # Example rate format: '01FFFF'
        return self._send_command(f'!5131FF')

    
    def get_handwheel_position(self):
        return self._send_command('!5140FF')


    def close(self):
        self.dev.close()
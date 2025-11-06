# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# 6 1/2 Digit Digital Multimeter
# KEYSIGHT : 34461A
#
# TODO:
# Make documentation

import time as _time
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['KEYSIGHT_34461A']


class KEYSIGHT_34461A(_InstrumentBase):
    def __init__(self,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'TCPIP::192.168.13.11::INSTR'
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEYSIGTH 34461A'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF

        self.write('*CLS')
        self.write('*RST')

    @property
    def voltage(self):
        '''Voltage Value'''
        return self.query_float('MEAS:VOLT:DC?')
        
    @property
    def current(self):
        '''DC Currrent Value'''
        return self.query_float('MEAS:CURR:DC?')

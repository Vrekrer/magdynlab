# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# 7 1/2 Digit Nano Volt / Mirco Ohm Meter
# KEYSIGHT : 34420A
#
# TODO:
# Make documentation

import time as _time
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['KEYSIGHT_34420A']


class KEYSIGHT_34420A(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=23, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEYSIGTH 34420A'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF

        self.write('*CLS')
        self.write('*RST')

    @property
    def voltage(self):
        '''Voltage Value'''
        return self.query_float('MEAS:VOLT:DC?')

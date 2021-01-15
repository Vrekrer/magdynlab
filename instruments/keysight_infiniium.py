# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Oscilloscopes
# Keysigth Infiniium series
#
# TODO:
# Clean code
# Make documentation

import numpy as _np
import time
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['KEYSIGHT_Infiniium']


class KEYSIGHT_Infiniium(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=21, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEYSIGHT DSOZ204A'
        self.write('*CLS')
        self.VI.write_termination = None
        self.VI.read_termination = self.VI.LF
        self.write('WAV:FORM WORD')
        self.write('WAV:BYT LSBF') #Little endian
        self.write('WAV:STR OFF')
        self.write('SYST:HEAD OFF')
        self.values_format.is_binary = True
        self.values_format.datatype = 'h'  # Integer 16 bits
        self.values_format.is_big_endian = False

    def getWaveform(self, source='CHAN1', new=False):
        self.write('STOP')
        if new == True:
            self.write('SING')
        while self.query('RSTATE?') != 'STOP':
            time.sleep(0.1)
        self.write('WAV:SOUR %s' % source)
        x_ori = self.query_float('WAV:XOR?')
        x_inc = self.query_float('WAV:XINC?')
        y_ori = self.query_float('WAV:YOR?')
        y_inc = self.query_float('WAV:YINC?')
        raw_data = self.query_values('WAV:DATA?')
        self.ts = _np.arange(len(raw_data)) * x_inc + x_ori
        voltages = raw_data * y_inc + y_ori
        voltages[raw_data == 31232] = _np.nan
        return voltages

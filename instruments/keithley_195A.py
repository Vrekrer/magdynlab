# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Multimiter
# KEITHLEY : 195A
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['KEITHLEY_195']


class KEITHLEY_195(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=17, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEITHLEY 195'
        self.VI.write_termination = ''
        self.VI.read_termination = self.VI.CR + self.VI.LF
        # Voltage Mode
        # Line cicle integration; 1 readings 4 1/2 Digitis
        # SQR disabled
        # Non EOI
        # One shot on X (write 'X')
        # Filters OFF
        self.write('F0S1M0K0T5P0X')

    def filter(self, f):
        '''
        Sets the Filter setting
        Usage :
            Filter(Code)
                Codes :
                 '0' = Filter Disabled
                 '1' = Fron Panel Filter On
                 '2' = Used with 5 1/2 digit resolution mode
                 '3' = Applied to 20mV 200mV DC, etc
        '''
        if f in ['0', '1', '2', '3']:
            self.VI.write('P' + f + 'X')
        else:
            self._log('ERR ', 'Wrong Filter Code')

    def range(self, vRange):
        '''
        Sets the Voltage Range
        values are rounded to aviable upper hardware value
        set to None for Auto Range
        '''
        # Documentation
        # Codes : Values
        # '0'  = Auto
        # '1'  = 20 mV
        # '2'  = 200 mV
        # '3'  = 2 V
        # '4'  = 20 V
        # '5'  = 200 V
        # '6'  = 1000 V
        # '7'  = 1000 V
        if vRange is None:
            self.write('R0X')
        else:
            vRange = _np.abs(vRange)
            bins = [2E-3, 20E-3, 200E-3,
                    2, 20, 200]
            vr_i = _np.abs(_np.array(bins) - vRange).argmin()
            self.write('R%dX' % vr_i)

    @property
    def voltage(self):
        '''Voltage Value'''
        self.write('X')
        return float(self.read()[4:])

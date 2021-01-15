# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Spectrum Analyzer
# Rohde & Schwarz : FSL
#
# TODO:
# Clean code
# Make documentation

import time as _time
import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['RS_FSL']


class RS_FSL(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=19, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'RS FSL'
        self.write('*CLS')
        self.write('SYST:COMM:GPIB:RTER EOI')
        self.VI.write_termination = None
        self.VI.read_termination = None
        self.write('FORM:DATA REAL, 32')
        self.values_format.is_binary = True
        self.values_format.datatype = 'f'  # float 32 bits
        self.values_format.is_big_endian = False

        self.trace = Trace(self)  # Use only one trace ??

    def query(self, command):
        # Remove \n terminations by software
        returnQ = super().query(command)
        return returnQ.strip('\n')

    @property
    def bandwidth(self):
        return self.query_float('SENS:BWID?')

    @bandwidth.setter
    def bandwidth(self, newBW):
        self.write('SENS:BWID %(BW)0.9E' % {'BW': newBW})

    @property
    def center_frequency(self):
        return self.query_float('SENS:FREQ:CENT?')

    @center_frequency.setter
    def center_frequency(self, value):
        self.write('SENS:FREQ:CENT %(value)0.9E' % {'value': value})

    def SetSweep(self, start, stop, np, na=1):
        self.write('SENS:FREQ:STAR %(f)0.9E' % {'f': start})
        self.write('SENS:FREQ:STOP %(f)0.9E' % {'f': stop})
        self.write('SENS:SWE:POIN %(n)d' % {'n': np})
        self.write('SENS:AVER:COUN %(n)d' % {'n': na})
        if na > 1:
            self.write('SENS:AVER:STAT ON' )
        else:
            self.write('SENS:AVER:STAT OFF' )

    def INIT(self):
        while True:
            self.write('INIT:IMM')
            if self.query('SYST:ERR?') == '0,"No error"':
                break

    @property
    def stb(self):
        return self.VI.stb


class Trace(_InstrumentChild):
    def __init__(self, parent, name='TRACE1'):
        super().__init__(parent)
        self.name = name

    def getNewData(self):
        self.write('INIT:CONT OFF')
        self.parent.INIT()
        #TODO Fix this
        while (self.parent.stb & 0b10000): # message available bit
            _time.sleep(0.01)

    def getFDAT(self, new=True):
        '''
        Return formatted trace data,
        accordingly to the selected trace format
        '''
        if new:
            self.getNewData()
        return self.query_values('TRAC:DATA? %(n)s' % {'n' : self.name})

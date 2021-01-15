# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Microwave Signal Generator
# Rohde & Schwarz : SMF100A
#
# TODO:
# Clean code
# Make documentation

import time as _time
import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['RS_SMF']


class RS_SMF(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=28, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'RS SMF100A'
        self.write('*CLS')
        self.write('SYST:COMM:GPIB:RTER EOI')
        self.VI.write_termination = None
        self.VI.read_termination = None

    def query(self, command):
        # Remove \n terminations by software
        returnQ = super().query(command)
        return returnQ.strip('\n')

    @property
    def frequency(self):
        return self.query_float('FREQ?')

    @frequency.setter
    def frequency(self, value):
        self.write('FREQ %(value)0.9E' % {'value': value})

    @property
    def phase(self):
        return self.query_float('PHAS?')

    @phase.setter
    def phase(self, value):
        self.write('PHAS %(value)0.2f' % {'value': value})

    @property
    def power(self):
        return self.query_float('POW:LEV?')

    @power.setter
    def power(self, value):
        self.write('POW:LEV %(value)0.2f' % {'value': value})

    @property
    def attenuation(self):
        return self.query_float('POW:ATT?')

    @attenuation.setter
    def attenuation(self, value):
        self.write('POW:ATT %(value)0.2f' % {'value': value})

    @property
    def output(self):
        '''
        Sets or returns the output status 'ON' or 'OFF'

        The following codes can be used
         'ON', 1, True
         'OFF', 0, False
        '''
        val = self.query('OUTP:STAT?')
        return {'0': 'OFF', '1': 'ON'}[val]

    @output.setter
    def output(self, val):
        out_srt = {'ON':  'ON',
                   1:     'ON',
                   True:  'ON',
                   'OFF': 'OFF',
                   0:     'OFF',
                   False: 'OFF'}.get(val, 'OFF')
        self.write('OUTP:STAT %s' % out_srt)

    @property
    def stb(self):
        return self.VI.stb


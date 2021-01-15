# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Radio Frequency Amplifier model 60/20S1G18A
# by Amplifier Research
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import findResource

__all__ = ['VrekrerTermometers']


class VrekrerTermometers(_InstrumentBase):
    def __init__(self, ResourceName, logFile=None):
        super().__init__(ResourceName, logFile)
        self._IDN = 'RF Amplifier'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF

    def Output(self, out):
        '''
        Enable or disable power supply output

        Usage :
            Output('ON'/'OFF')
        '''
        if out in ['ON', 'OFF']:
            state = {'ON':1, 'OFF':0}[out]
            self.write('P%d' %state)
        else:
            self._log('ERR ', 'Output error code')

    @property
    def ID(self):
        '''ID'''
        return self.query('*IDN?')

    @property
    def SensorCount(self):
        '''Number of present sensors'''
        return self.query_int('DEV:COUNT?')

    @property
    def Temperatures(self):
        '''Measured Temperatures'''
        return = _np.array([self.query_float('MEAS:VOLT? %d' % i) for
                            i in range(self.SensorCount)]

    @property
    def SerialNumbers(self):
        '''Sensors serial numbers'''
        return = _np.array([self.query('DEV:SER? %d' % i) for
                            i in range(self.SensorCount)]


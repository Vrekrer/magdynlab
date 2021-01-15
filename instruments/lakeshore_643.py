# coding=utf-8

# Author: Diego Gonzalez Chavez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Electromagnet Power Suply
# LakeShore 643
#
# TODO:
# Make documentation

import time as _time
import pyvisa.constants as _pvc
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import findResource

__all__ = ['LakeShore_643']

class LakeShore_643(_InstrumentBase):
    def __init__(self,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = findResource('LSCI,MODEL643',
                                        filter_string='ASRL',
                                        timeout=2000,
                                        baud_rate=57600, 
                                        data_bits=7,
                                        parity=_pvc.Parity.odd, 
                                        stop_bits=_pvc.StopBits.one,
                                        read_termination='\r\n',
                                        write_termination='\r\n')
        super().__init__(ResourceName, logFile)
        self._IDN = 'LakeShore 643'
        self.VI.write_termination = self.VI.CR + self.VI.LF
        self.VI.read_termination = self.VI.CR + self.VI.LF
        self.VI.parity=_pvc.Parity.odd
        self.VI.stop_bits=_pvc.StopBits.one
        self.VI.baud_rate=57600
        self.VI.data_bits=7
        self.write('*CLS')
        _time.sleep(0.1)
        self.write('*RST')
        _time.sleep(1)
        self.query('RATE?') #?? Needed??
        self.write('RATE +0.5')  # 0.5 A/s
        _time.sleep(0.1)
        self.write('LIMIT +50.0 +0.5')  # max I 50A , max rate 0.5 A/s
        _time.sleep(0.1)

    def __del__(self):
        self.write('STOP')
        self.write('SETI 0')
        super().__del__()

    def STOP(self):
        '''STOP the current ramp'''
        self.write('STOP')

    def TurnOff(self, wait=False):
        '''
        Set the current to zero.

        If wait=True returns after the current is zeroed
        if wait=False (default) returns immediately.
        '''
        self.write('STOP')
        self.setpoint = 0
        if wait:
            self.WaitRamp()

    @property
    def ramp_done(self):
        '''Whether the setpoint is reached or not'''
        return (self.query_int('OPST?') & 2) != 0   # bit 1 of OPST

    @property
    def ramp_rate(self):
        '''
        Sets or query the ramp rate in A/s
        Max (default) value = 0.5 A/s
        '''
        return self.query_float('RATE?')

    @ramp_rate.setter
    def ramp_rate(self, rRate):
        self.write('RATE %0.4f' % rRate)

    def WaitRamp(self, t_test=0.1):
        '''
        Wait until the output setpoint is reached
        '''
        _time.sleep(t_test)
        while not(self.ramp_done):
            _time.sleep(t_test)

    @property
    def setpoint(self):
        '''
        Sets or return the programed output current setpoint
        '''
        return self.query_float('SETI?')

    @setpoint.setter
    def setpoint(self, cOut):
        self.write('SETI %0.4f' % cOut)

    @property
    def measured_voltage(self):
        '''Measured Voltage Value'''
        return self.query_float('RDGV?')

    @property
    def measured_current(self):
        '''Measured Current Value'''
        return self.query_float('RDGI?')

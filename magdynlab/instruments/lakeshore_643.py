# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Electromagnet Power Suply
# LakeShore 643
#
# TODO:
# Make documentation

import time as _time
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['LakeShore_643']


class LakeShore_643(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=13, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'LakeShore 643'
        self.VI.write_termination = self.VI.CR + self.VI.LF
        self.VI.read_termination = self.VI.CR + self.VI.LF
        self.write('*CLS')
        self.write('*RST')
        self.write('RATE +0.1')  # 0.1 A/s
        self.write('LIMIT +50.0 +0.1')  # max I 50A , max rate 0.1 A/s

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
        self.Set_setpoint(0, wait)

    @property
    def ramp_done(self):
        '''Whether the setpoint is reached or not'''
        return (self.query_int('OPST?') & 2) != 0   # bit 1 of OPST

    @property
    def ramp_rate(self):
        '''
        Sets or query the ramp rate in A/s
        Max (default) value = 0.1 A/s
        '''
        return self.query_float('RATE?')

    @ramp_rate.setter
    def ramp_rate(self, rRate):
        self.write('RATE %0.4f' % rRate)

    def WaitRamp(self, t_test=0.1):
        '''
        Wait until the output setpoint is reached
        '''
        while not(self.rampDone):
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

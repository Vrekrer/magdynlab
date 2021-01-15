# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Voltmeter Arduino Based Hardware build by Diego
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import findResource

__all__ = ['VrekrerVoltMeter']


class VrekrerVoltMeter(_InstrumentBase):
    def __init__(self,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = findResource('VrekrerVoltMeter',
                                        filter_string='ASRL',
                                        timeout=2000,
                                        read_termination='\n',
                                        write_termination='\n')
        super().__init__(ResourceName, logFile)
        self._IDN = 'Vrerker VoltMeter'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF

    @property
    def ID(self):
        '''ID'''
        return self.query('*IDN?')

    @property
    def voltage(self):
        '''Voltage Value'''
        return self.query_float('MEAS:VOLT?')
        
    @property
    def gain(self):
        '''Gain'''
        return self.query_float('CONF:GAIN?')
        
    @property
    def gateway(self):
        '''Default gateway'''
        return self.query('SYST:COMM:LAN:DGAT?')
        
    @property
    def ip(self):
        '''IP address'''
        return self.query('SYST:COMM:LAN:ADDR?')

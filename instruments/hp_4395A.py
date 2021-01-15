# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Network/Spectrum/Impedance Analyzer
# HP / Agilent : 4395A
#
# TODO:
# Clean code
# Make documentation

import time as _time
import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['HP_4395A']


class HP_4395A(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=17, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'HP_4395A'
        #self.write('*CLS')
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.write('FORM3') #data format
        self.values_format.is_binary = True
        self.values_format.datatype = 'd'  # float 64 bits
        self.values_format.is_big_endian = True

    def get_sweep_parameter(self):
        return self.query_values('OUTPSWPRM?')

    def get_Gamma(self, new=True):
        if new:
            self.write('SING')
            self.query('*OPC?')
        data = self.query_values('OUTPDATA?')
        return data[::2] + 1.0j*data[1::2]
        
    def get_Z(self, new=True):
        G = self.get_Gamma(new)
        return (1+G)/(1-G)*50


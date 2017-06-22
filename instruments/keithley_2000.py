# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Multimeter
# KEITHLEY : 2000
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['KEITHLEY_2000']


class KEITHLEY_2000(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=16, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEITHLEY 2000'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF

        time.sleep(0.5)
        self.write('*CLS')
        self.write('*RST')
        time.sleep(0.5)
        self.write('FUNC "VOLT:DC"')
        self.write('VOLT:DC:RANG:UPP 1')
        self.write('VOLT:DC:AVER:TCON MOV')
        self.write('VOLT:DC:AVER:COUN 20')
        self.write('VOLT:DC:DIG 5')
        self.write('INIT:CONT 1')
        
    @property
    def voltage(self):
        '''Voltage Value'''
        return self.query_float('FETCH?')

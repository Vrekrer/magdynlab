# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
#This class controls the: 
#Monopolar Power Supplies
#AGILENT E36XX
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['E3648A']


class E3648A(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=5, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'Lock In DSP 7265'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.logFile = None
        self.VI.write('*CLS')
        self.VI.write('*RST')

    @property
    def output(self):
        return self.query('INST:SEL?')
    @output.setter
    def output(self, value):
        if value in [1, 2]:
            self.write('INST:SEL OUT%d' % value)
        elif value in ['OUTP1', 'OUTP2', 'OUT1', 'OUT2']:
            self.write('INST:SEL %s' % value)
        else:
            print('Output error code') 

    @property
    def outStatus(self):
        stat = int( self.query('OUTP:STAT?') )
        return {1:'ON', 0:'OFF'}[stat] 
    @outStatus.setter
    def outStatus(self, value):
        if value in [0, 1]:
            self.write('OUTP:STAT %s' % {1:'ON', 0:'OFF'}[value])
        elif value in ['ON', 'OFF', 'on', 'off', 'On', 'Off']:
            self.write('OUTP:STAT %s' % value)
        else:
            print('Output Status error code') 
    
    @property
    def range(self):
        return self.query('VOLT:RANG?')
    @range.setter
    def range(self, value):
        self.write('VOLT:RANG %s' %value)

    @property
    def current(self):
        return float( self.query('CURR:LEV:IMM:AMPL?') )
    @current.setter
    def current(self, value):
        self.write('APPL MAX, %0.4f' %value)
        
    @property
    def voltage(self):
        return float( self.query('VOLT:LEV:IMM:AMPL?') )
    @voltage.setter
    def voltage(self, value):
        self.write('APPL %0.4f, MAX' %value)
        
    @property
    def MeasuredVoltage(self):
        #Measured Voltage Value"""
        return float(self.query('MEAS:SCAL:VOLT:DC?'))
    @property
    def MeasuredCurrent(self):
        #Measured Current Value"""
        return float(self.query('MEAS:SCAL:CURR:DC?'))

    def BEEP(self):
        #BEEP
        self.write('SYST:BEEP')



# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Source Meter
# KEITHLEY : 2400
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['KEITHLEY_2400']


class KEITHLEY_2400(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=24, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEITHLEY 2400'
        self.VI.write_termination = None
        self.VI.read_termination = self.VI.LF

        self.write('*CLS')
        self.write('*RST')
        self.SourceVoltageLimit = 1
        self.SourceCurrentLimit = 1E-3

    def __warning(self, *args):
        print([a for a in args])

    @property
    def sense_mode(self):
        '''
        Sets or return the sense mode: '2-Wires' or '4-Wires'

        The following codes can be used to set the sense mode
         4, '4W', 'Remote', '4-Wires'
         2, '2W', 'Local', '2-Wires'
        '''
        val = self.query('SYST:RSEN?')
        return {'0': '2-Wires', '1': '4-Wires'}[val]

    @sense_mode.setter
    def sense_mode(self, val):
        s_str = {4:         '1',
                 '4W':      '1',
                 'Remote':  '1',
                 '4-Wires': '1',
                 2:         '0',
                 '2W':      '0',
                 'Local':   '0',
                 '2-Wires': '0'}.get(val, '1')
        self.write('SYST:RSEN %s' % s_str)

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

    def BEEP(self, freq=2E3, time=0.1):
        self.write('SYST:BEEP %0.2E, %0.2f' % (freq, time))

    @property
    def source_function(self):
        val = self.query('SOUR:FUNC?')
        return {'VOLT': 'Voltage', 'CURR': 'Current'}[val]

    @source_function.setter
    def source_function(self, val):
        source_str = {'Voltage': 'VOLT',
                      'V':       'VOLT',
                      'Current': 'CURR',
                      'I':       'CURR'}.get(val, 'VOLT')
        self.write('SOUR:FUNC %s' % source_str)

    @property
    def source_value(self):
        funct_str = self.query('SOUR:FUNC?')
        return self.query_float('SOUR:%s:LEV:IMM:AMPL?' % funct_str)

    @source_value.setter
    def source_value(self, val):
        funct = self.source_function
        if funct == 'Voltage':
            vMax = self.SourceVoltageLimit
            unit = 'V'
            cmd = 'VOLT'
        else:
            vMax = self.SourceCurrentLimit
            unit = 'A'
            cmd = 'CURR'
        vOut = _np.clip(val, -vMax, vMax)
        if vOut != val:
            self.BEEP(1E3, 0.01)
            self.__warning('KEITHLEY_2400 *warning* : Output %s out of range,'
                           ' %0.2E %s used' % (funct, vOut, unit))
        self.write('SOUR:%s:LEV:IMM:AMPL %0.6E' % (cmd, vOut))

    @property
    def sense_function(self):
        return self.query('SENS:FUNC?')

    @sense_function.setter
    def sense_function(self, val):
        sense_str = {'Voltage': 'VOLT',
                     'V':       'VOLT',
                     'Current': 'CURR',
                     'I':       'CURR'}.get(val, 'VOLT')
        self.write('SENS:FUNC:OFF:ALL')
        self.write('SENS:FUNC \'%s\'' % sense_str)
        self.write('FORM:ELEM:SENS %s' % sense_str)

    @property
    def sense_value(self):
        return self.query_float('READ?')

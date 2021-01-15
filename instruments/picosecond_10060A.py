# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Pulse generator
# PulseLabs : Picosecond 10,060A
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['Picosecond']


class Picosecond(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=3, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'Picosecond'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.write('*RST')
        self.write('HEAD OFF')
        self.pulse = Pulse(self)
        self.trigger = Trigger(self)

    @property
    def stb(self):
        '''
        Status Byte
        '''
        return self.VI.stb

    @property
    def status_info(self):
        '''
        Status Byte Info
        '''
        bits = self.stb
        info = ''
        if bits & (1 << 6-1): #DIO6
            info += 'Command error\n'
        elif bits & (1 << 5-1): #DIO5
            info += 'Execution error\n'
        elif bits & (1 << 4-1): #DIO4
            info += 'Input buffer overflow\n'
        elif bits & (1 << 3-1): #DIO3
            info += 'Query error\n'
        elif bits & (1 << 2-1): #DIO2
            info += 'Output buffer overflow\n'
        else:
            info += 'No error\n'
        return info[:-1]

class Pulse(_InstrumentChild):
    def __init__(self, parent):
        super().__init__(parent)
        self.limit = 1.0

    @property
    def duration(self):
        '''
        Pulse duration
        '''
        return self.query_float('DUR?')

    @duration.setter
    def duration(self, value):
        self.write('DUR %(Value)0.6E' % {'Value': value})

    @property
    def amplitude(self):
        '''
        Pulse amplitude
        '''
        return self.query_float('AMPL?')

    @amplitude.setter
    def amplitude(self, value):
        value = _np.clip(value, 0.0, self._limit)
        self.write('AMPL %(Value)0.6E' % {'Value': value})

    @property
    def limit(self):
        '''
        Amplitude limit
        '''
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value
        _amp = self.amplitude
        _enabled = self.enabled
        self.Disable()
        value = _np.clip(value, 0.0, 10.0)
        self.amplitude = value
        self.write('LIM ON')
        self.amplitude = _amp
        if _enabled:
            self.Enable()

    def Enable(self):
        '''
        Enable pulse output
        '''
        self.write('ENAB')

    def Disable(self):
        '''
        Disable pulse output
        '''
        self.write('DIS')

    @property
    def enabled(self):
        '''
        Is pulse output enabled?
        '''
        value = {'YES' : True, 'NO' : False}[self.query('ENAB?')]
        return value


class Trigger(_InstrumentChild):
    def __init__(self, parent):
        super().__init__(parent)

    @property
    def frequency(self):
        '''
        Internal trigger frequency / pulse repetition frequency
        '''
        return self.query_float('FREQ?')

    @frequency.setter
    def frequency(self, value):
        self.write('FREQ %(Value)0.6E' % {'Value': value})

    @property
    def period(self):
        '''
        Internal trigger period / pulse repetition period
        '''
        return self.query_float('PER?')

    @period.setter
    def period(self, value):
        self.write('PER %(Value)0.6E' % {'Value': value})

    @property
    def delay(self):
        '''
        Delay between the trigger output and the pulse output
        Allowed level values range from 0 to 63ns with 1ns resolution
        '''
        return self.query_float('DEL?')

    @delay.setter
    def delay(self, value):
        value = _np.clip(value, 0.0, 63.0E-9)
        self.write('DEL %(Value)0.1E' % {'Value': value})

    @property
    def level(self):
        '''
        Trigger input level
        Allowed level values range from -2V to +2V with 1mV resolution
        '''
        return self.query_float('LEV?')

    @level.setter
    def level(self, value):
        self.write('LEV %(Value)0.3E' % {'Value': value})

    @property
    def slope(self):
        '''
        Slope of the trigger input signal
        "Positive" : Rising edge
        "Negative" : Falling edge
        '''
        vSlope = self.query('SLOP?')
        return {'POS': 'Positive', 'NEG': 'Negative'}[vSlope]

    @slope.setter
    def slope(self, value):
        vSlope = {'Positive': 'POS',
                  'POS': 'POS',
                  'Negative': 'NEG',
                  'NEG': 'NEG',}[value]
        self.write('SLOP %(Value)s' % {'Value': vSlope})

    @property
    def source(self):
        '''
        Trigger source
        "Internal" : Determined by period or frequency parameters
        "External" : Trigger input BNC connector
        "Manual" : Manual Trigger key
        "GPIB" : Trigger signal from the GPIB
        '''
        vTrig = self.query('TRIG?')
        trigDict = {'INT' : 'Internal',
                    'EXT' : 'External',
                    'MAN' : 'Manual',
                    'GPIB' : 'GPIB'}
        return trigDict[vTrig]

    @source.setter
    def source(self, value):
        vTrig = {'INT' : 'INT',
                 'EXT' : 'EXT',
                 'MAN' : 'MAN',
                 'Internal' : 'INT',
                 'External' : 'EXT',
                 'Manual' : 'MAN',
                 'GPIB' : 'GPIB'}[value]
        self.write('TRIG %(Value)s' % {'Value': vTrig})

    @property
    def gating(self):
        '''
        Trigger gating
        When this is set ON, the generator will not trigger
        unless there is a high TTL logic level applied
        at the gate BNC input
        '''
        return self.query('GATE?')

    @gating.setter
    def gating(self, value):
        vGate = {True : 'ON',
                 False : 'OFF',
                 'ON' : 'ON',
                 'OFF' : 'OFF'}[value]
        self.write('GATE %(Value)s' % {'Value': vGate})

    @property
    def hysteresis(self):
        '''
        Trigger Hysteresis
        '''
        return self.query('HYST?')

    @hysteresis.setter
    def hysteresis(self, value):
        vHist = {True : 'ON',
                 False : 'OFF',
                 'ON' : 'ON',
                 'OFF' : 'OFF'}[value]
        self.write('HYST %(Value)s' % {'Value': vHist})
        
    def Trigger(self):
        self.write('*TRG')

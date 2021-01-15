# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Impedance analyzer
# KEYSIGHT : E4990A
#
# TODO:
# Make documentation

import time as _time
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['KEYSIGHT_E4990A']


class KEYSIGHT_E4990A(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=17, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEYSIGTH E4990A'
        self.VI.write_termination = None
        self.VI.read_termination = None

        self.write('*CLS')
        self.write('FORMat:DATA REAL')
        self.write('FORMat:BORDer NORM')
        self.values_format.is_binary = True
        self.values_format.datatype = 'd'  # float 64 bits
        self.values_format.is_big_endian = True
        self.Ch1 = Channel(self, 1)
        self.write('INIT1:CONT ON')

    def query(self, command):
        # Remove \n terminations by software
        returnQ = super().query(command)
        return returnQ.strip('\n')


class Channel(_InstrumentChild):
    def __init__(self, parent, ChanNum=1, ID='Auto'):
        super().__init__(parent)
        self._number = ChanNum
        if ID == 'Auto':
            self.ID = 'Ch%d' % self.number
        else:
            self.ID = ID
        # self.write('CONF:CHAN%d:STAT ON' % self.number)

    def SetSweep(self, start, stop, step, np=50):
        self.write('SENS%(Ch)d:FREQ:STAR %(f)0.11E' %
                   {'Ch': self.number, 'f': start})
        self.write('SENS%(Ch)d:FREQ:STOP %(f)0.11E' %
                   {'Ch': self.number, 'f': stop})
        self.write('SENS%(Ch)d:SWE:POIN %(n)d' %
                   {'Ch': self.number, 'n': np})

    @property
    def fs(self):
        return self.getSTIM()

    def getSTIM(self):
        return self.query_values('SENS%(Ch)d:FREQ:DATA?' % {'Ch': self.number})

    @property
    def number(self):
        return self._number

    @property
    def source_mode(self):
        return self.query('SOUR%(Ch)d:MODE?' % {'Ch': self.number})

    @source_mode.setter
    def source_mode(self, val):
        source_str = {'Voltage': 'VOLT',
                      'V':       'VOLT',
                      'Current': 'CURR',
                      'I':       'CURR'}.get(val, 'VOLT')
        self.write('SOUR%(Ch)d:MODE %(mode)s' %
                   {'Ch': self.number, 'mode': source_str})

    @property
    def source_voltage(self):
        return self.query_float('SOUR%(Ch)d:VOLT?' % {'Ch': self.number})

    @source_voltage.setter
    def source_voltage(self, val):
        self.write('SOUR%(Ch)d:VOLT %(val)0.3E' % 
                   {'Ch': self.number, 'val': val})

    @property
    def bias_mode(self):
        return self.query('SOUR%(Ch)d:BIAS:MODE?' % {'Ch': self.number})

    @bias_mode.setter
    def bias_mode(self, val):
        source_str = {'Voltage': 'VOLT',
                      'V':       'VOLT',
                      'Current': 'CURR',
                      'I':       'CURR'}.get(val, 'VOLT')
        self.write('SOUR%(Ch)d:BIAS:MODE %(mode)s' %
                   {'Ch': self.number, 'mode': source_str})

    @property
    def bias_voltage(self):
        return self.query_float('SOUR%(Ch)d:BIAS:VOLT?' % {'Ch': self.number})

    @bias_voltage.setter
    def bias_voltage(self, val):
        self.write('SOUR%(Ch)d:BIAS:VOLT %(val)0.3E' % 
                   {'Ch': self.number, 'val': val})

    @property
    def traces(self):
        trcCount = self.query_int('CALC%(Ch)d:PAR:COUN?' %
                                  {'Ch': self.number})
        vTraces = []
        for trN in range(trcCount):
            tr = Trace(self, trN)
            if tr.channel_number == self.number:
                vTraces.append(tr)
        return vTraces

    def TRIG(self):
        while True:
            while self.query_int('STAT:OPER:COND?') & (1 << 4):
                _time.sleep(0.01)
            self.write('TRIG:IMM')
            if self.query('SYST:ERR?') == '+0,"No error"':
                break
            _time.sleep(0.1)

class Trace(_InstrumentChild):
    def __init__(self, parent, trcNum):
        super().__init__(parent)
        self._trcNum = trcNum
        self._ChNumber = parent.number

    @property
    def channel_number(self):
        '''Channel Number'''
        return self._ChNumber

    def getNewData(self):
        ChN = self.channel_number
        self.write('TRIG:SOUR BUS')
        averStat = self.query('SENS%(Ch)d:AVER:STAT?' % {'Ch': ChN})
        if averStat == '1':
            averCount = self.query_int('SENS%(Ch)d:AVER:COUN?' % {'Ch': ChN})
            self.write('CALC%(Ch)d:AVER:CLE' % {'Ch': ChN})
        else:
            averCount = 1
        for i in range(averCount):
            self.parent.TRIG()
            # test bit4 Measuring
            while self.query_int('STAT:OPER:COND?') & (1 << 4):
                _time.sleep(0.01)

    def getFDAT(self, New=False):
        '''
        Return formatted trace data,
        accordingly to the selected trace format
        '''
        ChN = self.channel_number
        self.write('CALC%(Ch)d:PAR%(Ch)d:SEL' %
                   {'Ch': ChN, 'N': self._trcNum})
        if New:
            self.getNewData()
        FDAT = self.query_values('CALC%(Ch)d:DATA:FDAT?' % {'Ch': ChN})
        return FDAT[::2] + 1.0j*FDAT[1::2]

    def getRDAT(self, New=False):
        '''
        Returns raw trace data :
        Real and imaginary part of each measurement point
        '''
        ChN = self.channel_number
        self.write('CALC%(Ch)d:PAR%(Ch)d:SEL' %
                   {'Ch': ChN, 'N': self._trcNum})
        if New:
            self.getNewData()
        RDAT = self.query_values('CALC%(Ch)d:DATA:RDAT?' % {'Ch': ChN})
        return RDAT[::2] + 1.0j*RDAT[1::2]

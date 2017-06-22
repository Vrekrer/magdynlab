# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Vector Network Analyzer
# Rohde & Schwarz : VNA Z24
#
# TODO:
# Clean code
# Make documentation

import time as _time
import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['RS_VNA_Z']


class RS_VNA_Z(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=20, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'R&S VNA'
        self.write('*CLS')
        self.write('SYST:COMM:GPIB:RTER EOI')
        self.VI.write_termination = None
        self.VI.read_termination = None
        self.write('FORM:DATA REAL, 64')
        self.Ch1 = Channel(self, 1)
        #  self.Ch2 = Channel(self, 2)

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
        self.write('CONF:CHAN%d:STAT ON' % self.number)

    @property
    def number(self):
        return self._number

    @property
    def traces(self):
        TrcNames = self.query('CONF:TRAC:CAT?').strip('\'').split(',')[1::2]
        vTraces = []
        for trN in TrcNames:
            tr = Trace(self, trN)
            if tr.channel_number == self.number:
                vTraces.append(tr)
        return vTraces

    @property
    def bandwidth(self):
        return self.query_float('SENS%(Ch)d:BWID?' % {'Ch': self.Number})

    @bandwidth.setter
    def bandwidth(self, newBW):
        self.write('SENS%(Ch)d:BWID %(BW)0.9E' %
                   {'Ch': self.Number, 'BW': newBW})

    def SetSweep(self, start, stop, np, na=50):
        self.write('SENS%(Ch)d:FREQ:STAR %(f)0.9E' %
                   {'Ch': self.number, 'f': start})
        self.write('SENS%(Ch)d:FREQ:STOP %(f)0.9E' %
                   {'Ch': self.number, 'f': stop})
        self.write('SENS%(Ch)d:SWE:POIN %(n)d' %
                   {'Ch': self.number, 'n': np})
        self.write('SENS%(Ch)d:AVER:COUN %(n)d' %
                   {'Ch': self.number, 'n': na})
        if na > 1:
            self.write('SENS%(Ch)d:AVER:STAT ON' % {'Ch': self.number})
        else:
            self.write('SENS%(Ch)d:AVER:STAT OFF' % {'Ch': self.number})

    def getSTIM(self):
        return self.query_values('CALC%(Ch)d:DATA:STIM?' % {'Ch': self.number})

    def INIT(self):
        while True:
            self.write('INIT%(Ch)d:IMM' % {'Ch': self.Number})
            if self.query('SYST:ERR:ALL?') == '0,"No error"':
                break


class Trace(_InstrumentChild):
    def __init__(self, parent, Name='Auto'):
        super().__init__(parent)
        self.name = Name
        self._ChNumber = self.query_int('CONF:TRAC:CHAN:NAME:ID? \'%s\''
                                        % Name)

    @property
    def channel_number(self):
        '''Channel Number'''
        return self._ChNumber

    def getNewData(self):
        ChN = self.channel_number
        self.write('INIT:CONT OFF')
        averStat = self.query('SENS%(Ch)d:AVER:STAT?' % {'Ch': ChN})
        if averStat == '1':
            averCount = self.query_int('SENS%(Ch)d:AVER:COUN?' % {'Ch': ChN})
            self.write('SENS%(Ch)d:AVER:CLE' % {'Ch': ChN})
        else:
            averCount = 1
        for i in range(averCount):
            self.parent.INIT()
            while self.query('CALC%(Ch)d:DATA:NSW:COUN?' % {'Ch': ChN}) == '0':
                _time.sleep(0.01)

    def getFDAT(self, New=False):
        '''
        Return formatted trace data,
        accordingly to the selected trace format
        '''
        ChN = self.channel_number
        self.write('CALC%(Ch)d:PAR:SEL \'%(N)s\'' %
                   {'Ch': ChN, 'N': self.name})
        if New:
            self.getNewData()
        return self.query_values('CALC%(Ch)d:DATA? FDAT' % {'Ch': ChN})

    def getSDAT(self, New=False):
        '''
        Returns unformatted trace data :
        Real and imaginary part of each measurement point
        For wave quantities the unit is Volts
        '''
        ChN = self.channel_number
        self.write('CALC%(Ch)d:PAR:SEL \'%(N)s\'' %
                   {'Ch': ChN, 'N': self.name})
        if New:
            self.getNewData()
        SDAT = self.query_values('CALC%(Ch)d:DATA? SDAT' % {'Ch': ChN})
        return SDAT[::2] + 1.0j*SDAT[1::2]

    def SaveSData(self, fileName, New=False):
        f = self.parent.getSTIM()
        S = self.getSDAT(New)
        _np.savetxt(fileName, _np.array([f, S.real, S.imag]).T, fmt='%.16E')

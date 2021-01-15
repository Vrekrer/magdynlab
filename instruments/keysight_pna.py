# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Vector Network Analyzer
# Keysight PNA series
#
# TODO:
# Clean code
# Make documentation

import numpy as _np
import time as _time
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import InstrumentChild as _InstrumentChild

__all__ = ['KEYSIGHT_PNA']


class KEYSIGHT_PNA(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=16, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEYSIGHT PNA'
        self.write('*CLS')
        self.VI.write_termination = None
        self.VI.read_termination = None
        self.VI.timeout = 2000
        self.VI.chunk_size = 1024000
        self.write('FORM:DATA REAL, 64')
        self.values_format.is_binary = True
        self.values_format.datatype = 'd'  # float 64 bits
        self.values_format.is_big_endian = True
        self.Ch1 = Channel(self, 1)
        # self.Ch2 = Channel(self, 2)

    def query(self, command):
        # Remove \n terminations by software
        returnQ = super().query(command)
        return returnQ.strip('\n')

    @property
    def auxiliar_voltage_output1(self):
        return self.query_float('CONT:AUX:OUTP1:VOLT?')

    @auxiliar_voltage_output1.setter
    def auxiliar_voltage_output1(self, newVoltage):
        self.write('CONT:AUX:OUTP1:VOLT %0.3f' % newVoltage)

    @property
    def auxiliar_voltage_output2(self):
        return self.query_float('CONT:AUX:OUTP2:VOLT?')

    @auxiliar_voltage_output2.setter
    def auxiliar_voltage_output2(self, newVoltage):
        self.write('CONT:AUX:OUTP2:VOLT %0.3f' % newVoltage)


class Channel(_InstrumentChild):
    def __init__(self, parent, ChanNum=1, ID='Auto'):
        super().__init__(parent)
        self._number = ChanNum
        if ID == 'Auto':
            self.ID = 'Ch%d' % self.number
        else:
            self.ID = ID
        # self.write('CONF:CHAN%d:STAT ON' % self.number)

    @property
    def number(self):
        return self._number

    @property
    def traces(self):
        TrcNames = self.query('CALC:PAR:CAT:EXT?').strip('\"').split(',')[0::2]
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

    def SetSweep(self, start, stop, np, na=None):
        self.write('SENS%(Ch)d:SWE:TYPE LIN' %
                   {'Ch':self.number})

        self.write('SENS%(Ch)d:SWE:POIN %(n)d' %
                   {'Ch':self.number, 'n':np})
        self.write('SENS%(Ch)d:FREQ:STAR %(f)0.9E' %
                   {'Ch':self.number, 'f':start})
        self.write('SENS%(Ch)d:FREQ:STOP %(f)0.9E' %
                   {'Ch':self.number, 'f':stop})

        if na is not None:
            self.write('SENS%(Ch)d:AVER:COUN %(n)d' %
               {'Ch':self.number, 'n':na})
            if na > 1:
                self.write('SENS%(Ch)d:AVER:STAT ON' % {'Ch':self.number})
            else:
                self.write('SENS%(Ch)d:AVER:STAT OFF' % {'Ch':self.number})

    def SetFrequencies(self, fs):
        self.write('SENS%(Ch)d:SEGM1:CLE' %
                   {'Ch': self.number})

        fs = _np.atleast_1d(fs).copy()
        fs.sort()
        if len(fs)%2 != 0:
            fs = _np.r_[fs, [fs[-1]]]
        for sgn in range(len(fs)//2):
            self.write('SENS%(Ch)d:SEGM%(sg)d:ADD' %
                       {'Ch': self.number, 'sg': sgn+1})
            self.write('SENS%(Ch)d:SEGM%(sg)d:FREQ:START %(f)0.9E' %
                       {'Ch': self.number, 'sg': sgn+1, 'f':fs[2*sgn]})
            self.write('SENS%(Ch)d:SEGM%(sg)d:FREQ:STOP %(f)0.9E' %
                       {'Ch': self.number, 'sg': sgn+1, 'f':fs[2*sgn+1]})
            npts = 2
            if fs[2*sgn+1] == fs[2*sgn]:
                npts = 1
            self.write('SENS%(Ch)d:SEGM%(sg)d:SWE:POIN %(npts)d' %
                       {'Ch':self.number, 'sg':sgn+1, 'npts':npts})
        self.write('SENS%(Ch)d:SWE:TYPE SEGM' %
                   {'Ch':self.number})

    def getSTIM(self):
        return self.query_values('CALC:MEAS:X?')

    def INIT(self):
        while True:
            if 'No error' in self.query('SYST:ERR?'):
                break
        while True:
            self.write('INIT%(Ch)d:IMM' % {'Ch': self.number})
            if 'No error' in self.query('SYST:ERR?'):
                break
            else:
                _time.sleep(0.5)


class Trace(_InstrumentChild):
    def __init__(self, parent, Name='Auto'):
        super().__init__(parent)
        self.name = Name
        self._ChNumber = 1
        # self.query_int('CONF:TRAC:CHAN:NAME:ID? \'%s\'' % Name)

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
            self.query('*OPC?')

    def getFDAT(self, New=False):
        '''
        Return formatted trace data,
        accordingly to the selected trace format
        '''
        ChN = self.channel_number
        self.write('CALC%(Ch)d:PAR:SEL \'%(N)s\'' %
                   {'Ch': ChN, 'N': self.name})
        MeasN = self.query_int('CALC%(Ch)d:PAR:MNUM?' %
                               {'Ch': ChN})
        if New:
            self.getNewData()
        return self.query_values('CALC%(Ch)d:MEAS%(MeasN)d:DATA:FDAT?' 
                                 % {'Ch': ChN, 'MeasN': MeasN})

    def getSDAT(self, New=False):
        '''
        Returns unformatted trace data :
        Real and imaginary part of each measurement point
        For wave quantities the unit is Volts
        '''
        ChN = self.channel_number
        self.write('CALC%(Ch)d:PAR:SEL \'%(N)s\'' %
                   {'Ch': ChN, 'N': self.name})
        MeasN = self.query_int('CALC%(Ch)d:PAR:MNUM?' %
                               {'Ch': ChN})
        if New:
            self.getNewData()
        try:
            _time.sleep(0.05)
            SDAT = self.query_values('CALC%(Ch)d:MEAS%(MeasN)d:DATA:SDATA?' 
                                     % {'Ch': ChN, 'MeasN': MeasN})
        except:
            self.query('*OPC?')
            _time.sleep(0.05)
            SDAT = self.query_values('CALC%(Ch)d:MEAS%(MeasN)d:DATA:SDATA?' 
                                     % {'Ch': ChN, 'MeasN': MeasN})
        return SDAT[::2] + 1.0j*SDAT[1::2]

    def SaveSData(self, fileName, New=False):
        f = self.parent.getSTIM()
        S = self.getSDAT(New)
        _np.savetxt(fileName, _np.array([f, S.real, S.imag]).T, fmt='%.16E')

# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Lock-In Amplifier
# Stanford Research Systems: SR530
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['SRS_SR530']


class SRS_SR530(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=23, GPIB_Device=0, RemoteOnly=False,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'SRS_SR530'
        self.VI.write_termination = self.VI.CR + self.VI.LF
        self.VI.read_termination = self.VI.CR + self.VI.LF
        self.write('B1')  # Set Band Pass Filter
        self.write('L1,1')  # Set Notch Filter x1
        self.write('L2,1')  # Set Notch Filter x1
        self.write('R0')  # Positive edge ref trigger
        self.write('S2')  # Output R and Phase
        self.write('C0')  # Display frequency on the LCD
        self.RemoteOnly(RemoteOnly)

    def RemoteOnly(self, rO=True):
        if rO:
            self.write('I1')
        else:
            self.write('I0')

    @property
    def TC(self):
        '''
        Sets or return the Filter Time Constant
        setted values are rounded to aviable hardware value.
        '''
        # #Documentation#
        # TC Codes :
        # '1'  = 1 ms
        # '2'  = 3 ms
        # '3'  = 10 ms
        # '4'  = 30 ms
        # '5'  = 100 ms
        # '6'  = 300 ms
        # '7' = 1 s
        # '8' = 3 s
        # '9' = 10 s
        # '10' = 30 s
        # '11' = 100 s
        tc_i = self.query_int('T1')
        bins = [0, 1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1, 3, 10, 30, 100]
        return bins[tc_i]

    @TC.setter
    def TC(self, tc):
        tc = _np.abs(tc)
        bins = [1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1, 3, 10, 30, 100]
        tc_i = _np.abs(_np.array(bins) - tc).argmin() + 1
        self.write('T1,%d' % tc_i)

    @property
    def SEN(self):
        '''
        Sets or return the Full Scale Sensitivity
        setted values rounded to aviable hardware value.
        '''
        # #Documentation#
        # SEN  Codes
        # Codes : Voltage  Current
        #  '1'  = 10 nV    10 fA
        #  '2'  = 20 nV    20 fA
        #  '3'  = 50 nV    50 fA
        #  '4'  = 100 nV   100 fA
        #  '5'  = 200 nV   200 fA
        #  '6'  = 500 nV   500 fA
        #  '7'  = 1 uV     1 pA
        #  '8'  = 2 uV     2 pA
        #  '9' = 5 uV     5 pA
        #  '10' = 10 uV    10 pA
        #  '11' = 20 uV    20 pA
        #  '12' = 50 uV    50 pA
        #  '13' = 100 uV   100 pA
        #  '14' = 200 uV   200 pA
        #  '15' = 500 uV   500 pA
        #  '16' = 1 mV     1 nA
        #  '17' = 2 mV     2 nA
        #  '18' = 5 mV     5 nA
        #  '19' = 10 mV    10 nA
        #  '20' = 20 mV    20 nA
        #  '21' = 50 mV    50 nA
        #  '22' = 100 mV   100 nA
        #  '23' = 200 mV   200 nA
        #  '24' = 500 mV   500 nA
        sen_i = self.query_int('G')
        vSen = [0, 10E-9, 20E-9, 50E-9,
                100E-9, 200E-9, 500E-9,
                1E-6, 2E-6, 5E-6,
                10E-6, 20E-6, 50E-6,
                100E-6, 200E-6, 500E-6,
                1E-3, 2E-3, 5E-3,
                10E-3, 20E-3, 50E-3,
                100E-3, 200E-3, 500E-3,
                1E-6][sen_i]
        return vSen

    @SEN.setter
    def SEN(self, vSen):
        vSen = _np.abs(vSen)
        bins = [10E-9, 20E-9, 50E-9,
                100E-9, 200E-9, 500E-9,
                1E-6, 2E-6, 5E-6,
                10E-6, 20E-6, 50E-6,
                100E-6, 200E-6, 500E-6,
                1E-3, 2E-3, 5E-3,
                10E-3, 20E-3, 50E-3,
                100E-3, 200E-3, 500E-3,
                1E-6]
        sen_i = _np.abs(_np.array(bins) - vSen).argmin() + 1
        self.write('G%d' % sen_i)

    @property
    def X(self):
        return self.query_float('QX')

    @property
    def Y(self):
        return self.query_float('QY')

    @property
    def Magnitude(self):
        return self.query_float('Q1')

    @property
    def Phase(self):
        return self.query_float('Q2')

    @property
    def Freq(self):
        return self.query_float('F')

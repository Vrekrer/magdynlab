# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# DSP Lock-In Amplifier
# Stanford Research Systems: SR844
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['SRS_SR844']

class SRS_SR844(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=8, GPIB_Device=0, RemoteOnly=False,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'SRS_SR844'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.write('OUTX 1') #GPIB Mode
        self.RemoteOnly(RemoteOnly)
        
        
    def RemoteOnly(self, rO = True):
        if rO:
            self.write('OVRM 0')
        else:
            self.write('OVRM 1')

            
    @property
    def TC(self):
        '''
        Sets or return the Filter Time Constant
        setted values are rounded to aviable hardware value.
        '''
        # #Documentation#
        # TC Codes :
        # '0'  = 100 us
        # '1'  = 300 us
        # '2'  = 1 ms
        # '3'  = 3 ms
        # '4'  = 10 ms
        # '5'  = 30 ms
        # '6'  = 100 ms
        # '7'  = 300 ms
        # '8' = 1 s
        # '9' = 3 s
        # '10' = 10 s
        # '11' = 30 s
        # '12' = 100 s
        # '13' = 300 s
        # '14' = 1 ks
        # '15' = 3 ks
        # '16' = 10 ks
        # '17' = 30 ks
        tc_i = self.query_int('OFLT?')
        bins = [100E-6, 300E-6,
                1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1, 3, 10, 30, 100, 300,
                1E3, 3E3, 10E3, 30E3]
        return bins[tc_i]

    @TC.setter
    def TC(self, tc):
        tc = _np.abs(tc)
        bins = [100E-6, 300E-6,
                1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1, 3, 10, 30, 100, 300,
                1E3, 3E3, 10E3, 30E3]
        tc_i = _np.abs(_np.array(bins) - tc).argmin()
        self.write('OFLT %d' % tc_i)
        
    @property
    def SEN(self):
        '''
        Sets or return the Full Scale Sensitivity
        setted values rounded to aviable hardware value.
        '''
        # #Documentation#
        # SEN  Codes
        # Codes : Voltage
        #  '0'  = 100 nV
        #  '1'  = 300 nV 
        #  '2'  = 1   uV 
        #  '3'  = 3   uV 
        #  '4'  = 10  uV 
        #  '5'  = 30  uV 
        #  '6'  = 100 uV 
        #  '7'  = 300 uV 
        #  '8'  = 1   mV 
        #  '9'  = 3   mV 
        #  '10' = 10  mV 
        #  '11' = 30  mV
        #  '12' = 100 mV
        #  '13' = 300 mV
        #  '14' = 1   V
        sen_i = self.query_int('SENS?')
        vSen = [100E-9, 300E-9,
                1E-6, 3E-6, 10E-6, 30E-6, 100E-6, 300E-6,
                1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1]
        return vSen
        
    @SEN.setter
    def SEN(self, vSen):
        vSen = _np.abs(vSen)
        bins = [100E-9, 300E-9,
                1E-6, 3E-6, 10E-6, 30E-6, 100E-6, 300E-6,
                1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1]
        sen_i = _np.abs(_np.array(bins) - vSen).argmin()
        self.write('SENS %d' % sen_i)
    
    def FilterSlope(self, sl):
        '''
        Set the output filter slope
        Usage :
            FilterSlope(Code)
                Codes :
                 '0' = 6 dB/octave
                 '1' = 12 dB/octave
                 '2' = 18 dB/octave
                 '3' = 24 dB/octave
        '''
        if sl in ['0', '1', '2', '3']:
            self.write('OFSL %s' % sl)
        else:
            self._log('ERR ', 'Wrong Slope Code')

    def setOscilatorFreq(self, freq):
        '''Set the internal Oscilator Frequency'''
        self.write('FREQ %0.6f' % freq)
        
    def getReferenceFreq(self):
        return numpy.float(self.query('FRAQ?'))
          
    def setRefPhase(self, ph):
        #Set the phase reference"""
        self.write('PHAS %0.6f' %ph)
        
    def getRefPhase(self):
        #Get the programed phase reference"""
        return numpy.float(self.query('PHAS?'))
        
            
    @property
    def X(self):
        return self.query_float('OUTP? 1')

    @property
    def Y(self):
        return self.query_float('OUTP? 2')

    @property
    def Magnitude(self):
        return self.query_float('OUTP? 3')

    @property
    def Phase(self):
        return self.query_float('OUTP? 4')

    @property
    def Freq(self):
        return self.query_float('FRAQ?')
        
    @property
    def AUX_In_1(self):
        return self.query_float('OAUX?1')

    @property
    def AUX_In_2(self):
        return self.query_float('OAUX?2')
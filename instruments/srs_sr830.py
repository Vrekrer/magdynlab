# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# DSP Lock-In Amplifier
# Stanford Research Systems: SR830
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['SRS_SR830']


class SRS_SR830(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=8, GPIB_Device=0, RemoteOnly=False,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'SRS_SR830'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.write('OUTX 1')  # GPIB Mode
        self.RemoteOnly(RemoteOnly)

    def RemoteOnly(self, rO=True):
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
        # '0'  = 10 us
        # '1'  = 30 us
        # '2'  = 100 us
        # '3'  = 300 us
        # '4'  = 1 ms
        # '5'  = 3 ms
        # '6'  = 10 ms
        # '7'  = 30 ms
        # '8'  = 100 ms
        # '9'  = 300 ms
        # '10' = 1 s
        # '11' = 3 s
        # '12' = 10 s
        # '13' = 30 s
        # '14' = 100 s
        # '15' = 300 s
        # '16' = 1 ks
        # '17' = 3 ks
        # '18' = 10 ks
        # '19' = 30 ks
        tc_i = self.query_int('OFLT?')
        bins = [10E-6, 30E-6, 100E-6, 300E-6,
                1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
                1, 3, 10, 30, 100, 300,
                1E3, 3E3, 10E3, 30E3]
        return bins[tc_i]

    @TC.setter
    def TC(self, tc):
        tc = _np.abs(tc)
        bins = [10E-6, 30E-6, 100E-6, 300E-6,
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
        # Codes : Voltage  Current
        #  '0'  = 2 nV     2 fA
        #  '1'  = 5 nV     5 fA
        #  '2'  = 10 nV    10 fA
        #  '3'  = 20 nV    20 fA
        #  '4'  = 50 nV    50 fA
        #  '5'  = 100 nV   100 fA
        #  '6'  = 200 nV   200 fA
        #  '7'  = 500 nV   500 fA
        #  '8'  = 1 uV     1 pA
        #  '9'  = 2 uV     2 pA
        #  '10' = 5 uV     5 pA
        #  '11' = 10 uV    10 pA
        #  '12' = 20 uV    20 pA
        #  '13' = 50 uV    50 pA
        #  '14' = 100 uV   100 pA
        #  '15' = 200 uV   200 pA
        #  '16' = 500 uV   500 pA
        #  '17' = 1 mV     1 nA
        #  '18' = 2 mV     2 nA
        #  '19' = 5 mV     5 nA
        #  '20' = 10 mV    10 nA
        #  '21' = 20 mV    20 nA
        #  '22' = 50 mV    50 nA
        #  '23' = 100 mV   100 nA
        #  '24' = 200 mV   200 nA
        #  '25' = 500 mV   500 nA
        #  '26' = 1 V      1 uA
        sen_i = self.query_int('SENS?')
        vSen = [2E-15, 5E-15, 10E-15, 20E-15,
                50E-15, 100E-15, 200E-15, 500E-15,
                1E-12, 2E-12, 5E-12, 10E-12, 20E-12,
                50E-12, 100E-12, 200E-12, 500E-12,
                1E-9, 2E-9, 5E-9, 10E-9, 20E-9,
                50E-9, 100E-9, 200E-9, 500E-9,
                1E-6][sen_i]
        inputMode = self.query('ISRC?')
        if inputMode in ['0', '1']:
            # Voltage mode
            vSen *= 1.0E6
        return vSen

    @SEN.setter
    def SEN(self, vSen):
        vSen = _np.abs(vSen)
        if self.query('ISRC?') in ['0', '1']:
            # Voltage mode
            vSen *= 1.0E-6
        bins = [2E-15, 5E-15, 10E-15, 20E-15,
                50E-15, 100E-15, 200E-15, 500E-15,
                1E-12, 2E-12, 5E-12, 10E-12, 20E-12,
                50E-12, 100E-12, 200E-12, 500E-12,
                1E-9, 2E-9, 5E-9, 10E-9, 20E-9,
                50E-9, 100E-9, 200E-9, 500E-9,
                1E-6]
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

    def InputMode(self, imode):
        '''
        Current/Voltage mode Input Selector
        Usage :
            InputMode(Code)
                Codes :
                 '0' = Voltage Mode A
                 '1' = Voltage Mode A-B
                 '2' = Current Mode 1 Mega Ohm
                 '3' = Current Mode 100 Mega Ohm
        '''
        if imode in ['0', '1', '2', '3']:
            self.write('ISRC %s' % imode)
        else:
            self._log('ERR ', 'Wrong Input Mode Code')

    def Sync(self, Sy=True):
        '''Enable or disable Synchonous time constant'''
        if Sy:
            self.write('SYNC 1')
        else:
            self.write('SYNC 0')

    def setOscilatorFreq(self, freq):
        '''Set the internal Oscilator Frequency'''
        self.write('FREQ %0.6f' % freq)

    def setOscilatorAmp(self, amp):
        '''Set the internal Oscilator Amplitude'''
        self.write('SLVL %0.6f' % amp)

    def setRefPhase(self, ph):
        '''Set the phase reference'''
        self.write('PHAS %0.6f' % ph)

    def getRefPhase(self):
        '''Get the programed phase reference'''
        return self.query_float('PHAS?')

    def ConfigureInput(self,
                       InDev='FET', Coupling='AC',
                       Ground='GND', AcGain='Auto'):
        # TODO Implement
        pass

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
        return self.query_float('FREQ?')

    @property
    def AUX_In_1(self):
        return self.query_float('OAUX?1')

    @property
    def AUX_In_2(self):
        return self.query_float('OAUX?2')

    @property
    def AUX_In_3(self):
        return self.query_float('OAUX?3')

    @property
    def AUX_In_4(self):
        return self.query_float('OAUX?4')

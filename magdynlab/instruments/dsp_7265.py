# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# DSP Lock-In Amplifier
# EG&G Instruments : 7265
# Should work with Signal Recovery 7265 DSP Lock-In
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['DSP_7265']


class DSP_7265(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=12, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'Lock In DSP 7265'
        self.VI.write_termination = self.VI.CR + self.VI.LF
        self.VI.read_termination = self.VI.CR + self.VI.LF

    def RemoteOnly(self, rO=True):
        if rO:
            self.write('REMOTE 1')
        else:
            self.write('REMOTE 0')

    @property
    def TC(self):
        '''
        Sets or return the Filter Time Constant
        setted values are rounded to aviable hardware value.
        '''
        # #Documentation#
        # TC Codes :
        # '0'  = 10 us
        # '1'  = 20 us
        # '2'  = 40 us
        # '3'  = 80 us
        # '4'  = 160 us
        # '5'  = 320 us
        # '6'  = 640 us
        # '7'  = 5 ms
        # '8'  = 10 ms
        # '9'  = 20 ms
        # '10' = 50 ms
        # '11' = 100 ms
        # '12' = 200 ms
        # '13' = 500 ms
        # '14' = 1 s
        # '15' = 2 s
        # '16' = 5 s
        # '17' = 10 s
        # '18' = 20 s
        # '19' = 50 s
        # '20' = 100 s
        # '21' = 200 s
        # '22' = 500 s
        # '23' = 1 ks
        # '24' = 2 ks
        # '25' = 5 ks
        # '26' = 10 ks
        # '27' = 20 ks
        # '28' = 50 ks
        # '29' = 100 ks
        # '30' = 200 ks
        return self.query_float('TC.')

    @TC.setter
    def TC(self, tc):
        tc = _np.abs(tc)
        bins = [10E-6, 20E-6, 40E-6, 80E-6,
                160E-6, 320E-6, 640E-6,
                5E-3, 10E-3, 20E-3, 50E-3,
                100E-3, 200E-3, 500E-3,
                1, 2, 5, 10, 20, 50,
                100, 200, 500,
                1E3, 2E3, 5E3, 10E3, 20E3, 50E3,
                100E3, 200E3]
        tc_i = _np.abs(_np.array(bins) - tc).argmin()
        self.write('TC %d' % tc_i)

    @property
    def SEN(self):
        '''
        Sets or return the Full Scale Sensitivity
        setted values rounded to aviable hardware value.
        '''
        # #Documentation#
        # SEN  Codes :
        # Code : IMODE=0 IMODE=1 IMODE=2
        # '1'  = 2 nV    2 fA    n/a
        # '2'  = 5 nV    5 fA    n/a
        # '3'  = 10 nV   10 fA   n/a
        # '4'  = 20 nV   20 fA   n/a
        # '5'  = 50 nV   50 fA   n/a
        # '6'  = 100 nV  100 fA  n/a
        # '7'  = 200 nV  200 fA  2 fA
        # '8'  = 500 nV  500 fA  5 fA
        # '9'  = 1 uV    1 pA    10 fA
        # '10' = 2 uV    2 pA    20 fA
        # '11' = 5 uV    5 pA    50 fA
        # '12' = 10 uV   10 pA   100 fA
        # '13' = 20 uV   20 pA   200 fA
        # '14' = 50 uV   50 pA   500 fA
        # '15' = 100 uV  100 pA  1 pA
        # '16' = 200 uV  200 pA  2 pA
        # '17' = 500 uV  500 pA  5 pA
        # '18' = 1 mV    1 nA    10 pA
        # '19' = 2 mV    2 nA    20 pA
        # '20' = 5 mV    5 nA    50 pA
        # '21' = 10 mV   10 nA   100 pA
        # '22' = 20 mV   20 nA   200 pA
        # '23' = 50 mV   50 nA   500 pA
        # '24' = 100 mV  100 nA  1 nA
        # '25' = 200 mV  200 nA  2 nA
        # '26' = 500 mV  500 nA  5 nA
        # '27' = 1V      1 uA    10 nA
        return self.query_float('SEN.')

    @SEN.setter
    def SEN(self, vSen):
        vSen = _np.abs(vSen)
        iMode = self.query('IMODE')
        if iMode == '0':
            vSen *= 1.0E-6
        bins = [0, 2E-15, 5E-15, 10E-15, 20E-15,
                50E-15, 100E-15, 200E-15, 500E-15,
                1E-12, 2E-12, 5E-12, 10E-12, 20E-12,
                50E-12, 100E-12, 200E-12, 500E-12,
                1E-9, 2E-9, 5E-9, 10E-9, 20E-9,
                50E-9, 100E-9, 200E-9, 500E-9,
                1E-6]
        sen_i = _np.abs(_np.array(bins) - vSen).argmin()
        if iMode == '2':
            sen_i += 6
            sen_i = _np.clip(sen_i, 7, 27)
        self.write('SEN %d' % sen_i)

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
            self.write('SLOPE %s' % sl)
        else:
            self._log('ERR ', 'Wrong Slope Code')

    def InputMode(self, imode):
        '''
        Current/Voltage mode Input Selector
        Usage :
            InputMode(Code)
                Codes :
                 '0' = Voltage Mode
                 '1' = Current Mode High bandwidth
                 '2' = Current Mode Low noise
        '''
        if imode in ['0', '1', '2']:
            self.write('IMODE %s' % imode)
        else:
            self._log('ERR ', 'Wrong Input Mode Code')

    def VoltageInputMode(self, vmode):
        '''
        #Voltage Input Configuration
        Usage :
            VoltageInputMode(Code)
                Codes :
                 '0' = Grounded
                 '1' = A Input only
                 '2' = -B Input only
                 '3' = A-B diferential mode
        '''
        if vmode in ['0', '1', '2', '3']:
            self.write('VMODE %s' % vmode)
        else:
            self._log('ERR ', 'Wrong Voltage Configuration Code')

    def Sync(self, Sy=True):
        '''Enable or disable Synchonous time constant'''
        if Sy:
            self.write('SYNC 1')
        else:
            self.write('SYNC 0')

    def ConfigureInput(self,
                       InDev='FET', Coupling='AC',
                       Ground='GND', AcGain='Auto'):
        '''
        Configure the input chanel
        '''
        if InDev == 'FET':
            self.VI.write('FET 1')
        elif InDev == 'Bipolar':
            self.VI.write('FET 0')
        else:
            self._log('ERR ', 'Wrong Input device control Code')

        if Coupling == 'DC':
            self.VI.write('CP 1')
        elif Coupling == 'AC':
            self.VI.write('CP 0')
        else:
            self._log('ERR ', 'Wrong Input Coupling Code')

        if Ground == 'GND':
            self.VI.write('FLOAT 0')
        elif Ground == 'Float':
            self.VI.write('FLOAT 1')
        else:
            self._log('ERR ', 'Wrong Input Coupling Code')

        if AcGain == 'Auto':
            self.VI.write('AUTOMATIC 1')
        elif AcGain in map(str, range(10)):
            self.VI.write('AUTOMATIC 0')
            self.VI.write('ACGAIN ' + AcGain)
        else:
            self._log('ERR ', 'Wrong AcGain Code')

    def setOscilatorFreq(self, freq):
        '''Set the internal Oscilator Frequency'''
        self.write('OF %d' % freq*1000)

    def setOscilatorAmp(self, amp):
        '''Set the internal Oscilator Amplitude'''
        self.write('OA %d' % amp*1E6)

    def setRefPhase(self, ph):
        '''Set the phase reference'''
        self.write('REFP %d' % ph*1E3)

    def getRefPhase(self):
        '''Get the programed phase reference'''
        return self.query_float('REFP.')

    @property
    def X(self):
        return self.query_float('X.')

    @property
    def Y(self):
        return self.query_float('Y.')

    @property
    def Magnitude(self):
        return self.query_float('MAG.')

    @property
    def Phase(self):
        return self.query_float('PHA.')

    @property
    def Freq(self):
        return self.query_float('FRQ.')

# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Radio Frequency Amplifier model 60/20S1G18A
# by Amplifier Research
#
# TODO:
# Make documentation

import numpy as _np
from .instruments_base import InstrumentBase as _InstrumentBase
from .instruments_base import findResource

__all__ = ['AR_RF_Amplifier']


class AR_RF_Amplifier(_InstrumentBase):
    def __init__(self, ResourceName, logFile=None):
        super().__init__(ResourceName, logFile)
        self._IDN = 'RF Amplifier'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.write('R')

    @property
    def ID(self):
        '''ID'''
        return self.query('*IDN?')

    def Output(self, out):
        '''
        Enable or disable power supply output

        Usage :
            Output('ON'/'OFF')
        '''
        if out in ['ON', 'OFF']:
            state = {'ON':1, 'OFF':0}[out]
            self.write('P%d' %state)
        else:
            self._log('ERR ', 'Output error code')

    @property
    def gain(self):
        '''
        Gain level (in %)
        '''
        gain_bin = int(self.query('G?').strip('G'))
        return gain_bin/4095*100

    @gain.setter
    def gain(self, vGain):
        gain_bin = round(vGain/100*4095)
        self.write('G%d' %gain_bin)
        
    def Band(self, band):
        '''
        Select the high or low band amplifier

        Usage :
            Band('HIGH'/'LOW')
        '''
        if band in ['HIGH', 'LOW']:
            self.write('BAND%s' %band[0])
        else:
            self._log('ERR ', 'Band error code')

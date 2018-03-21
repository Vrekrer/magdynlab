# -*- coding: utf-8 -*-

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# USB Acquisition Board
# Measurement Computing : USB 1602HS 2AO
#
# TODO:
# Make documentation


import numpy as _np
import os
if os.name == 'nt':
    try:
        from mcculw import ul
        from mcculw.enums import ULRange, TrigType, ScanOptions
        __all__ = ['USB_1602HS']
    except:
        print('ERROR USB 1602HS 2AO, UniversalLibrary not found')
        __all__ = []
else:
    __all__ = []


class Channel(object):
    def __init__(self, parent, num):
        self.parent = parent
        self.num = num
        self._range = '\xb1 10V'
        self._ULrange = ULRange.BIP10VOLTS
        self._rangeVpp = 20
        self.enabled = True
    @property
    def info(self):
        print( 'Ch %d' % self.num)
        print( ' Range : %s' % self._range)
        print( ' Enabled : %s' % self.enabled)
    @property
    def range(self):
        return self._range
    @range.setter
    def range(self, value):
        if value in ['BIP2PT5VOLTS', 2.5, '2.5V', '\xb1 2.5V']:
            self._range = '\xb1 2.5V'
            self._ULrange = ULRange.BIP2PT5VOLTS
            self._rangeVpp = 5
        elif value in ['BIPPT5VOLTS', 0.5, '0.5V', '\xb1 0.5V']:
            self._range = '\xb1 0.5V'
            self._ULrange = ULRange.BIPPT5VOLTS
            self._rangeVpp = 1
        else:
            self._range = '\xb1 10V'
            self._ULrange = ULRange.BIP10VOLTS
            self._rangeVpp = 20

class Trigger(object):
    digitalTriggers = ['TRIG_HIGH', 'TRIG_LOW', 
                       'TRIG_POS_EDGE', 'TRIG_NEG_EDGE']
    analogTriggers = ['TRIG_ABOVE', 'TRIG_BELOW']
    def __init__(self, parent):
        self.parent = parent
        self._trigType = None
        self._lowThreshold = 0
        self._highThreshold = 0
        self._analogChannel = 0
        self.enabled = False
    def disable_Trigger(self):
        self.enabled = False
        self._trigType = None
    def set_Digital_Trigger(self, trigType):
        if trigType in self.digitalTriggers:
            self._trigType = trigType
            self.enabled = True
            ul.set_trigger(self.parent.boardNum, 
                           TrigType.__members__[self._trigType], 0,0)
        else:
            print('Invalid Digital Trigger \n Trigger disabled')
            self.disable_Trigger()
    def set_Analog_Trigger(self, trigType, lowThreshold = 0, 
                           highThreshold = 0, channel = 0):
        if trigType in self.analogTriggers:
            self._trigType = trigType
            self.enabled = True
            self._analogChannel = channel
            self._lowThreshold = ul.from_eng_units(self.parent.boardNum,
                                                   self.parent.Channels[channel]._ULrange,
                                                   lowThreshold)
            self._highThreshold = ul.from_eng_units(self.parent.boardNum,
                                                    self.parent.Channels[channel]._ULrange,
                                                    highThreshold)
            ul.set_trigger(self.parent.boardNum, 
                            TrigType.__members__[self._trigType],
                            self._lowThreshold,
                            self._highThreshold)
        else:
            print('Invalid Digital Trigger \n Trigger disabled')
            self.disable_Trigger()

class USB_1602HS(object):
    def __init__(self, boardNum = 0):
        self._boardNum = boardNum
        self.Ch0 = Channel(self, 0)
        self.Ch1 = Channel(self, 1)
        self.Channels = [self.Ch0, self.Ch1]
        self.Trigger = Trigger(self)
        self._nSamples = 100
        self._rate = int(2E6)
        self._adqTime = self._nSamples * 1.0/self._rate
        self.maxTime = 60
        self.Lib = ul

    @property
    def rate(self):
        return self._rate
    @rate.setter
    def rate(self, newRate):
        newRate = _np.clip(newRate, 1, 2E6)
        self._rate = int(newRate)
        self.adqTime = self._nSamples * 1.0/self._rate
        
    @property
    def nSamples(self):
        return self._nSamples
    @nSamples.setter
    def nSamples(self, vN):
        self._nSamples = int(vN)
        self.adqTime = self._nSamples * 1.0/self._rate

    @property
    def adqTime(self):
        return self._adqTime
    @adqTime.setter
    def adqTime(self, newTime):
        newTime = _np.clip(newTime, 0, self.maxTime)
        self._adqTime = newTime
        self._nSamples = int(self._adqTime * self.rate)
        
    def Adquire(self):
        enabledChannels = _np.array([ch.num for ch in self.Channels if ch.enabled], dtype = _np.int16)
        UL_gains = _np.array([ch._ULrange for ch in self.Channels if ch.enabled], dtype = _np.int16)
        gains = _np.array([ch._rangeVpp for ch in self.Channels if ch.enabled], dtype = _np.int16)
        nChannels = len(enabledChannels)
        ul.a_load_queue(self.boardNum, enabledChannels, UL_gains, nChannels)
        
        dataSize = self.nSamples * nChannels
        rawData = _np.zeros(dataSize, dtype = _np.int16)
        if self.Trigger.enabled:
            opts = ScanOptions.BLOCKIO + ScanOptions.EXTTRIGGER
        else:
            opts = ScanOptions.BLOCKIO
        trueRate = ul.a_in_scan(self.boardNum, 0, 0, dataSize, self.rate, 0, rawData.ctypes.data, opts)
        voltsOut = _np.uint16(rawData).reshape((self.nSamples, nChannels)).T / 2.0**16 - 0.5
        voltsOut = voltsOut * gains[:,None]
        self.dT = 1.0/trueRate
        ts = _np.arange(self.nSamples)  * self.dT
        return _np.r_[ts[None,:], voltsOut]
        

    @property
    def boardNum(self):
        return self._boardNum


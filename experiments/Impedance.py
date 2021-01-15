# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments
import magdynlab.controllers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt



class ZA(object):
    def __init__(self):
        logFile = os.path.expanduser('~/MagDynLab.log')
        IA = magdynlab.instruments.KEYSIGHT_E4990A(ResourceName='TCPIP::192.168.13.3::INSTR', logFile=logFile)

        self.IAC = magdynlab.controllers.IA_Controller(IA)

        self.SaveFormat = 'npy'
        self.Info = ''
        self.PlotFunct = None

    def MeasureSpectra(self):
        self.fs = self.IAC.frequencies
        self.Z = self.IAC.getRData(new = True)

    def Save(self, file_name):
        self.MeasureSpectra()
        numpy.savez_compressed(file_name + '.Imp',
                               Z=self.Z,
                               f=self.IAC.frequencies,
                               Info=self.Info)

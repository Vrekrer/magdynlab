# -*- coding: utf-8 -*-

import numpy
import os
import magdynlab.instruments
import magdynlab.controllers
import magdynlab.data_types


class VNA(object):
    def __init__(self, GPIB_Device=0):
        logFile = os.path.expanduser('~/MagDynLab.log')
        VNA = magdynlab.instruments.RS_VNA_Z(
            ResourceName='TCPIP::192.168.13.2::INSTR',
            logFile=logFile
        )

        self.VNAC = magdynlab.controllers.VNA_Controler(VNA)

        self.traceNumbers = [0, 1, 2, 3]

        self.SaveFormat = 'npy'
        self.Info = ''

    def MeasureSpectra(self):
        Ss = []
        S = self.VNAC.getSData(self.traceNumbers[0], True)
        Ss.append(S)
        for tr in self.traceNumbers[1:]:
            S = self.VNAC.getSData(tr, False)
            Ss.append(S)
        self.S11 = Ss[0]
        self.S22 = Ss[1]
        self.S12 = Ss[2]
        self.S21 = Ss[3]
        return Ss

    def Save(self, file_name):
        self.Ss = numpy.array(self.MeasureSpectra())
        numpy.savez_compressed(file_name + '.VNA',
                               Ss=self.Ss,
                               f=self.VNAC.frequencies,
                               Info=self.Info)

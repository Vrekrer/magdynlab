# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments
import magdynlab.controllers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt


@ThD.gui_safe
def MyPlot(Data):
    f = plt.figure('VNA-FMR', (5, 4))

    extent = numpy.array([Data.x.min(),
                          Data.x.max(),
                          Data.y.min()/1E9,
                          Data.y.max()/1E9])

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    ax.clear()
    ax.imshow(Data.dataArray,
              aspect='auto',
              origin='lower',
              extent=extent)

    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Freq (GHz)')
    f.tight_layout()
    f.canvas.draw()


class VNA_FMR(object):
    def __init__(self):
        logFile = os.path.expanduser('~/MagDynLab.log')
        PowerSource = magdynlab.instruments.KEPCO_BOP(ResourceName='GPIB0::6::INSTR', logFile=logFile)
        VNA = magdynlab.instruments.RS_VNA_Z(ResourceName='TCPIP::192.168.13.2::INSTR', logFile=logFile)

        self.VNAC = magdynlab.controllers.VNA_Controler(VNA)
        self.FC = magdynlab.controllers.FieldControler(PowerSource)
        self.FC.Kepco.Voltage = 15

        # We store the raw wave quantities in this Collection
        self.DataCollection = []
        for i in range(3):
            D = magdynlab.data_types.Data3D()
            self.DataCollection.append(D)

        # This is used to plot
        self.DataPlot = magdynlab.data_types.Data3D()

        self.traceNumbers = [0, 1, 2]

        self.SaveFormat = 'npy'
        self.Info = ''

    def SetTraces(self):
        self.VNAC.set_traces_WaveQuantities()

    def _MeasureSpectra(self):
        Ss = []
        S = self.VNAC.getSData(self.traceNumbers[0], True)
        Ss.append(S)
        for tr in self.traceNumbers[1:]:
            S = self.VNAC.getSData(tr, False)
            Ss.append(S)
        return Ss

    def _SaveData(self, file_name):
        numpy.savez_compressed(file_name + '.VNA_P_Raw',
                               a1=numpy.nan_to_num(self.DataCollection[0].dataArray),
                               b1=numpy.nan_to_num(self.DataCollection[1].dataArray),
                               b2=numpy.nan_to_num(self.DataCollection[2].dataArray),
                               Ref=self.Refs,
                               h=self.DataCollection[0].x,
                               f=self.DataCollection[0].y,
                               Info=self.Info)

    def SaveRef(self, file_name):
        self.Refs = numpy.array(self._MeasureSpectra())
        numpy.savez_compressed(file_name + '.VNA_P_Ref',
                               Ref=self.Refs,
                               f=self.VNAC.frequencies,
                               Info=self.Info)

    def PlotData(self, i=None):
        Ref_Pa1 = numpy.abs(self.Refs[0])**2/50
        Ref_Pb1 = numpy.abs(self.Refs[1])**2/50
        Ref_Pb2 = numpy.abs(self.Refs[2])**2/50

        Ppr = (Ref_Pa1 - Ref_Pb1 - Ref_Pb2) / (Ref_Pa1 - Ref_Pb1)

        # Update only last column
        if i is not None:
            LastPa1 = numpy.abs(self.DataCollection[0].dataArray[:, i])**2/50
            LastPb1 = numpy.abs(self.DataCollection[1].dataArray[:, i])**2/50
            LastPb2 = numpy.abs(self.DataCollection[2].dataArray[:, i])**2/50

            Pim = LastPa1 - LastPb1
            Ppm = (Pim - LastPb2 - Ppr*Pim)/Pim
            self.DataPlot.addColumn(Ppm)
        else:
            LastPa1 = numpy.abs(self.DataCollection[0].dataArray)**2/50
            LastPb1 = numpy.abs(self.DataCollection[1].dataArray)**2/50
            LastPb2 = numpy.abs(self.DataCollection[2].dataArray)**2/50

            Pim = LastPa1 - LastPb1
            Ppm = (Pim - LastPb2 - Ppr[:, None]*Pim)/Pim

            self.DataPlot.dataArray = Ppm
        MyPlot(self.DataPlot)

    @ThD.as_thread
    def Measure(self, crv, file_name, hold_time = 0.0):
        fields = crv
        freqs = self.VNAC.frequencies

        # Initialize data objects
        for D in self.DataCollection:
            D.initialize(fields, freqs, dtype=complex)
        self.DataPlot.initialize(fields, freqs)

        # Loop for each field
        for i, h in enumerate(fields):

            self.FC.setField(h)
            time.sleep(hold_time)
            Ss = self._MeasureSpectra()
            for j, S in enumerate(Ss):
                self.DataCollection[j].addColumn(S)
            self.PlotData(i)
            ThD.check_stop()

        if file_name is not None:
            self._SaveData(file_name)
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    def Stop(self, TurnOff=True):
        print('Stoping...')
        self.FC.BEEP()
        self.Measure.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        print('DONE')
        if TurnOff:
            print('Turning field OFF')
            self.FC.TurnOff()
            print('DONE')

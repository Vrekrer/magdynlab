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
    f = plt.figure('MI', (5, 4))

    extent = numpy.array([Data.x.min(),
                          Data.x.max(),
                          Data.y.min()/1E3,
                          Data.y.max()/1E3])

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    ax.clear()
    ax.imshow(Data.dataArray,
              aspect='auto',
              origin='lower',
              extent=extent)

    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Freq (kHz)')
    f.tight_layout()
    f.canvas.draw()


class MI(object):
    def __init__(self, GPIB_Device=0):
        logFile = os.path.expanduser('~/MagDynLab.log')
        PowerSource = magdynlab.instruments.KEPCO_BOP_blind(ResourceName='TCPIP0::192.168.13.3::KepcoBOP2020::INSTR', logFile=logFile)
        IA = magdynlab.instruments.KEYSIGHT_E4990A(ResourceName='TCPIP0::192.168.13.3::USB_E4990A::INSTR', logFile=logFile)

        self.IAC = magdynlab.controlers.IA_Controller(IA)
        self.FC = magdynlab.controlers.FieldController(PowerSource)
        self.FC.Kepco.Voltage = 15

        # We store the raw Z parameters here
        self.Z_Data = magdynlab.data_types.Data3D()

        # This is used to plot
        self.DataPlot = magdynlab.data_types.Data3D()

        self.SaveFormat = 'npy'
        self.Info = ''
        self.PlotFunct = None

    def _MeasureSpectra(self):
        return self.IAC.getRData(new = True)

    def _SaveData(self, file_name):
        numpy.savez_compressed(file_name + '.MI_Raw',
                               Z=numpy.nan_to_num(self.Z_Data.dataArray),
                               Ref=self.Ref,
                               h=self.Z_Data.x,
                               f=self.Z_Data.y,
                               Info=self.Info)

    def SaveRef(self, file_name):
        self.Ref = self._MeasureSpectra()
        numpy.savez_compressed(file_name + '.MI_Ref',
                               Ref=self.Ref,
                               f=self.IAC.frequencies,
                               Info=self.Info)

    def PlotData(self, i=None):
        Pr = numpy.abs(self.Ref)

        # Update only last column
        if i is not None:
            LastZ = self.Z_Data.dataArray[:, i]
            if self.PlotFunct is None:
                Pm = numpy.abs(LastZ)
                self.DataPlot.addColumn(Pm - Pr)
            else:
                self.DataPlot.addColumn(self.PlotFunct(LastZ, Pr))
        else:
            Z = self.Z_Data.dataArray
            if self.PlotFunct is None:
                Pm = numpy.abs(Z)
                self.DataPlot.dataArray = Pm-Pr[:, None]
            else:
                self.DataPlot.dataArray = self.PlotFunct(Z, Pr[:, None])
        MyPlot(self.DataPlot)

    @ThD.as_thread
    def Measure(self, crv, file_name):
        fields = crv
        freqs = self.IAC.frequencies

        # Initialize data objects
        self.Z_Data.initialize(fields, freqs, dtype=complex)
        self.DataPlot.initialize(fields, freqs)

        # Loop for each field
        for i, h in enumerate(fields):

            self.FC.setField(h)#, Tol=0.25, FldStep=0.5)
            # time.sleep(0.5)
            S = self._MeasureSpectra()
            self.Z_Data.addColumn(S)
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

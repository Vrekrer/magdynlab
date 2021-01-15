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
def Plot_ColorMap(Data):
    f = plt.figure('ZxBias', (5, 4))

    extent = numpy.array([Data['bias'].min(),
                          Data['bias'].max(),
                          Data['f'].min()/1E3,
                          Data['f'].max()/1E3])

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    ax.clear()
    ax.imshow(Data['ColorMap'].T,
              aspect='auto',
              origin='lower',
              extent=extent)

    ax.set_xlabel('Bias Voltage (V)')
    ax.set_ylabel('Freq (kHz)')
    f.tight_layout()
    f.canvas.draw()

class ZxBias(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Kepco = 'TCPIP0::192.168.13.7::KepcoBOP2020::INSTR',
                         RN_IA = 'TCPIP::192.168.13.3::INSTR')
        defaultRN.update(ResouceNames)
        RN_IA = defaultRN['RN_IA']
        
        self.IA = magdynlab.instruments.KEYSIGHT_E4990A(ResourceName=RN_IA,
                                                   logFile=logFile)

        self.IAC = magdynlab.controllers.IA_Controller(self.IA)

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.ZxBias_Raw' #Z vs Bias vs fs

        self.ColorMapData = magdynlab.data_types.DataContainer()
        self.ColorMapData.file_id = '.ZxH_ColorMap' #|Z| vs hs vs fs

        self.SaveFormat = 'npy'
        self.Info = ''
        self.PlotFunct = numpy.abs

    def PlotColorMap(self, i=None):
        Z_ref = self.PlotFunct(self.Data['Ref'])
        if i is not None:
            # Update up to i column
            for j in range(i+1):
                Z = self.PlotFunct(self.Data['Z'][j])
                if self.Data['bias'][0] > self.Data['bias'][-1]:
                    j = -1 - j
                self.ColorMapData['ColorMap'][j] = Z - Z_ref
        else:
            Z = self.PlotFunct(self.Data['Z'])
            self.ColorMapData['ColorMap'] = Z - Z_ref[None,:]
            if self.Data['bias'][0] > self.Data['bias'][-1]:
                self.ColorMapData['ColorMap'] = Z[::-1]
        Plot_ColorMap(self.ColorMapData)

    def MeasureRef(self):
        self.Data['Ref'] = self.IAC.getRData(True)

    @ThD.as_thread
    def Measure(self, bias_volts, file_name, hold_time=0.01):

        self.Data['bias'] = bias_volts
        self.Data['f'] = self.IAC.frequencies
        data_shape = (len(self.Data['bias']), len(self.Data['f']))
        self.Data['Z'] = numpy.zeros(data_shape, dtype=complex)
        self.Data.info = self.Info
        
        self.ColorMapData['bias'] = self.Data['bias']
        self.ColorMapData['f'] = self.Data['f']
        self.ColorMapData['ColorMap'] = numpy.zeros(data_shape, dtype=float)
        self.ColorMapData['ColorMap'] += numpy.nan
        self.ColorMapData.info = self.Info
        
        # Loop for each field
        for i, v in enumerate(bias_volts):
            self.IA.Ch1.bias_voltage = v
            time.sleep(hold_time)
            self.Data['Z'][i] = self.IAC.getRData(True)
            self.PlotColorMap(i)
            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)

    def Stop(self):
        print('Stoping...')
        self.Measure.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        print('DONE')


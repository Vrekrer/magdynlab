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
    f = plt.figure('ZxH', (5, 4))

    extent = numpy.array([Data['h'].min(),
                          Data['h'].max(),
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

    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Freq (kHz)')
    f.tight_layout()
    f.canvas.draw()

@ThD.gui_safe
def Plot_ColorMapTime(Data):
    f = plt.figure('Zxt', (5, 4))

    extent = numpy.array([Data['t'].min(),
                          Data['t'].max(),
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

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Freq (kHz)')
    f.tight_layout()
    f.canvas.draw()

@ThD.gui_safe
def Plot_ResFreq(Data):
    f = plt.figure('ResFreq', (5, 4))

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]

    ymax = numpy.nanmax(Data['ResFreq'])/1E3
    ymin = numpy.nanmin(Data['ResFreq'])/1E3
    dy  = numpy.max([ymax - ymin, 1E-6])

    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim([Data['t'].min(), Data['t'].max()])
        ax.set_ylim([ymax+dy, ymin-dy])
        
    line = ax.lines[-1]
    line.set_data(Data['t'], Data['ResFreq']/1E3)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('ResFreq (kHz)')
    ax.grid(True)

    #check Y scale
    yc = (ymax + ymin)/2
    ymin, ymax = ax.get_ylim()
    ymax = numpy.max([yc + dy*1.1/2, ymax])
    ymin = numpy.min([yc - dy*1.1/2, ymin])
    ax.set_ylim([ymin, ymax])

    f.tight_layout()
    f.canvas.draw()


class ZxH(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Kepco = 'TCPIP0::192.168.13.7::KepcoBOP2020::INSTR',
                         RN_IA = 'TCPIP::192.168.13.3::INSTR')
        defaultRN.update(ResouceNames)
        RN_Kepco = defaultRN['RN_Kepco']
        RN_IA = defaultRN['RN_IA']
        
        PowerSource = magdynlab.instruments.KEPCO_BOP(ResourceName=RN_Kepco,
                                                      logFile=logFile)
        IA = magdynlab.instruments.KEYSIGHT_E4990A(ResourceName=RN_IA,
                                                   logFile=logFile)

        self.IAC = magdynlab.controllers.IA_Controller(IA)
        self.FC = magdynlab.controllers.FieldController(PowerSource)
        self.FC.Kepco.Voltage = 5

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.ZxH_Raw' #Z vs hs vs fs

        self.DataTime = magdynlab.data_types.DataContainer()
        self.DataTime.file_id = '.Zxt_Raw' #Z vs ts vs fs

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
                if self.Data['h'][0] > self.Data['h'][-1]:
                    j = -1 - j
                self.ColorMapData['ColorMap'][j] = Z - Z_ref
        else:
            Z = self.PlotFunct(self.Data['Z'])
            self.ColorMapData['ColorMap'] = Z - Z_ref[None,:]
            if self.Data['h'][0] > self.Data['h'][-1]:
                self.ColorMapData['ColorMap'] = Z[::-1]
        Plot_ColorMap(self.ColorMapData)

    def PlotColorMapTime(self, i=None):
        Z_ref = self.PlotFunct(self.Data['Ref'])
        if i is not None:
            # Update up to i column
            for j in range(i+1):
                Z = self.PlotFunct(self.DataTime['Z'][j])
                self.ColorMapData['ColorMap'][j] = Z - Z_ref
        else:
            Z = self.PlotFunct(self.DataTime['Z'])
            self.ColorMapData['ColorMap'] = Z - Z_ref[None,:]

        dt = self.DataTime['t'][1] - self.DataTime['t'][0]
        if dt < 0:
            dt = 1

        self.ColorMapData['t'] = numpy.arange(0, len(self.DataTime['t'])) * dt
        Plot_ColorMapTime(self.ColorMapData)

        if i is not None:
            # Update up to i column
            for j in range(i+1):
                posPeak = self.ColorMapData['ColorMap'][j].argmax()
                self.ColorMapData['ResFreq'][j] = self.DataTime['f'][posPeak]
        if i >= 1:
            Plot_ResFreq(self.ColorMapData)

    def MeasureRef(self):
        self.Data['Ref'] = self.IAC.getRData(True)

    @ThD.as_thread
    def Measure(self, fields, file_name, hold_time=0.0):

        self.Data['h'] = fields
        self.Data['f'] = self.IAC.frequencies
        data_shape = (len(self.Data['h']), len(self.Data['f']))
        self.Data['Z'] = numpy.zeros(data_shape, dtype=complex)
        self.Data.info = self.Info
        
        self.ColorMapData['h'] = self.Data['h']
        self.ColorMapData['f'] = self.Data['f']
        self.ColorMapData['ColorMap'] = numpy.zeros(data_shape, dtype=float)
        self.ColorMapData['ColorMap'] += numpy.nan
        self.ColorMapData.info = self.Info
        
        # Loop for each field
        for i, h in enumerate(fields):
            self.FC.setField(h)
            time.sleep(hold_time)
            self.Data['Z'][i] = self.IAC.getRData(True)
            self.PlotColorMap(i)
            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    @ThD.as_thread
    def MeasureVsTime(self, field, time_step, n_steps, file_name):

        self.DataTime['t'] = numpy.zeros((n_steps))
        self.DataTime['f'] = self.IAC.frequencies
        data_shape = (len(self.DataTime['t']), len(self.DataTime['f']))
        self.DataTime['Z'] = numpy.zeros(data_shape, dtype=complex)
        
        self.ColorMapData['t'] = numpy.arange(0, n_steps)
        self.ColorMapData['ResFreq'] = numpy.arange(0, n_steps) + numpy.nan
        self.ColorMapData['f'] = self.DataTime['f']
        self.ColorMapData['ColorMap'] = numpy.zeros(data_shape, dtype=float)
        self.ColorMapData['ColorMap'] += numpy.nan
        self.ColorMapData.info = self.Info

        self.FC.setField(field)

        # Loop for each field
        for i in range(n_steps):
            time.sleep(time_step)
            self.DataTime['t'][i] = time.time()
            self.DataTime['Z'][i] = self.IAC.getRData(True)
            self.PlotColorMapTime(i)
            ThD.check_stop()

        self.DataTime.info = self.Info
        if file_name is not None:
            self.DataTime.save(file_name)

    def Stop(self, TurnOff=True):
        print('Stoping...')
        self.FC.BEEP()
        if self.Measure.thread is not None:
            self.Measure.stop()
            self.Measure.thread.join()
        if self.MeasureVsTime.thread is not None:
            self.MeasureVsTime.stop()
            self.MeasureVsTime.thread.join()
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        print('DONE')
        if TurnOff:
            print('Turning field OFF')
            self.FC.TurnOff()
            print('DONE')


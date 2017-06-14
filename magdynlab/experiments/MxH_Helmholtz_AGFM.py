# -*- coding: utf-8 -*-

#MxH_Helmholtz_AGFM

import numpy
import time
import magdynlab.instruments
import magdynlab.controlers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt

@ThD.gui_safe
def MyPlot(Data):
    f = plt.figure('AGFM MxH', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*Data.ylim)
    line = ax.lines[-1]
    line.set_data(Data.X, Data.Y)
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('m')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()
    f.savefig('MxH.png')

@ThD.gui_safe
def FreqPlot(Data):
    f = plt.figure('AGFM Amp vs Freq', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*Data.ylim)
    line = ax.lines[-1]
    line.set_data(Data.X, Data.Y)
    ax.set_xlabel('Freq')
    ax.set_ylabel('Amp')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()
    f.savefig('MxF.png')
    
class MxH(object):
    def __init__(self):
        PowerSource = magdynlab.instruments.KEPCO_BOP_blind(GPIB_Address=7)
        LockIn = magdynlab.instruments.SRS_SR830()

        self.FC = magdynlab.controlers.FieldControler(PowerSource)
        self.VC = magdynlab.controlers.LockIn_Mag_Controler(LockIn)

        #This is used to plot
        self.Data = magdynlab.data_types.Data2D()
        self.DataFreq = magdynlab.data_types.Data2D()
        
    def _SaveData(self, file_name):
        self.Data.save(file_name)

    def PlotData(self, i = None):
        MyPlot(self.Data)

    def PlotFreq(self):
        FreqPlot(self.DataFreq)

    @ThD.as_thread
    def FreqCurve(self, crvf = [], file_name = None, TurnOff = False):
        freqs = numpy.asarray(crvf)

        #Initialize data objects
        self.DataFreq.reset()
        self.DataFreq.xlim = [freqs.min(), freqs.max()]
        sen = self.VC.LockIn.SEN * 1.5 * self.VC.emu_per_V
        self.DataFreq.ylim = [0, sen]
        
        #Loop for each field
        for i, f in enumerate(freqs):
            self.VC.LockIn.setOscilatorFreq(f)
            #time.sleep(0.5)
            a = self.VC.getAmplitude() 
            if a >= 0.9 * self.VC.LockIn.SEN:
                self.VC.LockIn.SEN = 3*self.VC.LockIn.SEN
                a = self.VC.getAmplitude() 
            self.DataFreq.addPoint(f, a*self.VC.emu_per_V)
            FreqPlot(self.DataFreq)
            ThD.check_stop()
            
        if file_name is not None:
            self._SaveData(file_name)
        if TurnOff:
            self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    @ThD.as_thread
    def Measure(self, crv = [], file_name = None, meas_opts = [10, 1, 0.1]):
        fields = numpy.asarray(crv)
        
        # Initialize data objects
        self.Data.reset()
        self.Data.xlim = [fields.min(), fields.max()]
        sen = self.VC.LockIn.SEN * 1.5 * self.VC.emu_per_V
        self.Data.ylim = [-sen, sen]
        
        n_pts, iniDelay, measDelay = meas_opts
        
        # Loop for each field
        for i, h in enumerate(fields):
            self.FC.setField(h)
            while abs(h - self.FC.getField()) > 50:
                self.FC.setField(h)
            #time.sleep(0.5)
            m, sm = self.VC.getMagnetization(n = n_pts, iniDelay = iniDelay, measDelay = measDelay)
            self.Data.addPoint(h, m)
            MyPlot(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self._SaveData(file_name)
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    def Stop(self, TurnOff = True):
        print('Stoping...')
        self.FC.BEEP()
        self.Measure.stop()
        self.FreqCurve.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        if self.FreqCurve.thread is not None:
            self.FreqCurve.thread.join()
        print('DONE')
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        if TurnOff:
            print('Turning field OFF')
            self.FC.setField(0)
            print('DONE')


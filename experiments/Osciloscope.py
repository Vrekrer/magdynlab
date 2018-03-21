# -*- coding: utf-8 -*-

#MxH_Helmholtz_AGFM

import numpy
import time
import magdynlab.instruments
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt

@ThD.gui_safe
def MyPlot(t, ch0, ch1, g0=1, g1=1):
    f = plt.figure('Osc', (5,4))
    
    ymax = max([ch0.max(), ch1.max()])
    ymin = min([ch0.min(), ch1.min()])
    rr = (ymax-ymin)
    ymax += rr*0.05
    ymin -= rr*0.05
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b-')
        ax.plot([],[],'r-')
        ax.set_xlim(t.min(), t.max())
        ax.set_ylim(ymin, ymax)
    ax.lines[0].set_data(t, ch0*g0)
    ax.lines[1].set_data(t, ch1*g1)

    ax.set_xlabel('time (s)')
    ax.set_ylabel('Vmed (V)')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()
    
class Osc(object):
    def __init__(self):
        self.conf = magdynlab.instruments.USB_1602HS()
        self.conf.Trigger.set_Digital_Trigger('TRIG_POS_EDGE')
        #self.Data = magdynlab.data_types.Data2D()
        #self.Data.reset(n=3)
        self._stop = False
        self._run_delay = 0.1
        self.g0 = 1
        self.g1 = 1
        
    def _SaveData(self, file_name):
        self.Data.save(file_name)

    def PlotData(self, i = None):
        MyPlot(self.Data)

    @ThD.as_thread
    def Run(self):
        self._stop = False
        while not(self._stop):
            t, ch0, ch1 = self.conf.Adquire()
            MyPlot(t, ch0, ch1, self.g0, self.g1)
            time.sleep(self._run_delay)

    def Stop(self):
        self._stop = True
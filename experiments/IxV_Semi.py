# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments
import magdynlab.controllers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt

def Plot_IxV(Data):
    f = plt.figure('IxV Semi', (5, 4))

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]

    #check Y scale
    ymax = numpy.nanmax(Data['V'])
    ymin = numpy.nanmin(Data['V'])
    dy  = numpy.max([ymax - ymin, 1E-6])

    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim([Data['I'].min(), Data['I'].max()])
        ax.set_ylim([ymax+dy, ymin-dy])
        
    line = ax.lines[-1]
    line.set_data(Data['I'], Data['V'])
    ax.set_xlabel('Current (A)')
    ax.set_ylabel('Voltage (V)')
    ax.grid(True)

    yc = (ymax + ymin)/2
    ymin, ymax = ax.get_ylim()
    ymax = numpy.max([yc + dy*1.1/2, ymax])
    ymin = numpy.min([yc - dy*1.1/2, ymin])
    ax.set_ylim([ymin, ymax])

    f.tight_layout()
    f.canvas.draw()

def resistance(Data):
    I = Data['I']
    V = Data['V']
    R = numpy.polyfit(I, V, 1)[0]
    return R


class IxV(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')

        defaultRN = dict(RN_SCA = 'TCPIP::192.168.13.7::5025::SOCKET')
        defaultRN.update(ResouceNames)
        RN_SCA = defaultRN['RN_SCA']

        self.SCA = magdynlab.instruments.KEYSIGHT_B1500A(ResourceName=RN_SCA,
                                             logFile=logFile)

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.IxV_Semi'
        self.Info = ''


    def Measure(self, file_name=None):
        self.Data.info = self.Info

        print('Measuring : %s' %file_name)
        # Get one measurement to get the data shape and dictionaries
        m_data = self.SCA.getResultDictionary(new=True, delete=True)
        for key in m_data.keys():
            self.Data[key] = m_data[key]

        if file_name is not None:
            self.Data.save(file_name)
            self.Data.savetxt(file_name + '.IxV', 
                              keys=[k for k in self.Data.keys()])
        print('DONE')
        print('Resistance : %0.3E Ohms' % resistance(self.Data))
        Plot_IxV(self.Data)

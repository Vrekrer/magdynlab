# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Signal generator + Spectrum analyzer experiment
#
# TODO:
# Make documentation

import time
import numpy
import os
import threading_decorators as ThD
import matplotlib.pyplot as plt
import magdynlab.instruments
import magdynlab.data_types

@ThD.gui_safe
def Plot_Pw_vs_f(Data):
    f = plt.figure('Frequency Spectrum', (5, 4))

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]

    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim([Data['f'].min()/1E9, Data['f'].max()/1E9])
        ax.set_ylim([-1E-10, 1E-10])
        
    line = ax.lines[-1]
    line.set_data(Data['f']/1E9, Data['power'])
    ax.set_xlabel('Frequency (GHz)')
    ax.set_ylabel('Power (dBm)')
    ax.grid(True)

    #check Y scale
    ymax = numpy.nan_to_num(Data['power']).max()
    ymin = numpy.nan_to_num(Data['power']).min()
    dy  = ymax - ymin
    yc = (ymax + ymin)/2
    ymin, ymax = ax.get_ylim()
    ymax = numpy.max([yc + dy*1.1/2, ymax])
    ymin = numpy.min([yc - dy*1.1/2, ymin])
    ax.set_ylim([ymin, ymax])

    f.tight_layout()
    f.canvas.draw()


class FSL_SMF(object):
    '''
    Signal generator + Spectrum analyzer controller
    '''

    def __init__(self, ResouceNames={}):
    
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_FSL = 'TCPIP::192.168.13.5::INSTR',
                         RN_SMF = 'TCPIP::192.168.13.4::INSTR')
        defaultRN.update(ResouceNames)
        RN_FSL = defaultRN['RN_FSL']
        RN_SMF = defaultRN['RN_SMF']
        
    
        self.SA = magdynlab.instruments.RS_FSL(ResourceName=RN_FSL,
                                               logFile=logFile)
        self.SG = magdynlab.instruments.RS_SMF(ResourceName=RN_SMF,
                                               logFile=logFile)
        self._Tr = self.SA.trace

        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.power_spectra' #power vs freq

    @ThD.as_thread
    def measure(self, freqs, file_name=None):

        self.Data['f'] = freqs
        self.Data['power'] = numpy.zeros_like(freqs) + numpy.nan

        for i, f in enumerate(freqs):
            self.SG.frequency = f
            self.SA.center_frequency = f
            time.sleep(0.01)
            self.SA.INIT()
            time.sleep(0.1)
            P = self._Tr.getFDAT(new=False)
            self.Data['power'][i] = P.mean()
            Plot_Pw_vs_f(self.Data)

        if file_name is not None:
            self.Data.save(file_name)



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
def Plot_RxH(Data):
    f = plt.figure('MR RxH', (5, 4))

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]

    #check Y scale
    ymax = numpy.nanmax(Data['R'])
    ymin = numpy.nanmin(Data['R'])
    dy  = numpy.max([ymax - ymin, 1E-6])

    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim([Data['h'].min(), Data['h'].max()])
        ax.set_ylim([ymax+dy, ymin-dy])
        
    line = ax.lines[-1]
    line.set_data(Data['h'], Data['R'])
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('R (Ohm)')
    ax.grid(True)

    yc = (ymax + ymin)/2
    ymin, ymax = ax.get_ylim()
    ymax = numpy.max([yc + dy*1.1/2, ymax])
    ymin = numpy.min([yc - dy*1.1/2, ymin])
    ax.set_ylim([ymin, ymax])

    f.tight_layout()
    f.canvas.draw()
    f.savefig('RxH.png')

def resistance(Data):
    I = Data['I']
    V = Data['V']
    R = numpy.polyfit(I, V, 1)[0]
    return R


class RxH(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')

        defaultRN = dict(RN_Kepco = 'TCPIP::192.168.13.7::KepcoBOP2020::INSTR',
                         RN_SCA = 'TCPIP::192.168.13.7::5025::SOCKET')
        defaultRN.update(ResouceNames)
        RN_Kepco = defaultRN['RN_Kepco']
        RN_SCA = defaultRN['RN_SCA']

        PowerSource = magdynlab.instruments.KEPCO_BOP(ResourceName=RN_Kepco,
                                                      logFile=logFile)
        self.SCA = magdynlab.instruments.KEYSIGHT_B1500A(ResourceName=RN_SCA,
                                             logFile=logFile)

        self.FC = magdynlab.controllers.FieldController(PowerSource)
        self.FC.Kepco.Voltage = 15

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.RxH_Semi'
        self.Info = ''
        self.PlotFunct = resistance


    @ThD.as_thread
    def Measure(self, crv, file_name=None):
        fields = crv
        self.Data['h'] = fields
        self.Data['R'] = numpy.zeros_like(fields) + numpy.nan
        self.Data.info = self.Info

        # Get one measurement to get the data shape and dictionaries
        m_data = self.SCA.getResultDictionary(new=True, delete=True)
        for key in m_data.keys():
            data_shape = ( len(fields), len(m_data[key]) )
            self.Data[key] = numpy.zeros(data_shape)

        # Loop for each field
        for i, h in enumerate(fields):

            self.FC.setField(h)

            m_data = self.SCA.getResultDictionary(new=True, delete=True)
            for key in m_data.keys():
                self.Data[key][i,:] = m_data[key]

            self.Data['R'][i] = self.PlotFunct(m_data)
            Plot_RxH(self.Data)

            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)
            self.Data.savetxt(file_name + '.RxH', keys=['h', 'R'])

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

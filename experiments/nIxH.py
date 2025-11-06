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
def Plot_nIxH(Data):
    f = plt.figure('ISHE IxH', (5, 4))

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]

    #check Y scale
    ymax = numpy.nanmax(Data['I']*1E9)
    ymin = numpy.nanmin(Data['I']*1E9)
    dy  = numpy.max([ymax - ymin, 1])

    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim([Data['h'].min(), Data['h'].max()])
        ax.set_ylim([ymax+dy, ymin-dy])
        
    line = ax.lines[-1]
    line.set_data(Data['h'], Data['I']*1E9)
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('I (nA)')
    ax.grid(True)

    yc = (ymax + ymin)/2
    ymin, ymax = ax.get_ylim()
    ymax = numpy.max([yc + dy*1.1/2, ymax])
    ymin = numpy.min([yc - dy*1.1/2, ymin])
    ax.set_ylim([ymin, ymax])

    f.tight_layout()
    f.canvas.draw()
    f.savefig('nIxH.png')


class nIxH(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')

        defaultRN = dict(RN_Kepco = 'TCPIP::192.168.13.7::KepcoBOP2020::INSTR',
                         RN_nIMeter = 'TCPIP::192.168.13.11::INSTR')
        defaultRN.update(ResouceNames)
        RN_Kepco = defaultRN['RN_Kepco']
        RN_nIM = defaultRN['RN_nIMeter']

        PowerSource = magdynlab.instruments.KEPCO_BOP(ResourceName=RN_Kepco,
                                                      logFile=logFile)
        self.nVM = magdynlab.instruments.KEYSIGHT_34461A(ResourceName=RN_nIM,
                                             logFile=logFile)

        self.FC = magdynlab.controllers.FieldController(PowerSource)
        self.FC.Kepco.Voltage = 15

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.nIxH'
        self.Info = ''


    @ThD.as_thread
    def Measure(self, crv, file_name=None, hold=0.05, reps=1):
       
        fields = crv
        self.Data['h'] = fields
        self.Data['I'] = numpy.zeros_like(fields) + numpy.nan
        self.Data.info = self.Info

        # Loop for each field
        for i, h in enumerate(fields):

            self.FC.setField(h)
            time.sleep(hold)
            values = numpy.zeros((reps))
            for j in range(reps):
                values[j] = self.nVM.query_float('READ?')
            self.Data['I'][i] = float(values.mean())
            Plot_nIxH(self.Data)

            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)
            self.Data.savetxt(file_name + '.nIxH', keys=['h', 'I'])

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

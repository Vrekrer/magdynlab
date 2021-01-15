# coding=utf-8

# Author: Diego Gonzalez Chavez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# magdynlab
# Rutinas de analisis para los datos medidos con:
#   experiments/MI
#
# TODO:
# Make documentation

import numpy
import matplotlib
import matplotlib.pyplot as plt

class _MI(object):
    '''
    Broadband MI measurement
    '''

    def getHi(self, h):
        return numpy.argmin(numpy.abs(self.h - h))

    def getFi(self, f):
        return numpy.argmin(numpy.abs(self.f - f))

    def getOutH(self, h):
        hi = numpy.argmin(numpy.abs(self.h - h))
        return self.ColorMapData[hi]

    def getOutF(self, f):
        fi = numpy.argmin(numpy.abs(self.f - f))
        return self.ColorMapData[:,fi]

    def Calc(self,  Sfunct, *args, **kargs):
        Sfunct(self, *args,  **kargs)

    def plot_ColorMap(self, fig='Auto'):
        if fig == 'Auto':
            fig = self.file.split('/')[-1] + '_CM'

        data = self.ColorMapData
        if self.sweepDir == '-1':
            data = data[::-1]
        extent = self.extent

        if self.ColorMapData.dtype != 'complex':
            fig = plt.figure(fig, (4,4))
            fig.clear()
            plt.xlim(*extent[[0,1]])
            plt.ylim(*extent[[2,3]])
            plt.xlabel('Field (Oe)')
            plt.ylabel('Freq (MHz)')
            plt.imshow(data.T,
                       aspect = 'auto',
                       origin = 'lower',
                       extent = extent)
            fig.tight_layout()
            fig.canvas.draw()
        else:
            fig = plt.figure(fig, (7,4))
            fig.clear()
            for pl in [121, 122]:
                plt.subplot(pl)
                plt.xlim(*extent[[0,1]])
                plt.ylim(*extent[[2,3]])
                plt.xlabel('Field (Oe)')
                plt.ylabel('Freq (MHz)')
            ax = fig.axes[0]
            ax.imshow(data.real.T,
                      aspect = 'auto',
                      origin = 'lower',
                      extent = extent)
            ax = fig.axes[1]
            ax.imshow(data.imag.T,
                      aspect = 'auto',
                      origin = 'lower',
                      extent = extent)
            fig.tight_layout()
            fig.canvas.draw()

    def plotH(self, h, fig='Auto'):
        if fig == 'Auto':
            fig = self.file.split('/')[-1] + '_H'
        data = self.getOutH(h)
        fig = plt.figure(fig,  (4, 3))
        plt.plot(self.f/1E6, data.real, '-')
        plt.grid(True)
        plt.xlabel('Freq (MHz)')
        if data.dtype == 'complex':
            plt.plot(self.f/1E6, data.imag, '--')
        fig.tight_layout()

    def plotF(self, f, fig='Auto'):
        if fig == 'Auto':
            fig = self.file.split('/')[-1] + '_F'
        data = self.getOutF(f)
        fig = plt.figure(fig,  (4, 3))
        plt.plot(self.h, data.real, '-')
        plt.grid(True)
        plt.xlabel('Field (Oe)')
        if data.dtype == 'complex':
            plt.plot(self.h, data.imag, '--')
        fig.tight_layout()

    def To_PowSpectra(self, file_name, info=''):
        numpy.savez_compressed(file_name + '.PowerSpectra',
                               info=info,
                               outArray=self.ColorMapData.real, 
                               h=self.h, f=self.f)

    @property
    def extent(self):
        return numpy.array([self.h.min(), self.h.max(), 
                            self.f.min()/1E6, self.f.max()/1E6])

class MI(_MI):
    '''
    Broadband MI measurement port
    '''

    def __init__(self, file_name):
        npz_file = numpy.load(file_name+'.ZxH_Raw.npz')
        self.Info = str(npz_file['Info'])
        self.f = npz_file['f']
        self.h = npz_file['h']
        self.Z = npz_file['Z']
        self.Ref = npz_file['Ref']
        self.file = file_name

        self.sweepDir = '+1'
        if self.h[0]>self.h[-1]:
            self.sweepDir = '-1'

        self.ColorMapData = numpy.abs(self.Z)[:,:] - numpy.abs(self.Ref)[None,:]


class MI_t(_MI):
    '''
    Broadband FMR measurement 1 port
    '''

    def __init__(self, file_name):
        npz_file = numpy.load(file_name+'.Zxt_Raw.npz')
        self.Info = str(npz_file['Info'])
        self.f = npz_file['f']
        self.t = npz_file['t']
        self.t -= self.t[0]
        self.t[self.t>1E6] = numpy.nan
        self.t[self.t<-1E6] = numpy.nan
        self.Z = npz_file['Z']
        self.file = file_name

        self.ColorMapData = self.Z

    def get_ti(self, t):
        return numpy.argmin(numpy.abs(self.t - t))

    def getOut_t(self, t):
        ti = numpy.argmin(numpy.abs(self.t - t))
        return self.ColorMapData[ti]

    @property
    def extent(self):
        return numpy.array([self.t.min(), self.t.max(), 
                            self.f.min()/1E6, self.f.max()/1E6])

    def plot_ColorMap(self, fig='Auto'):
        if fig == 'Auto':
            fig = self.file.split('/')[-1] + '_CM'

        data = self.ColorMapData
        extent = self.extent

        if self.ColorMapData.dtype != 'complex':
            fig = plt.figure(fig, (4,4))
            fig.clear()
            plt.xlim(*extent[[0,1]])
            plt.ylim(*extent[[2,3]])
            plt.xlabel('time (s)')
            plt.ylabel('Freq (MHz)')
            plt.imshow(data.T,
                       aspect = 'auto',
                       origin = 'lower',
                       extent = extent)
            fig.tight_layout()
            fig.canvas.draw()
        else:
            fig = plt.figure(fig, (7,4))
            fig.clear()
            for pl in [121, 122]:
                plt.subplot(pl)
                plt.xlim(*extent[[0,1]])
                plt.ylim(*extent[[2,3]])
                plt.xlabel('time (s)')
                plt.ylabel('Freq (MHz)')
            ax = fig.axes[0]
            ax.imshow(data.real.T,
                      aspect = 'auto',
                      origin = 'lower',
                      extent = extent)
            ax = fig.axes[1]
            ax.imshow(data.imag.T,
                      aspect = 'auto',
                      origin = 'lower',
                      extent = extent)
            fig.tight_layout()
            fig.canvas.draw()

# coding=utf-8

# Author: Diego Gonzalez Chavez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# magdynlab
# Rutinas de analisis para los datos medidos con:
#   experiments/VNA_FMR_1P
#   experiments/VNA_FMR_2P
#
# TODO:
# Make documentation

import numpy
import matplotlib
import matplotlib.pyplot as plt

class _FMR_P(object):
    '''
    Broadband FMR measurement common functions
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
            plt.ylabel('Freq (GHz)')
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
                plt.ylabel('Freq (GHz)')
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
        plt.plot(self.f/1E9, data.real, '-')
        plt.grid(True)
        plt.xlabel('Freq (GHz)')
        if data.dtype == 'complex':
            plt.plot(self.f/1E9, data.imag, '--')
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
                            self.f.min()/1E9, self.f.max()/1E9])

class FMR_1P(_FMR_P):
    '''
    Broadband FMR measurement 1 port
    '''

    def __init__(self, file_name):
        npz_file = numpy.load(file_name+'.VNA_1P_Raw.npz')
        self.Info = str(npz_file['Info'])
        self.DateTime = str(npz_file['DateTime'])
        self.f = npz_file['f']
        self.h = npz_file['h']
        self.S11 = npz_file['S11']
        self.S11_Ref = npz_file['S11_Ref']
        self.file = file_name

        self.sweepDir = '+1'
        if self.h[0]>self.h[-1]:
            self.sweepDir = '-1'

        #Pabs = 1 - |S11|²
        #Pref = 1 -|S11_ref|²
        #CM = Pabs - Pref = |S11_ref|² - |S11|²
        self.ColorMapData = numpy.abs(self.S11_Ref)**2 - numpy.abs(self.S11)**2


class FMR_2P(_FMR_P):
    '''
    Broadband FMR measurement 2 ports
    '''

    def __init__(self, file_name):
        npz_file = numpy.load(file_name+'.VNA_2P_Raw.npz')
        self.Info = str(npz_file['Info'])
        self.DateTime = str(npz_file['DateTime'])
        self.f = npz_file['f']
        self.h = npz_file['h']
        
        self.S11 = npz_file['S11']
        self.S21 = npz_file['S21']
        self.S22 = npz_file['S22']
        self.S12 = npz_file['S12']
        
        self.S11_Ref = npz_file['S11_Ref']
        self.S21_Ref = npz_file['S21_Ref']
        self.S22_Ref = npz_file['S22_Ref']
        self.S12_Ref = npz_file['S12_Ref']
        
        self.file = file_name

        self.sweepDir = '+1'
        if self.h[0]>self.h[-1]:
            self.sweepDir = '-1'

        #Pabs = 1 - |S11|² - |S21|²
        #Pref = 1 -|S11_ref|² - |S21_ref|²
        #CM = Pabs - Pref = |S11_ref|² + |S21_ref|² - |S11|² - |S21|²
        self.ColorMapData = + numpy.abs(self.S11_Ref)**2 \
                            + numpy.abs(self.S21_Ref)**2 \
                            - numpy.abs(self.S11)**2 \
                            - numpy.abs(self.S21)**2


class FMR_dP_dH():
    '''
    FMR differential measurement
    '''

    def __init__(self, file_name):
        self.file = file_name
        x, y = numpy.loadtxt(file_name+'.dPxH', unpack=True)
        self.h = x
        self.dp_dh = y*1000
        with open(file_name+'.dPxH', 'r') as text_file: 
            lines = text_file.readlines()
        for line in lines:
            if 'Frequency' in line:
                self.f = float(line.split(':')[-1].split('G')[0])*1E9
            elif 'Osc Field' in line:
                self.h_ac = float(line.split(':')[-1].split('O')[0])
                break

    def plot(self, fig='Auto', stl='.-'):
        if fig == 'Auto':
            fig = self.file.split('/')[-1]
        fig = plt.figure(fig,  (4, 3))
        plt.plot(self.h, self.dp_dh, stl, label='%0.3f GHz'%(self.f/1E9))
        plt.legend()
        plt.xlabel('Field (Oe)')
        plt.ylabel('dp/dh (a.u.)')
        plt.grid(True)
        fig.tight_layout()

    def fit(self):
        pass


_dp_dh_script = '''
def dp_dh_fitfunct(h, %(prefix)sK1, %(prefix)sK2, %(prefix)sH_FMR, %(prefix)sDH):
    #Fitting function for FMR
    #Ref: Thesis (page 51) Georg Woltersdorf 2004 SIMON FRASER UNIVERSITY 
    #"SPIN-PUMPING AND TWO-MAGNON SCATTERING IN MAGNETIC MULTILAYERS"
    K1 = %(prefix)sK1
    K2 = %(prefix)sK2
    H_FMR = %(prefix)sH_FMR
    DH = %(prefix)sDH
    dh = h - H_FMR
    denom = (DH**2 + dh**2)**2
    return (-K1*2*dh*DH - K2*(DH**2-dh**2))/denom
'''

def dp_dh_model(prefix=''):
    import lmfit
    expr = 'dp_dh_fitfunct(x, %(prefix)sK1, %(prefix)sK2, %(prefix)sH_FMR, %(prefix)sDH)' % {'prefix':prefix}
    script = _dp_dh_script % {'prefix':prefix}
    return lmfit.models.ExpressionModel(expr,
                                        independent_vars=['x'],
                                        init_script=script,
                                        nan_policy='omit')

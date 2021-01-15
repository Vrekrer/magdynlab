# coding=utf-8

# Author: Diego Gonzalez Chavez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com

import numpy
import matplotlib.pyplot as plt

class MxH(object):
    def __init__(self, file_name, Hs = 100, smooth = None, 
                 incl = False, Hcs = False, Invert = False,
                 skiprows = 'Auto', usecols = 'Auto', delimiter = ' '):
        self.file_name = file_name
        self.Analizar(Hs, smooth, incl, Hcs, Invert, skiprows, usecols, delimiter)
    def Analizar(self, Hs = 100, smooth = None, 
                 incl = False, Hcs = False, Invert = False, 
                 skiprows = 'Auto', usecols = 'Auto', delimiter = ' '):
        #Nomalizacion y calculo de campos coersivo y de exchange
        if skiprows == 'Auto':
            skiprows = 0
        if usecols == 'Auto':
            usecols = (0,1,2)
            
        try:
            (H,M,E) = numpy.loadtxt(self.file_name, unpack = True, 
                                    usecols = usecols, skiprows = skiprows,
                                    delimiter = delimiter)
        except:
            (H,M) = numpy.loadtxt(self.file_name, unpack = True, 
                                  usecols = usecols[0:2], skiprows = skiprows,
                                  delimiter = delimiter)
            E = numpy.ones_like(H)

        if Invert:
            M *= -1
            H *= -1
        if smooth != None:
            M = smoothX(M, smooth)

        self.M_Raw = M
        self.H = H
        self.E = E

        if numpy.isscalar(Hs):
            Hs = [-Hs, Hs]
        
        Hn = H[H<Hs[0]]
        Mn = M[H<Hs[0]]
        En = E[H<Hs[0]] + 1E-25
        Wn = (1/En)/(1/En).sum()
        
        Hp = H[H>Hs[1]]
        Mp = M[H>Hs[1]]
        Ep = E[H>Hs[1]] + 1E-25
        Wp = (1/Ep)/(1/Ep).sum()
        
        if incl:
            #Tirar la inclinacion de la curva
            pn = numpy.polyfit(Hn,Mn,1,w=Wn)
            pp = numpy.polyfit(Hp,Mp,1,w=Wp)
            
            M = M - H*(pn[0]*len(Hn)+pp[0]*len(Hp))/(len(Hn) + len(Hp))
            Mn = M[H<Hs[0]]
            Mp = M[H>Hs[1]]

        Mm = (Mn*Wn).sum()
        MM = (Mp*Wp).sum()       
    
        self.M = ( M - (MM+Mm)/2 )
        self.Mn = self.M / ((MM-Mm)/2)
        self.Ms = (MM-Mm)/2.0

        if Hcs:
            smag = numpy.sign(self.Mn)
            smag[0] = 0
            tst1 = numpy.abs(smag - numpy.roll(smag, 1)) == 2
            tst2 = numpy.abs(smag - numpy.roll(smag, -1)) == 2
            tst = tst1 + tst2
            Ht = H[tst]
            Mt = self.Mn[tst]
            H1 = Ht[0] - ((Ht[0]-Ht[1])/(Mt[0]-Mt[1]))*Mt[0]
            H2 = Ht[-1] - ((Ht[-1]-Ht[-2])/(Mt[-1]-Mt[-2]))*Mt[-1]
            self.Hex = (H1 + H2)/2
            self.Hc = numpy.abs(H1 - H2)/2
    def plotM(self, opt = 'bo-', figN = 1):
        plt.figure(figN)
        plt.plot(self.H, self.M, opt)
        plt.grid(True)
        plt.xlabel('Field (Oe)')
        plt.ylabel('Magentization (e.m.u.)')

    def plotMn(self, opt = 'bo-', figN = 2):
        plt.figure(figN)
        plt.plot(self.H, self.Mn, opt)
        plt.grid(True)
        plt.xlabel('H(Oe)')
        plt.ylabel('M/Ms')

    def saveMn(self, file_name):
        numpy.savetxt(file_name, numpy.array([self.H, self.Mn]).T, fmt = '%.5e')
    def saveM(self, file_name):
        numpy.savetxt(file_name, numpy.array([self.H, self.M]).T, fmt = '%.5e')

def smoothX(x, wl = 5):
    w= numpy.hanning(2*wl+1)
    w = w/w.sum()
    s = numpy.r_[numpy.ones(wl)*x[0], x, numpy.ones(wl)*x[-1]]
    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

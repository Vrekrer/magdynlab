# coding=utf-8

# Author: Diego Gonzalez Chavez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# magdynlab
# Filtros para colormaps
#
# TODO:
# Make documentation

import numpy
import scipy
import scipy.signal
import scipy.optimize

def Spline_Filter(HF, a=50):
    HF.ColorMapData = scipy.signal.spline_filter(HF.ColorMapData, a)

def Gaussian_Filter(HF, nf=5,  nh='nf'):
    HF.ColorMapData = Smooth(HF.ColorMapData, nf,  nh)

def Smooth(S, nf=3,  nh='nf'):
    if nh == 'nf':
        nh = nf
    nh = int(nh)
    nf = int(nf)
    x, y = numpy.mgrid[-nh:nh+1, -nf:nf+1]
    g = numpy.exp(-(x**2.0/nh + y**2.0/nf))
    g = g / g.sum()
    out = scipy.ndimage.convolve(S.real, g, mode='nearest')
    if S.dtype == 'complex':
        out = out + 1.0j*scipy.ndimage.convolve(S.imag, g, mode='nearest')
    return out

def Revove_BG_Min(HF, nf=5, nh=5):
    S = HF.ColorMapData.copy()
    S = Smooth(S, nf=nf, nh=nh)
    bg = numpy.min(S.real, axis=0)
    HF.ColorMapData -= bg[None,:]
    if HF.ColorMapData.dtype == 'complex':
        bgC = numpy.min(S.imag, axis=0)
        HF.ColorMapData -= bgC[None,:]

def Revove_BG_Median(HF):
    S = HF.ColorMapData.copy()
    bg = numpy.zeros_like(S[0,:].real)
    m = numpy.median(S.real, axis=0)
    for i, x in enumerate(m):
        bg[i] = numpy.mean(S.real[:,i][S[:,i].real < x])
    HF.ColorMapData -= bg[None,:]
    if S.dtype == 'complex':
        m = numpy.median(S.imag, axis=0)
        for i, x in enumerate(m):
            bg[i] = numpy.mean(S.imag[:,i][S[:,i].imag < x])
        HF.ColorMapData -= 1.0j*bg[None,:]

def Cut_Freqs(HF, f_min, f_max):
    i_min = HF.getFi(f_min)
    i_max = HF.getFi(f_max)
    HF.f = HF.f[i_min:i_max]
    HF.ColorMapData = HF.ColorMapData[:,i_min:i_max]

def Cut_Fields(HF, h_min, h_max):
    if HF.sweepDir == '-1':
        i_min = HF.getHi(h_max)
        i_max = HF.getHi(h_min)
    else:
        i_min = HF.getHi(h_min)
        i_max = HF.getHi(h_max)
    HF.h = HF.h[i_min:i_max]
    HF.ColorMapData = HF.ColorMapData[i_min:i_max]

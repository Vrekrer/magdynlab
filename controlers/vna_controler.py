# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Vector Network Analizer controler
#
# TODO:
# Make documentation

__all__ = ['VNA_Controler']


class VNA_Controler(object):
    '''
    Vector Network Analizer controler
    '''

    def __init__(self, VNA_instrument):
        self.VNA = VNA_instrument

    def getSData(self, TrN, new=True):
        X = self.VNA.Ch1.Traces[TrN].getSDAT(new)
        return X.copy()

    @property
    def frequencies(self):
        return self.VNA.Ch1.getSTIM()

import numpy as np
try:
    from pyfftw.interfaces.scipy_fftpack import fftn, ifftn
except ImportError:
    print "no pyfftw package, going to use fft from scipy"
    from scipy.fftpack import fftn, ifftn
from rtk import identity_mapping


class BiharmonicRegularizer(object):

    def __init__(self, shape, convexity_penalty=1., norm_penalty=1.):
        self.shape = shape
        self.ndim = len(shape)
        self.convexity_penalty = convexity_penalty
        self.norm_penalty = norm_penalty

        self.set_operator()

    def set_operator(self):
        dx_sqinv = 1.

        A = self.norm_penalty * np.ones(self.shape)

        grid = identity_mapping(self.shape)

        for frequencies, length in zip(grid, self.shape):
            A += 2 * self.convexity_penalty * (
                1 - np.cos(2 * np.pi * frequencies / length)) * dx_sqinv

        # Since this is biharmonic, the exponent is 2.
        self.operator = 1 / (A ** 2)

    def __call__(self, momentum):
        G = np.zeros(momentum.shape, dtype=np.complex128)
        for i in xrange(len(momentum)):
            try:
                G[i] = fftn(momentum[i], threads=5)
            except:
                G[i] = fftn(momentum[i])

        F = G * self.operator

        vector_field = np.zeros_like(momentum)
        for i in xrange(len(momentum)):
            try:
                vector_field[i] = np.real(ifftn(F[i], threads=5))
            except:
                vector_field[i] = np.real(ifftn(F[i]))

        return vector_field

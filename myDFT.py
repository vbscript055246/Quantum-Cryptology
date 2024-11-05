import matplotlib.pyplot as plt
import numpy as np

#plt.style.use('seaborn-poster')
# %matplotlib inline

def DFT(x):
    """
    Function to calculate the
    discrete Fourier Transform
    of a 1D real-valued signal x
    """

    N = len(x)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp(-2j * np.pi * k * n / N)

    X = np.dot(e, x)

    return X

# sampling rate
# sr = 1000
# sampling interval
# ts = 1.0/sr
# t = np.arange(0, 1, ts)
# freq = 1.
# x = 3*np.sin(2*np.pi*freq*t)
# freq = 8
# x += np.sin(2*np.pi*freq*t)
# freq = 5
# x += 0.5*np.sin(2*np.pi*freq*t)

x = [i % 9 + 1 for i in range(256)]

plt.figure(figsize=(8, 6))
# plt.plot(t, x, 'r')
plt.plot(range(256), x, 'r')
plt.ylabel('Amplitude')
plt.show()

X = DFT(x)

# calculate the frequency
# N = len(X)
# n = np.arange(N)
# T = N/sr
# freq = n/T

plt.figure(figsize=(8, 6))
plt.stem(range(256), abs(X), 'b', markerfmt=" ", basefmt="-b")
plt.xlabel('Freq (Hz)')
plt.ylabel('DFT Amplitude |X(freq)|')
plt.show()
import numpy as np
import scipy as sp
# import scipy.linalg
import time


t0 = time.time()
a = np.random.normal(size=(1600,1600))
sp.linalg.svd(a)
print( time.time()-t0 )

# For channels.py, this results in pyzo closing the connection because
# the other side seems unresponsive.

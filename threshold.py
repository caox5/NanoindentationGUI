import numpy as np

class CP():  # Threshold
    def calculate(x,y):
        if CP.yth > np.max(y) or CP.yth < np.min(y):
            return False
        jrov = 0
        for j in range(len(y)-1, 1, -1):
            if y[j] > CP.yth and y[j-1] < CP.yth:
                jrov = j
                break
        if jrov==0 or jrov==len(y)-1:
            return False
        x0 = x[jrov]
        if CP.ddx <= 0:
            jxalign = np.argmin((x - (x0 - CP.dx)) ** 2)
            f0 = y[jxalign]
        else:
            jxalignLeft = np.argmin((x-(x0-CP.dx-CP.ddx))**2)
            jxalignRight = np.argmin((x-(x0-CP.dx+CP.ddx))**2)
            f0 = np.average(y[jxalignLeft:jxalignRight])
        jcp = jrov
        for j in range(jrov, 1, -1):
            if y[j] > f0 and y[j-1] < f0:
                jcp = j
                break
        if jcp == 0:
            return False
        xcp = x[jcp] + CP.sh
        ycp = y[np.argmin( (x-xcp)**2)]
        return [xcp, ycp]

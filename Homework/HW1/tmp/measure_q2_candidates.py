import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/cvhomework-mpl')
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

im = np.array(Image.open('campus.png').convert('RGB'))
gray = im @ np.array([.299,.587,.114])
sm = gaussian_filter(gray, .65)
detail = sm - gaussian_filter(gray, 5)
fig, ax=plt.subplots(figsize=(17,5))
ax.imshow(im[2070:2400,1700:4096], extent=(1700,4096,2400,2070))
ax.set_xticks(np.arange(1700,4100,100)); ax.set_yticks(np.arange(2080,2400,20))
ax.grid(alpha=.4); fig.tight_layout(); fig.savefig('tmp/pdfs/q2_paving_detail.png',dpi=140)
plt.close(fig)
# Strong local dark minima around each nominal longitudinal grout track.
for label, xbottom, dxdy in [('left',1880,-.50),('center',2110,-.18),('right',2800,.8),('far_right',3380,1.8)]:
    print(label)
    for y in [2180,2190,2200,2210,2220,2230,2240,2250,2260,2270,2280,2290,2300,2310,2320,2330,2340,2350]:
        xguess=int(xbottom+dxdy*(y-2355))
        xs=np.arange(xguess-18,xguess+19)
        v=detail[y-1:y+2,xs].mean(axis=0)
        j=v.argmin()
        print(y,int(xs[j]),round(float(v[j]),1))

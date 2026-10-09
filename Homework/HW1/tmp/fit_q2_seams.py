import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/cvhomework-mpl')
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

im = np.array(Image.open('campus.png').convert('RGB'))
gray = im @ np.array([.299,.587,.114])
sm = gaussian_filter(gray,.65)
response = gaussian_filter1d(sm,5,axis=1)-sm
ys=np.arange(2170,2356,1.)
candidates=[('D1',2114,-.25,8,.10),('D2',4010,3.2,40,.45),('D3',3100,1.4,35,.35),('D4',2800,1.,30,.25)]
results=[]
for label,xb,d,rx,rd in candidates:
    x0s=np.arange(xb-rx,xb+rx+.01,.5)
    ds=np.arange(d-rd,d+rd+.001,.002)
    dd,xx=np.meshgrid(ds,x0s)
    xx=xx.ravel();dd=dd.ravel()
    coordsx=xx[:,None]+dd[:,None]*(ys-2355)
    vals=map_coordinates(response,[np.broadcast_to(ys,coordsx.shape),coordsx],order=1)
    scores=np.clip(vals,-5,18).mean(axis=1)
    j=scores.argmax(); xbest=xx[j]; dbest=dd[j]
    print(label,'x(y)=',xbest,'+',dbest,'*(y-2355), score',scores[j])
    results.append((label,xbest,dbest))
fig,ax=plt.subplots(figsize=(18,5))
ax.imshow(im[2070:2400,1800:4096],extent=(1800,4096,2400,2070))
colors=['cyan','magenta','lime','orange']
for (label,xb,d),color in zip(results,colors):
    ax.plot(xb+d*(ys-2355),ys,color=color,lw=1.2,label=label)
ax.set_xticks(np.arange(1800,4100,100)); ax.set_yticks(np.arange(2080,2400,20)); ax.grid(alpha=.2)
ax.legend();fig.tight_layout();fig.savefig('tmp/pdfs/q2_seam_fits.png',dpi=120)
plt.close(fig)
for other in results[1:]:
    _,x1,d1=results[0];_,x2,d2=other
    y=2355+(x2-x1)/(d1-d2);x=x1+d1*(y-2355)
    print('VP D1 with',other[0],x,y)

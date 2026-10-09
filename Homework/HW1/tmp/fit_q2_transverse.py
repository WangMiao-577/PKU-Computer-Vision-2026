import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/cvhomework-mpl')
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

im=np.array(Image.open('campus.png').convert('RGB'))
gray=im @ np.array([.299,.587,.114])
sm=gaussian_filter(gray,.8)
response=gaussian_filter1d(sm,5,axis=0)-sm
xs=np.arange(1900,4001,2.)
results=[]
for label,yguess,ry in [('T1',2365,10),('T2',2270,20),('T3',2230,20),('T4',2305,15)]:
    yy,ss=np.meshgrid(np.arange(yguess-ry,yguess+ry+.01,.25),np.arange(-.030,.006,.00025))
    yy=yy.ravel();ss=ss.ravel()
    coordsy=yy[:,None]+ss[:,None]*(xs-2400)
    vals=map_coordinates(response,[coordsy,np.broadcast_to(xs,coordsy.shape)],order=1)
    scores=np.clip(vals,-3,10).mean(axis=1)
    j=scores.argmax();yb=yy[j];s=ss[j]
    results.append((label,yb,s))
    print(label, 'y(x)=',yb,'+',s,'*(x-2400); score',scores[j])
fig,ax=plt.subplots(figsize=(18,5))
ax.imshow(im[2070:2410,1700:4096],extent=(1700,4096,2410,2070))
colors=['cyan','magenta','lime','orange']
for (label,yb,s),c in zip(results,colors):
    ax.plot(xs,yb+s*(xs-2400),color=c,lw=1,label=label)
ax.set_xticks(np.arange(1700,4100,100));ax.set_yticks(np.arange(2080,2420,20));ax.grid(alpha=.25);ax.legend()
fig.tight_layout();fig.savefig('tmp/pdfs/q2_transverse_fits.png',dpi=120)

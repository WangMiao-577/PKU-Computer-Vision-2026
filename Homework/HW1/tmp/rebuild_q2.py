"""Reconstruct Q2 from full-resolution measured/fitted ground-line segments.

This is a geometry/figure preparation helper, not an implementation of Q3.
All coordinates below refer to the original 4096 x 3072 campus.png.
Line endpoints encode fits to visible seams (including the gaps between pavers).
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/cvhomework-mpl')
import json
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEGMENTS = {
    'D1': [[2167.02, 2170.0], [2113.0, 2355.0]],
    'D2': [[2836.99, 2170.0], [3086.0, 2355.0]],
    'T1': [[1900.0, 2374.750], [4000.0, 2350.600]],
    'T2': [[1900.0, 2272.875], [4000.0, 2246.100]],
}
A = np.array([1891.,1953.])
B = np.array([1891.,2141.])
KNOWN_HEIGHT = .76


def homogeneous_point(xy):
    return np.r_[xy,1.]


lines = {name: np.cross(*[homogeneous_point(p) for p in pts])
         for name,pts in SEGMENTS.items()}
vd = np.cross(lines['D1'],lines['D2']); vd /= vd[2]
vt = np.cross(lines['T1'],lines['T2']); vt /= vt[2]
horizon = np.cross(vd,vt); horizon /= horizon[1]
yh = -(horizon[0]*A[0]+horizon[2])
camera_height = KNOWN_HEIGHT*(B[1]-yh)/(B[1]-A[1])
assert np.allclose([np.dot(horizon,vd),np.dot(horizon,vt)],0,atol=1e-7)
for name, vp in [('D1',vd),('D2',vd),('T1',vt),('T2',vt)]:
    assert abs(np.dot(lines[name],vp)) < 1e-5

# Independent closed-form slope/intercept check (no homogeneous cross products).
xd1,xd2=SEGMENTS['D1'],SEGMENTS['D2']
d1=(xd1[1][0]-xd1[0][0])/(xd1[1][1]-xd1[0][1])
d2=(xd2[1][0]-xd2[0][0])/(xd2[1][1]-xd2[0][1])
ycheck=2170+(xd2[0][0]-xd1[0][0])/(d1-d2)
assert np.isclose(ycheck,vd[1])
assert 1.45 < camera_height < 1.56

data={'image_size':[4096,3072],'fitted_segments':SEGMENTS,
      'vanishing_point_depth':vd.tolist(), 'vanishing_point_transverse':vt.tolist(),
      'horizon_line_a_b_c':horizon.tolist(),'A':A.tolist(),'B':B.tolist(),
      'horizon_y_at_A':yh,'reference_height_m':KNOWN_HEIGHT,
      'camera_height_m':camera_height,
      'description':'Coordinates are full-resolution pixels. Endpoint pairs represent fitted image lines. The camera height uses the approximately level camera assumption.'}
Path('tmp/pdfs/q2_measurements.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print(json.dumps(data,indent=2))

im = np.array(Image.open('campus.png').convert('RGB'))
colors={'D1':'#00d9ff','D2':'#00d9ff','T1':'#f500d4','T2':'#f500d4'}
plt.rcParams.update({'font.size':11,'font.family':'DejaVu Sans'})


def photo(ax):
    ax.imshow(im,extent=(0,4096,3072,0))


def label(ax,xy,text,color,offset=(8,8),size=11):
    ax.annotate(text,xy,xytext=offset,textcoords='offset points',color=color,
                fontsize=size,fontweight='bold',bbox=dict(facecolor='white',alpha=.90,edgecolor='none',pad=2))


# Overview: actual measured directions, their finite/in-frame vanishing point,
# and the horizon extended across the photograph. T's vanishing point is off-frame.
fig,ax=plt.subplots(figsize=(12.8,6.8))
photo(ax)
ax.set_xlim(0,4096);ax.set_ylim(2700,900)
for name,pts in SEGMENTS.items():
    p,q=np.array(pts)
    ax.plot(*np.array([p,q]).T,color=colors[name],lw=2.2)
    ax.scatter(*np.array([p,q]).T,s=20,c=colors[name],edgecolors='black',lw=.4,zorder=5)
    if name.startswith('D'):
        ax.plot([p[0],vd[0]],[p[1],vd[1]],'--',color=colors[name],lw=1.6)
    label(ax,q,name,colors[name],offset=((-22,-13) if name.startswith('T') else (6,-13)))
xs=np.array([0.,4096.]);ys=-(horizon[0]*xs+horizon[2])
ax.plot(xs,ys,color='#e51b23',lw=2.2)
ax.scatter(vd[0],vd[1],s=65,c='white',edgecolors='#e51b23',lw=2,zorder=6)
label(ax,vd[:2],f'V_D = ({vd[0]:.1f}, {vd[1]:.1f})','#c51b23',offset=(12,20),size=12)
label(ax,(150, -(horizon[0]*150+horizon[2])),
      f'horizon: y = {(-horizon[0]):.5f} x + {(-horizon[2]):.2f}', '#c51b23',offset=(0,18),size=12)
ax.plot([A[0],B[0]],[A[1],B[1]],color='#00c944',lw=2.6)
for point,name in [(A,'A'),(B,'B')]:
    ax.scatter(*point,s=45,c='white',edgecolors='#00ad3b',lw=2,zorder=7)
    label(ax,point,name,'#008d30',offset=(-22,4))
ax.set_xlabel('x (full-resolution pixels)');ax.set_ylabel('y (full-resolution pixels)')
fig.tight_layout();fig.savefig('figs/q2_overview.png',dpi=180)
plt.close(fig)

# Enlarged measurement evidence on the actual ground texture.
fig,axes=plt.subplots(2,1,figsize=(12.8,5.4))
for ax,names,title in [(axes[0],['D1','D2'],'Depth-direction paving joints'),
                       (axes[1],['T1','T2'],'Transverse boundary and paving joint')]:
    photo(ax);ax.set_xlim(1900,4050);ax.set_ylim(2400,2155)
    for name in names:
        p,q=np.array(SEGMENTS[name]);ax.plot(*np.array([p,q]).T,color=colors[name],lw=1.1)
        ax.scatter(*np.array([p,q]).T,s=18,c=colors[name],edgecolors='black',lw=.4)
        label(ax,q,name,colors[name],offset=(-22,8))
    ax.set_title(title,loc='left',fontsize=11)
    ax.set_yticks([2180,2240,2300,2360]);ax.set_xlabel('x (pixels)');ax.set_ylabel('y (pixels)')
fig.tight_layout();fig.savefig('figs/q2_line_measurements.png',dpi=180)
plt.close(fig)

# Reference-height construction. No invented human reference height is used.
fig,ax=plt.subplots(figsize=(11.8,6.8))
photo(ax);ax.set_xlim(1400,2350);ax.set_ylim(2250,1650)
xs=np.array([1400,2350]);ax.plot(xs,-(horizon[0]*xs+horizon[2]),color='#e51b23',lw=2)
ax.plot([A[0],B[0]],[A[1],B[1]],color='#00c944',lw=2.5)
for point,name in [(A,'A'),(B,'B')]:
    ax.scatter(*point,s=80,c='white',edgecolors='#00ad3b',lw=2)
    label(ax,point,f'{name} = ({point[0]:.0f}, {point[1]:.0f})','#008d30',offset=(12,5),size=12)
for y in [yh,A[1],B[1]]:
    ax.plot([1470,1891],[y,y],':',color='#00c944',lw=1)
for y0,y1,txt in [(yh,A[1],f'h1 = {A[1]-yh:.2f} px'),
                   (A[1],B[1],f'h2 = {B[1]-A[1]:.0f} px = 0.76 m')]:
    ax.annotate('',(1490,y0),(1490,y1),arrowprops=dict(arrowstyle='<->',color='#00c944',lw=2))
    label(ax,(1490,(y0+y1)/2),txt,'#008d30',offset=(8,-5),size=12)
label(ax,(1420, -(horizon[0]*1420+horizon[2])), f'horizon at x_A: y_h = {yh:.2f}', '#c51b23',offset=(0,16),size=12)
label(ax,(1440,2220),f'H = 0.76 x ({B[1]:.0f} - {yh:.2f}) / {B[1]-A[1]:.0f} = {camera_height:.3f} m',
      '#1d1d1d',offset=(0,0),size=12)
ax.set_xlabel('x (full-resolution pixels)');ax.set_ylabel('y (full-resolution pixels)')
fig.tight_layout();fig.savefig('figs/q2_zoom.png',dpi=180)
plt.close(fig)

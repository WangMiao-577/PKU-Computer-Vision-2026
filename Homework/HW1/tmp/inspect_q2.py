from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/cvhomework-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

im = Image.open('campus.png').convert('RGB')
regions = {
    'paving_left': (1600, 2070, 2500, 2400),
    'paving_right': (2500, 2070, 3500, 2400),
    'paving_far_right': (3300, 2020, 4096, 2400),
    'facade_left': (0, 600, 1500, 1950),
    'facade_right': (2400, 600, 4096, 1950),
}
for name, (x0,y0,x1,y1) in regions.items():
    fig, ax = plt.subplots(figsize=(min((x1-x0)/100,24), (y1-y0)/100+0.6))
    ax.imshow(im, extent=(0,4096,3072,0))
    ax.set_xlim(x0,x1); ax.set_ylim(y1,y0)
    ax.set_xticks(range((x0//50+1)*50,x1,50))
    ax.set_yticks(range((y0//50+1)*50,y1,50))
    ax.grid(alpha=.35)
    fig.tight_layout()
    fig.savefig(Path('tmp/pdfs') / f'q2_measure_{name}.png', dpi=110)
    plt.close(fig)

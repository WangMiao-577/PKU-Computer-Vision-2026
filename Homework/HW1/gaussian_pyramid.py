"""Question 3: image filtering and subsampling.

依赖: numpy（数组运算）、Pillow（读图/存图）、matplotlib（仅用于输出对比图）
运行: python3 gaussian_pyramid.py
      python3 gaussian_pyramid.py --image zebra.jpg --outdir out --kernel 5 --sigma 1.0
"""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

SCALES = ["original", "half", "quarter", "eighth"]


def cross_correlation_2d(img, kernel, pad="constant"):
    img = np.asarray(img, dtype=np.float64)
    kernel = np.asarray(kernel, dtype=np.float64)
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    pad_width = ((ph, ph), (pw, pw)) + ((0, 0),) * (img.ndim - 2)
    padded = np.pad(img, pad_width, mode=pad)
    out = np.zeros_like(img)
    for m in range(kh):
        for n in range(kw):
            out += kernel[m, n] * padded[m:m + img.shape[0], n:n + img.shape[1]]
    return out


def convolve_2d(img, kernel, pad="constant"):
    """g(i,j) = sum_{k,l} f(i-k, j-l) h(k,l)  -- flip both kernel axes."""
    flipped = np.asarray(kernel, dtype=np.float64)[::-1, ::-1]
    return cross_correlation_2d(img, flipped, pad)


def gaussian_blur_kernel_2d(k, sigma):
    if k % 2 == 0:
        raise ValueError("kernel size k must be odd")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    ax = np.arange(k) - k // 2
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx ** 2 + yy ** 2) / (2.0 * sigma ** 2))
    return kernel / kernel.sum()


def low_pass(img, k, sigma, pad="constant"):
    return convolve_2d(img, gaussian_blur_kernel_2d(k, sigma), pad)


def low_pass_separable(img, k, sigma, pad="constant"):
    kernel = gaussian_blur_kernel_2d(k, sigma)
    v = kernel[:, k // 2]
    h = kernel[k // 2, :]
    v = (v / v.sum()).reshape(-1, 1)
    h = (h / h.sum()).reshape(1, -1)
    return convolve_2d(convolve_2d(img, v, pad), h, pad)


def image_subsampling(img, s):
    if s < 1:
        raise ValueError("factor s must be >= 1")
    return np.asarray(img)[::s, ::s]


def gaussian_pyramid(img, levels=4, k=5, sigma=1.0, pad="constant"):
    pyr = [np.asarray(img, dtype=np.float64)]
    for _ in range(levels - 1):
        pyr.append(image_subsampling(low_pass(pyr[-1], k, sigma, pad), 2))
    return pyr


def direct_pyramid(img, levels=4):
    pyr = [np.asarray(img, dtype=np.float64)]
    for _ in range(levels - 1):
        pyr.append(image_subsampling(pyr[-1], 2))
    return pyr


def to_uint8(img):
    return np.clip(np.rint(img), 0, 255).astype(np.uint8)


def high_freq_energy(img):
    x = np.asarray(img, dtype=np.float64)
    lap = (
        4.0 * x[1:-1, 1:-1]
        - x[:-2, 1:-1] - x[2:, 1:-1] - x[1:-1, :-2] - x[1:-1, 2:]
    )
    return np.abs(lap).mean()


def save_image(img, path):
    Image.fromarray(to_uint8(img)).save(path)


def save_montage(gauss_pyr, direct_pyr, path):
    n = len(gauss_pyr)
    fig, axes = plt.subplots(2, n, figsize=(3.2 * n, 5.2))
    for i in range(n):
        for row, (pyr, name) in enumerate(
            ((gauss_pyr, "gaussian"), (direct_pyr, "direct"))
        ):
            im = to_uint8(pyr[i])
            axes[row, i].imshow(im, **({} if im.ndim == 3 else {"cmap": "gray"}))
            axes[row, i].set_title(f"{name}\n{im.shape[1]}x{im.shape[0]}", fontsize=9)
            axes[row, i].axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    """调用部分由AI完成，撰写了API接口和函数调用代码"""
    ap = argparse.ArgumentParser(description="HW1 Q3: filtering and subsampling")
    ap.add_argument("--image", default="zebra.jpg", help="input textured image")
    ap.add_argument("--outdir", default="out", help="output directory")
    ap.add_argument("--kernel", type=int, default=5, help="Gaussian kernel size (odd)")
    ap.add_argument("--sigma", type=float, default=1.0, help="Gaussian std deviation")
    ap.add_argument("--pad", default="constant", choices=["constant", "edge", "reflect"],
                    help="border padding used by the convolution")
    ap.add_argument("--gray", action="store_true",
                    help="convert the input to a single luminance channel")
    args = ap.parse_args()

    mode = "L" if args.gray else "RGB"
    img = np.asarray(Image.open(args.image).convert(mode), dtype=np.float64)
    channels = "grayscale" if img.ndim == 2 else f"RGB ({img.shape[2]} channels)"
    print(f"input {args.image}: {img.shape[1]}x{img.shape[0]}, {channels}")

    ref = low_pass(img, args.kernel, args.sigma, args.pad)
    sep = low_pass_separable(img, args.kernel, args.sigma, args.pad)
    print(f"separable vs 2-D kernel: max abs diff = {np.abs(ref - sep).max():.3e}")

    gauss_pyr = gaussian_pyramid(img, len(SCALES), args.kernel, args.sigma, args.pad)
    direct_pyr = direct_pyramid(img, len(SCALES))

    for tag, pyr in (("gaussian_pyramid", gauss_pyr), ("direct_pyramid", direct_pyr)):
        outdir = os.path.join(args.outdir, tag)
        os.makedirs(outdir, exist_ok=True)
        for i, level in enumerate(pyr):
            name = f"level{i}_{SCALES[i]}.png"
            save_image(level, os.path.join(outdir, name))
            print(f"saved {os.path.join(outdir, name)}  {level.shape[1]}x{level.shape[0]}")

    save_montage(gauss_pyr, direct_pyr, os.path.join(args.outdir, "comparison.png"))
    print(f"saved {os.path.join(args.outdir, 'comparison.png')}")

    print("\nlevel           size     MAE   max|diff|  pix>16   HF gauss / direct")
    for i in range(1, len(SCALES)):
        a, b = gauss_pyr[i], direct_pyr[i]
        d = np.abs(a - b)
        print(
            f"{SCALES[i]:>8} {a.shape[1]:>4}x{a.shape[0]:<4} "
            f"{d.mean():6.2f} {d.max():10.1f} {(d > 16).mean() * 100:7.1f}% "
            f"{high_freq_energy(a):9.2f} / {high_freq_energy(b):.2f}"
        )


if __name__ == "__main__":
    main()

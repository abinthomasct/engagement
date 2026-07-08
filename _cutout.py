import os
os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp/numba_cache")

import sys
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove, new_session


def cut(src_path, out_path, bg_is_green=True):
    src = Image.open(src_path).convert("RGB")
    session = new_session("u2net")
    cut = remove(src.convert("RGBA"), session=session)
    arr = np.asarray(cut)
    rgb = arr[:, :, :3].astype(np.int16)
    A = arr[:, :, 3].astype(np.uint8)

    # Defringe: knock out semi-transparent edge pixels dominated by the
    # (green) background colour so no coloured rim remains.
    if bg_is_green:
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        greenish = (g > r + 18) & (g > b + 18)
        A = np.where(greenish & (A < 250), 0, A).astype(np.uint8)

    Aimg = Image.fromarray(A)
    # tidy edge: pull in ~1px, soften slightly
    Aimg = Aimg.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))

    out = Image.merge("RGBA", (cut.split()[0], cut.split()[1], cut.split()[2], Aimg))
    bbox = out.getbbox()
    out = out.crop(bbox)
    out.save(out_path)

    # previews on a few backgrounds
    base = os.path.splitext(os.path.basename(out_path))[0]
    for col, name in [((28, 28, 38, 255), "dark"), ((92, 26, 43, 255), "wine"),
                      ((251, 246, 239, 255), "ivory")]:
        bgimg = Image.new("RGBA", out.size, col)
        bgimg.alpha_composite(out)
        bgimg.convert("RGB").save("/tmp/%s_%s.png" % (base, name))
    print("saved", out_path, out.size)


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2]
    green = (len(sys.argv) < 4) or (sys.argv[3] != "nogreen")
    cut(src, out, bg_is_green=green)

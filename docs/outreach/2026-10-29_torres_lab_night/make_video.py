"""Assemble rendered frames into an MP4 (H.264, loops cleanly on iPad) and a smaller GIF.

usage: python make_video.py <frames dir> <out basename> [--fps 15] [--gif-every 2] [--gif-width 1000]
Holds the last frame for 2 s and the first frame for 1 s so the loop reads as a cycle.
"""
import sys, os, glob, argparse
import numpy as np
import imageio.v2 as imageio
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("frames"); ap.add_argument("out")
ap.add_argument("--fps", type=int, default=15); ap.add_argument("--gif-every", type=int, default=2)
ap.add_argument("--gif-width", type=int, default=1000); ap.add_argument("--mp4-width", type=int, default=1920)
a = ap.parse_args()

files = sorted(glob.glob(os.path.join(a.frames, "frame_*.png")))
print(len(files), "frames")
first = Image.open(files[0])
w, h = first.size
mw = a.mp4_width - (a.mp4_width % 2)
mh = int(round(h * mw / w)); mh -= mh % 2

def load(f, width, height):
    im = Image.open(f).convert("RGB").resize((width, height), Image.LANCZOS)
    return np.asarray(im)

seq = [files[0]] * a.fps + files + [files[-1]] * (2 * a.fps)
writer = imageio.get_writer(a.out + ".mp4", fps=a.fps, codec="libx264", quality=8,
                            macro_block_size=None, ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
for f in seq:
    writer.append_data(load(f, mw, mh))
writer.close()
print("mp4", a.out + ".mp4", os.path.getsize(a.out + ".mp4") // 1024, "KB", (mw, mh))

gw = a.gif_width; gh = int(round(h * gw / w))
gif_files = files[:: a.gif_every]
frames = [Image.open(f).convert("RGB").resize((gw, gh), Image.LANCZOS).quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in gif_files]
dur = [int(1000 * a.gif_every / a.fps)] * len(frames)
dur[0] = 1000; dur[-1] = 2000
frames[0].save(a.out + ".gif", save_all=True, append_images=frames[1:], duration=dur, loop=0, optimize=False)
print("gif", a.out + ".gif", os.path.getsize(a.out + ".gif") // 1024, "KB", (gw, gh), len(frames), "frames")

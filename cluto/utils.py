import os
import platform
import subprocess

from PIL import Image

from ranges import CRanges

def asc(*a):
    return sorted(a)

# https://stackoverflow.com/questions/6631299/python-opening-a-folder-in-explorer-nautilus-mac-thingie
def open_path(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def between(lower_inc, value, upper_exc):
    return lower_inc <= value and value < upper_exc

def rect_overlap(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    if in_rect(ax1, ay1, bx1, by1, bx2, by2):
        return True
    if in_rect(ax1, ay2, bx1, by1, bx2, by2):
        return True
    if in_rect(ax2, ay2, bx1, by1, bx2, by2):
        return True
    if in_rect(ax2, ay1, bx1, by1, bx2, by2):
        return True
    if in_rect(bx1, by1, ax1, ay1, ax2, ay2):
        return True
    if in_rect(bx1, by2, ax1, ay1, ax2, ay2):
        return True
    if in_rect(bx2, by2, ax1, ay1, ax2, ay2):
        return True
    if in_rect(bx2, by1, ax1, ay1, ax2, ay2):
        return True
    return False

def in_rect(x, y, x1, y1, x2, y2):
    return x1 <= x and x < x2 and y1 <= y and y < y2

def intersect(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    x1 = max(ax1, bx1)
    y1 = max(ay1, by1)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)
    if x2 >= x1 and y2 >= y1:
        return x1, y1, x2, y2
    return None

def dimension(x1, y1, x2, y2):
    dx = x2-x1
    dy = y2-y1
    if dx < 0 or dy < 0:
        return -1
    return dx*dy

def image_fallback(path, whitelist, fallback, remove=True):
    fn, ext = os.path.splitext(path)
    if ext[1:].lower() not in whitelist:
        path2 = "{}.{}".format(fn, fallback)
        im = Image.open(path)
        im.save(path2)
        if remove:
            os.unlink(path)
        return path2
    return path

def merge_lines(lines, distance=5):
    m = {}
    for p,a,b in lines:
        for k in m:
            if abs(p-k) < distance:
                break
        else:
            k = p
            m[p] = CRanges()
        m[k].add(a,b)
    return m
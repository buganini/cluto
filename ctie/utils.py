import os
import platform
import subprocess

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
    
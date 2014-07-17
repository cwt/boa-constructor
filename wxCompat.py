# -*- coding: utf-8 -*-
try:
    from wx import NO_3D as wxNO_3D
except ImportError:
    from wx import wxNO_3D

try:
    from wx import DIALOG_MODAL as wxDIALOG_MODAL
except ImportError:
    from wx import wxDIALOG_MODAL

try:
    from wx import DIALOG_MODELESS as wxDIALOG_MODELESS
except ImportError:
    from wx import wxDIALOG_MODELESS


## Code from wx-2.8
import zlib
import cStringIO
def my_crunch_data(data, compressed):
    # compress it?
    if compressed:
        data = zlib.compress(data, 9)

    # convert to a printable format, so it can be in a Python source file
    data = repr(data)

    # This next bit is borrowed from PIL.  It is used to wrap the text intelligently.
    fp = cStringIO.StringIO()
    data = data + " "  # buffer for the +1 test
    c = i = 0
    word = ""
    octdigits = "01234567"
    hexdigits = "0123456789abcdef"
    while i < len(data):
        if data[i] != "\\":
            word = data[i]
            i = i + 1
        else:
            if data[i+1] in octdigits:
                for n in range(2, 5):
                    if data[i+n] not in octdigits:
                        break
                word = data[i:i+n]
                i = i + n
            elif data[i+1] == 'x':
                for n in range(2, 5):
                    if data[i+n] not in hexdigits:
                        break
                word = data[i:i+n]
                i = i + n
            else:
                word = data[i:i+2]
                i = i + 2

        l = len(word)
        if c + l >= 78-1:
            fp.write("\\\n")
            c = 0
        fp.write(word)
        c = c + l

    # return the formatted compressed data
    return fp.getvalue()

try:
    from wx.tools.img2py import crunch_data
except ImportError:
    crunch_data = my_crunch_data

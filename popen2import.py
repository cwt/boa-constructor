from wxPython import wx
import sys

if sys.version[:2] == '2.':
    from os import popen3
elif wx.wxPlatform == '__WXMSW__':

    try:
        from win32pipe import popen3
    except ImportError:
        wx.wxMessageBox('Please install Mark Hammond''s win32all package',
              'Import Error', wx.wxOK | wx.wxICON_EXCLAMATION)
        raise
else:
    def popen3(cmd):
        import popen2
        o, i, e = popen2.popen3(cmd)
        return i, o, e

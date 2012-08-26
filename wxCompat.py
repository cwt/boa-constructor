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


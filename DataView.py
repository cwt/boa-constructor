from wxPython.wx import *
from Designer import InspectableObjectCollectionView
from Utils import AddToolButtonBmpObject
from EditorModels import init_utils
import PaletteMapping
import os
            
class DataView(wxListCtrl, InspectableObjectCollectionView):
    viewName = 'Data'
    collectionMethod = init_utils
    postBmp = wxBitmap('Images/Inspector/Post.bmp', wxBITMAP_TYPE_BMP)
    cancelBmp = wxBitmap('Images/Inspector/Cancel.bmp', wxBITMAP_TYPE_BMP)
    def __init__(self, parent, inspector, model, compPal, companionClass):
        [self.wxID_DATAVIEW] = map(lambda _init_ctrls: NewId(), range(1))    
        wxListCtrl.__init__(self, parent, self.wxID_DATAVIEW, style = wxLC_SMALL_ICON)#wxLC_LIST)

        InspectableObjectCollectionView.__init__(self, inspector, model, compPal, companionClass,
          ((NewId(), 'Post', self.OnPost),
          (NewId(), 'Cancel', self.OnCancel)), 0)

        self.il = wxImageList(24, 24)
        self.SetImageList(self.il, wxIMAGE_LIST_SMALL)

        EVT_LEFT_DOWN(self, self.OnSelectOrAdd)
        EVT_LIST_ITEM_SELECTED(self, self.wxID_DATAVIEW, self.OnObjectSelect)
        EVT_LIST_ITEM_DESELECTED(self, self.wxID_DATAVIEW, self.OnObjectDeselect)

        self.selected = -1

        self.active = true
        self.model = model

    def addViewTools(self, toolbar):
        AddToolButtonBmpObject(self.model.editor, toolbar, self.postBmp, 'Post', self.OnPost)
        AddToolButtonBmpObject(self.model.editor, toolbar, self.cancelBmp, 'Cancel', self.OnCancel)

    def deleteFromNotebook(self):
        # set selection to source view
        self.model.views['Source'].focus()   
        self.notebook.DeletePage(self.pageIdx)

    def initialize(self):
        ctrls, props, events = self.organiseCollection()
        self.initObjectsAndCompanions(ctrls.creators, props, events)

    def refreshCtrl(self):
        self.DeleteAllItems()

        ctrls, props, events = self.organiseCollection()

        for ctrl in ctrls.creators:
            if ctrl.comp_name:
                try:
                    classObj = eval(ctrl.class_name)
                    className = classObj.__name__
                    idx1 = self.il.Add(PaletteMapping.bitmapForComponent(classObj, gray = true))
                except:
                    className = aclass
                    if len(self.model.module.classes[aclass].super):
                        base = self.model.module.classes[aclass].super[0]
                        try: base = base.__class__.__name__
                        except: pass #print 'ERROR', base
                        idx1 = self.il.Add(PaletteMapping.bitmapForComponent(aclass, base, gray = true))
                    else:
                        idx1 = self.il.Add(PaletteMapping.bitmapForComponent(aclass, 'Component'))
                
                self.InsertImageStringItem(0, '%s : %s' % (ctrl.comp_name, className), idx1)

    def loadControl(self, ctrlClass, ctrlCompanion, ctrlName, params):
        """ Create and register given control and companion.
            See also: newControl """
        args = self.setupArgs(ctrlName, params, self.handledProps)
        
        # Create control and companion
        companion = ctrlCompanion(ctrlName, self, ctrlClass)
        self.objects[ctrlName] = [companion, companion.designTimeObject(args), None]
        self.objectOrder.append(ctrlName)
        
        return ctrlName

    def selectNone(self):
        for itemIdx in range(self.GetItemCount()):
            a = wxLIST_STATE_SELECTED
            state = self.GetItemState(itemIdx, a)
            self.SetItemState(itemIdx, 0, wxLIST_STATE_SELECTED)

    def close(self):
        self.cleanup()
        InspectableObjectCollectionView.close(self)

    def OnSelectOrAdd(self, event):
        """ Control is clicked. Either select it or add control from palette """
        if self.compPal.selection:
            objName = self.newObject(self.compPal.selection[1], self.compPal.selection[2])
            self.compPal.selectNone()
            self.refreshCtrl()
        else:
            # Skip so that OnObjectSelect may be fired
            event.Skip()
    
    def OnObjectSelect(self, event):
        self.inspector.containment.cleanup()
        self.selected = event.m_itemIndex
        name = string.split(self.GetItemText(self.selected), ' : ')[0]
        self.inspector.selectObject(self.objects[name][1], self.objects[name][0], false)

    def OnObjectDeselect(self, event):
        self.inspector.cleanup()

    def OnPost(self, event):
        self.controllerView.saveOnClose = true
        self.close()

    def OnCancel(self, event):
        self.controllerView.saveOnClose = false
        self.close()

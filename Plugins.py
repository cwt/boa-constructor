#-----------------------------------------------------------------------------
# Name:        Plugins.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, glob, new, pprint

#from wxPython import wx

import Preferences, Utils

class PluginError(Exception):
    pass

class SkipPlugin(PluginError):
    """ Special error, used to abort importing plugins early if they depend
    on modules not loaded

    Warning indicating problem is displayed """

class SkipPluginSilently(SkipPlugin):
    """ Special error, used to abort importing plugins early if they depend
    on modules not available.

    Plugin is skipped silently.
    Used when user can do nothing about the problem (like switching platforms ;)
    """

def importFromPlugins(name):
    # find module
    pluginsPath = Preferences.pyPath + '/Plug-ins'
    paths = [pluginsPath]
    if Preferences.extraPluginsPath:
        paths.append(Preferences.extraPluginsPath)
    pluginRcPath = Preferences.rcPath+ '/Plug-ins'
    if Preferences.rcPath != Preferences.pyPath and os.path.isdir(pluginRcPath):
        paths.append(pluginRcPath)

    modname = name.replace('.', '/') + '.py'
    for pth in paths:
        modpath = os.path.join(pth, modname)
        if os.path.isfile(modpath):
            break
    else:
        raise ImportError, 'Module %s could not be found in Plug-ins'

    mod = new.module(name)

    execfile(modpath, mod.__dict__)

    return mod

def transportInstalled(transport):
    return transport in eval(
         Utils.createAndReadConfig('Explorer').get('explorer', 
                                                   'installedtransports'),{})

def readPluginsState(section):
    cfg = Utils.createAndReadConfig('Explorer')
    if cfg.has_section(section):
        if cfg.has_option(section, 'ordered'):
            ordered = eval(cfg.get(section, 'ordered'), {})
        else:
            ordered = []
        if cfg.has_option(section, 'disabled'):
            disabled = eval(cfg.get(section, 'disabled'), {})
        else:
            disabled = []
        return ordered, disabled
    else:
        return [], []
    
def writePluginsState(section, ordered, disabled):
    cfg = Utils.createAndReadConfig('Explorer')
    if not cfg.has_section(section):
        cfg.add_section(section)
    cfg.set(section, 'ordered', pprint.pformat(ordered))
    cfg.set(section, 'disabled', pprint.pformat(disabled))
    
    Utils.writeConfig(cfg)
    
def buildPluginExecList():
    if not Preferences.pluginSections:
        return []

    pluginExecList = []
    pluginPathGlobs = []
    for sect, path in zip(Preferences.pluginSections, Preferences.pluginPaths):
        pluginState = readPluginsState(sect)
        pluginPathGlobs.append( (os.path.join(path, '*.plug-in.py'), pluginState) )

    for globPath, (ordered, disabled) in pluginPathGlobs:
        globList = glob.glob(globPath)

        insIdx = 0
        orderedPlugins = []
        for pluginName in ordered:
            pluginFilename = os.path.join(os.path.dirname(globPath),
                                          pluginName)+'.plug-in.py'
            try:
                idx = globList.index(pluginFilename)
            except ValueError:
                #wxLogWarning('Ordered plugin: %s not found: %'%pluginFilename)
                pass
            else:
                del globList[idx]
                globList.insert(insIdx, pluginFilename)
                insIdx = insIdx + 1
                orderedPlugins.append(pluginFilename)

        disabledPlugins = []
        for pluginName in disabled:
            disabledPlugins.append(os.path.join(os.path.dirname(globPath),
                                                pluginName)+'.plug-in.py')

        for pluginFilename in globList:
            pluginExecList.append( (pluginFilename,
                                    pluginFilename in orderedPlugins,
                                    pluginFilename not in disabledPlugins) )
    return pluginExecList


def registerPreference(pluginName, prefName, defPrefValSrc, docs=[], info=''):
    """ Define a plug-in preference. Added to prefs.plug-ins.rc.py in needed """

    def addBlankLine(module, lineNo):
        module.addLine('', lineNo)
        return lineNo + 1
        
    Preferences.exportedPluginProps.append(prefName)
    # quick exit when name already exists
    if hasattr(Preferences, prefName):
        return 
    
    pluginPrefs = os.path.join(Preferences.rcPath, 'prefs.plug-ins.rc.py')
    lines = [l.rstrip() for l in open(pluginPrefs).readlines()]
    import moduleparse
    m = moduleparse.Module(pluginName, lines)
    if not m.globals.has_key(prefName):
        breakLineNames = m.break_lines.values()
        if pluginName not in breakLineNames:
            lineNo = addBlankLine(m, len(lines))
            lineNo = addBlankLine(m, lineNo)
            m.addLine('#-%s%s'%(pluginName, '-' * (80-2-len(pluginName))), lineNo)
            lineNo = addBlankLine(m, lineNo + 1)
        else:
            for l, n in m.break_lines.items():
                if pluginName == n:
                    lineNo = l + 1
                    break
            else:
                lineNo = len(lines)
                
        if docs:
            for doc in docs:
                m.addLine('# %s'%doc, lineNo); lineNo += 1
        if info:
            m.addLine('## %s'%info, lineNo); lineNo += 1
        
        try:
            value = eval(defPrefValSrc, Preferences.__dict__)
        except Exception, err:
            raise PluginError(
                  ('Could not create default value from "%s" for %s. (%s:%s)'%(
                  defPrefValSrc, prefName, err.__class__, err)))

        m.addLine('%s = %s'%(prefName, defPrefValSrc), lineNo)
        lineNo = addBlankLine(m, lineNo + 1)

        setattr(Preferences, prefName, value)
        open(pluginPrefs, 'wb').write(os.linesep.join(m.source))
    else:
        raise PluginError(
            '%s not in Preferences, but is defined in globals of '
            'prefs.plug-ins.rc.py'%prefName)
    

def assureConfigFile(filename, data):
    if not os.path.exists(filename):
        open(filename, 'w').write(data)

    


from IsolatedDebugger import DebugServer


isPythonScriptMetaType = {
    'Script (Python)': 1,
    }.has_key


class ZopeScriptDebugServer(DebugServer):

    def getFilenameAndLine(self, frame):
        """Returns the filename and line number for the frame.

        This implementation adjusts for Python scripts.
        """
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        # XXX Python scripts currently (Zope 2.5) use their meta type
        # as their filename.  This is efficient but brittle.
        if isPythonScriptMetaType(filename):
            meta_type = filename
            # XXX This assumes the user never changes the "script" binding.
            script = frame.f_globals.get('script', None)
            if script is not None:
                url = script.absolute_url()
                url = url.split('://', 1)[-1]
                # XXX This is not a valid URL according to RFC 2396!
                filename = 'zopedebug://%s/%s' % (url, meta_type)
                # Offset for Boa's purposes
                lineno = lineno + 1
                return filename, lineno
        return self.canonic(filename), lineno

    def getFrameNames(self, frame):
        """Returns the module and function name for the frame.
        """
        try:
            modname = frame.f_globals['__name__']
        except KeyError:
            modname = ''
        funcname = frame.f_code.co_name
        return modname, funcname


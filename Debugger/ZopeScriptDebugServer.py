
__traceable__ = 0

from IsolatedDebugger import DebugServer


isPythonScriptMetaType = {
    'Script (Python)': 1,
    }.has_key


class ZopeScriptDebugServer(DebugServer):

    # scripts_only_mode is turned on to stop only in through-the-web scripts.
    scripts_only_mode = 0

    def getFilenameAndLine(self, frame):
        """Returns the filename and line number for the frame.  Invoked often.

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

    def isTraceable(self, frame):
        """Indicates whether the debugger should step into the given frame.

        Invoked often.
        """
        if self.scripts_only_mode:
            filename = frame.f_code.co_filename
            if not isPythonScriptMetaType(filename):
                # Stop only in high-level scripts.
                return 0
        return DebugServer.isTraceable(self, frame)

    def isAScriptFrame(self, frame):
        """Indicates whether the given frame is a high-level script frame.
        """
        filename = frame.f_code.co_filename
        return isPythonScriptMetaType(filename)

    def getStackInfo(self):
        """Returns a tuple describing the current stack.
        """
        exc_type, exc_value, stack, frame_stack_len = (
            DebugServer.getStackInfo(self))

        if self.scripts_only_mode:
            # Filter non-script frames out of the stack.
            new_stack = []
            new_len = 0
            for idx in range(len(stack)):
                frame, lineno = stack[idx]
                if self.isAScriptFrame(frame):
                    new_stack.append((frame, lineno))
                    if idx < frame_stack_len:
                        new_len = new_len + 1
            stack = new_stack
            frame_stack_len = new_len

        return exc_type, exc_value, stack, frame_stack_len

    def afterHardBreakpoint(self, frame):
        # Set a default stepping mode.
        self.set_step()
        # Choose scripts_only_mode based on whether the hard break was in
        # a script or not.
        if self.isAScriptFrame(frame):
            self.scripts_only_mode = 1
        else:
            self.scripts_only_mode = 0



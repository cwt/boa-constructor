
from IsolatedDebugger import DebugServer

__traceable__ = 0


TAL_INTERP_MODULE_NAME = 'TAL.TALInterpreter'
TALES_MODULE_NAME = 'Products.PageTemplates.TALES'


isPythonScriptMetaType = {
    'Script (Python)': 1,
    }.has_key


class ZopeScriptDebugServer(DebugServer):
    """A debug server that facilitates debugging of Zope Python Scripts
    and Page Templates.
    """

    # scripts_only_mode is turned on to stop only in through-the-web scripts.
    scripts_only_mode = 0

    def getFilenameAndLine(self, frame):
        """Returns the filename and line number for the frame.  Invoked often.

        This implementation adjusts for Python scripts and page templates.
        """
        code = frame.f_code
        filename = code.co_filename
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

        if code.co_name == 'interpret':
            source_file, ln = self.getTALPosition(frame)
            if source_file:
                return self.TALSourceToURL(source_file), ln

        return self.canonic(filename), lineno

    def TALSourceToURL(self, source_file):
        if source_file.startswith('traversal:'):
            path = source_file[10:]
            if path.startswith('/'):
                path = path[1:]
            meta_type = 'Page Template'
            host = 'localhost:8080'  # XXX XXX!
            return 'zopedebug://%s/%s/%s' % (host, path, meta_type)
        return source_file  # TODO: something better

    def getTALPosition(self, frame):
        """If the frame is in TALInterpreter.interpret(), detects what
        template was being interpreted and where, but only for specific
        interpreter frames.  Returns the source file and line number.
        """
        # Get TAL frames.  XXX brittle in many ways.
        if frame.f_globals.get('__name__') == TAL_INTERP_MODULE_NAME:
            caller = frame.f_back
            if caller.f_globals.get('__name__') == TAL_INTERP_MODULE_NAME:
                caller_name = caller.f_code.co_name
                source_file = None
                position = None
                if caller_name in ('do_useMacro', 'do_defineSlot'):
                    # Using a macro or slot.
                    # Expect to find saved_source and saved_position in
                    # locals.
                    source_file = caller.f_locals.get('saved_source')
                    position = caller.f_locals.get('saved_position')
                elif caller_name == '__call__':
                    # Calling the TAL interpreter.
                    interp = caller.f_locals.get('self', None)
                    if interp:
                        source_file = interp.sourceFile
                        position = interp.position
                if source_file:
                    if position:
                        lineno = position[0] or 0
                    else:
                        lineno = 0
                    return source_file, lineno
        return None, None

    def getFrameNames(self, frame):
        """Returns the module and function name for the frame.
        """
        if frame.f_code.co_name == 'interpret':
            source_file, ln = self.getTALPosition(frame)
            if source_file:
                return '', source_file.split('/')[-1]
        try:
            modname = frame.f_globals['__name__']
        except KeyError:
            modname = ''
        funcname = frame.f_code.co_name
        return modname, funcname

    def isTraceable(self, frame):
        """Indicates whether the debugger should step into the given frame.

        Called often.
        """
        if self.scripts_only_mode:
            code = frame.f_code
            if isPythonScriptMetaType(code.co_filename):
                return 1
            if code.co_name == 'setPosition':
                if frame.f_globals.get('__name__') == TALES_MODULE_NAME:
                    # Trace calls to PageTemplate.TALES.Context.setPosition().
                    if not frame.f_locals.get('__traced'):
                        # Avoid getting called more than once.
                        frame.f_locals['__traced'] = 1
                        return 1
        return DebugServer.isTraceable(self, frame)

    def isAScriptFrame(self, frame):
        """Indicates whether the given frame is a high-level script frame.
        """
        code = frame.f_code
        if isPythonScriptMetaType(code.co_filename):
            return 1
        if code.co_name == 'interpret':
            source_file, ln = self.getTALPosition(frame)
            if source_file:
                return 1
        return 0

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

    def getFrameNamespaces(self, frame):
        """Returns the locals and globals for a frame.
        """
        code = frame.f_code
        if code.co_name == 'interpret':
            source_file, ln = self.getTALPosition(frame)
            if source_file:
                # This is a TAL interpret() frame.  Use special locals
                # and globals.
                interp = frame.f_locals.get('self')
                if interp is not None:
                    local_vars = getattr(interp.engine, 'local_vars', {})
                    global_vars = getattr(interp.engine, 'global_vars', {})
                    return global_vars, local_vars

        return frame.f_globals, frame.f_locals


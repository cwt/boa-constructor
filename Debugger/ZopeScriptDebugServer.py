from IsolatedDebugger import DebugServer

__traceable__ = 0


TAL_INTERP_MODULE_NAME = 'TAL.TALInterpreter'
TALES_MODULE_NAME = 'Products.PageTemplates.TALES'


isAPythonScriptMetaType = {
    'Script (Python)': 1,
    }.has_key


def isATALInterpeterFrame(frame):
    """Indicates whether the given frame should show up as a TAL frame.

    A TAL frame is a call to interpret() from the __call__(),
    do_useMacro(), or do_defineSlot() methods.  This depends a lot
    on specific code in TAL. :-(
    """
    if (frame.f_code.co_name == 'interpret' and
        frame.f_globals.get('__name__') == TAL_INTERP_MODULE_NAME):
        caller = frame.f_back
        if caller.f_globals.get('__name__') == TAL_INTERP_MODULE_NAME:
            caller_name = caller.f_code.co_name
            if caller_name in ('__call__', 'do_useMacro', 'do_defineSlot'):
                return 1
    return 0


class ZopeScriptDebugServer(DebugServer):
    """A debug server that facilitates debugging of Zope Python Scripts
    and Page Templates.
    """

    # scripts_only_mode is turned on to stop only in through-the-web scripts.
    scripts_only_mode = 0
    stack_extra = None

    def beforeResume(self):
        """Frees references before jumping back into user code."""
        DebugServer.beforeResume(self)
        self.stack_extra = None

    def getFilenameAndLine(self, frame):
        """Returns the filename and line number for the frame.  Invoked often.

        This implementation adjusts for Python scripts and page templates.
        """
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        # XXX Python scripts currently (Zope 2.5) use their meta type
        # as their filename.  This is efficient but brittle.
        if isAPythonScriptMetaType(filename):
            meta_type = filename
            # XXX This assumes the user never changes the "script" binding.
            script = frame.f_globals.get('script', None)
            if script is not None:
                url = script.absolute_url()
                url = url.split('://', 1)[-1]
                filename = 'zopedebug://%s/%s' % (url, meta_type)
                # Offset for Boa's purposes
                lineno = lineno + 1
                return filename, lineno

        if code.co_name == 'interpret' and isATALInterpeterFrame(frame):
            source_file, ln = self.getTALPosition(frame)
            if source_file:
                return self.TALSourceToURL(source_file, frame), ln

        return self.canonic(filename), lineno

    def TALSourceToURL(self, source_file, frame):
        if source_file.startswith('traversal:'):
            path = source_file[10:]
            if path.startswith('/'):
                path = path[1:]
            meta_type = 'Page Template'
            host = 'localhost:8080'  # XXX XXX!
            return 'zopedebug://%s/%s/%s' % (host, path, meta_type)
        elif source_file.startswith('/'):
            meta_type = 'Page Template'
            interp = frame.f_locals.get('self')
            if interp is not None:
                global_vars = getattr(interp.engine, 'global_vars', {})
                template = global_vars.get('template', None)
                if template:
                    url = template.absolute_url().split('://', 1)[-1]
                    return 'zopedebug://%s/Page Template'%url
        return source_file  # TODO: something better

    def getTALPosition(self, frame):
        """If the frame is in TALInterpreter.interpret(), detects what
        template was being interpreted and where, but only for specific
        interpreter frames.  Returns the source file and line number.
        """
        se = self.stack_extra
        if se:
            info = se.get(frame, None)
            if info:
                # Return the precomputed file and lineno.
                source_file, lineno = info
                return source_file, lineno

        # Inspect TAL frames.  XXX brittle in many ways.
        interp = frame.f_locals.get('self', None)
        source_file = interp.sourceFile
        position = interp.position
        if position:
            lineno = position[0] or 0
        else:
            lineno = 0
        return source_file, lineno

    def getFrameNames(self, frame):
        """Returns the module and function name for the frame.
        """
        if isATALInterpeterFrame(frame):
            source_file, ln = self.getTALPosition(frame)
            if source_file:
                return '', source_file.split('/')[-1]
        return DebugServer.getFrameNames(self, frame)

    def isTraceable(self, frame):
        """Indicates whether the debugger should step into the given frame.

        Called often.
        """
        if self.scripts_only_mode:
            code = frame.f_code
            if isAPythonScriptMetaType(code.co_filename):
                return 1
            if code.co_name == 'setPosition':
                if frame.f_globals.get('__name__') == TALES_MODULE_NAME:
                    # Trace calls to PageTemplate.TALES.Context.setPosition().
                    # Avoid stopping more than once per call.
                    if frame.f_lineno == frame.f_code.co_firstlineno:
                        return 1
            return 0
        return DebugServer.isTraceable(self, frame)

    def isAScriptFrame(self, frame):
        """Indicates whether the given frame is a high-level script frame.
        """
        if isAPythonScriptMetaType(frame.f_code.co_filename):
            return 1
        if isATALInterpeterFrame(frame):
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

        # Compute filenames and positions for TAL frames.
        # The source_file and position variables get applied to the
        # interpreter frame that called them.
        self.stack_extra = {}
        last_interp = None
        saved_source = None
        saved_lineno = None
        for idx in range(len(stack) - 1, -1, -1):
            frame, lineno = stack[idx]
            if isATALInterpeterFrame(frame):
                caller = frame.f_back
                caller_name = caller.f_code.co_name
                interp = frame.f_locals.get('self', None)
                if last_interp is interp:
                    self.stack_extra[frame] = (saved_source, saved_lineno)
                if caller_name in ('do_useMacro', 'do_defineSlot'):
                    # Using a macro or slot.
                    # Expect to find saved_source and saved_position in
                    # locals.
                    saved_source = caller.f_locals.get('prev_source') #saved_source
                    position = 0#caller.f_locals.get('saved_position')
                    if position:
                        saved_lineno = position[0] or 0
                    else:
                        saved_lineno = 0
                last_interp = interp

        return exc_type, exc_value, stack, frame_stack_len

    def afterBreakpoint(self, frame):
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
        if isATALInterpeterFrame(frame):
            # This is a TAL interpret() frame.  Use special locals
            # and globals.
            interp = frame.f_locals.get('self')
            if interp is not None:
                local_vars = getattr(interp.engine, 'local_vars', {})
                global_vars = getattr(interp.engine, 'global_vars', {})
                return global_vars, local_vars

        return frame.f_globals, frame.f_locals

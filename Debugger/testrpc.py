
import string, sys
from ExternalLib.xmlrpclib import Server, Transport

class TransportWithAuth (Transport):

    def request(self, host, handler, request_body):
	# issue XML-RPC request

	import httplib
	h = httplib.HTTP(host)
	h.putrequest("POST", handler)

	# required by HTTP/1.1
	h.putheader("Host", host)

	# required by XML-RPC
	h.putheader("User-Agent", self.user_agent)
	h.putheader("Content-Type", "text/xml")
	h.putheader("Content-Length", str(len(request_body)))

        h.putheader('x-auth',
                    '84637cf34613265706a9357df73a4d2c0ba74ca4')

	h.endheaders()

	if request_body:
	    h.send(request_body)

	errcode, errmsg, headers = h.getreply()

	if errcode != 200:
	    raise ProtocolError(
		host + handler,
		errcode, errmsg,
		headers
		)

	return self.parse_response(h.getfile())


from wxPython.wx import wxExecute, wxProcess, wxYield
from xmlrpc import xmlrpclib
import os, time

def package_home(globals_dict):
    __name__=globals_dict['__name__']
    m=sys.modules[__name__]
    if hasattr(m,'__path__'):
        r=m.__path__[0]
    elif "." in __name__:
        r=sys.modules[__name__[:rfind(__name__,'.')]].__path__[0]
    else:
        r=__name__
    if __name__ == '__main__':
        return os.getcwd()
    else:
        return os.path.join(os.getcwd(), r)

dsp = os.path.join(package_home(globals()), 'DebugServerProcess.py')
process = wxProcess()
##process.Redirect()
wxExecute('%s "%s"' % (sys.executable, dsp), 0, process)

##line = ''
##while string.find(line, '\n') < 0:
##    stream = process.GetInputStream()
##    if not stream.eof():
##        text = stream.read()
##        line = line + text
##    else:
##        wxYield()

##port, auth = string.split(string.strip(line))

port = 3245
s = xmlrpclib.Server('http://localhost:%s' % port)

time.sleep(5)

print s.runFileAndRequestStatus(
    os.path.join(package_home(globals()), 'test.py'), (), ())


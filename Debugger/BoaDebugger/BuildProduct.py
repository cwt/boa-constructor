import zipfile

boaSrcModules = [
      '__init__', 'IsolatedDebugger', 'RemoteServer', 'Tasks', 
      'ZopeScriptDebugServer']

productFiles = [
      'BoaDebugger.py', 'CHANGES', 'README', 'refresh.txt', 'version.txt', 
      '__init__.py', 'help/debugger.stx', 'www/boa.gif']

def main():
    zipped = zipfile.ZipFile('BoaDebuggerProduct.zip', 'w', zipfile.ZIP_DEFLATED)
    zipped.write('../__init__.py', 'BoaDebugger/Boa/ExternalLib/__init__.py')
    zipped.write('../../ExternalLib/xmlrpcserver.py', 
                'BoaDebugger/Boa/ExternalLib/xmlrpcserver.py')    

    for fn in boaSrcModules:
        zipped.write('../%s.py'%fn, 'BoaDebugger/Boa/%s.py'%fn)    

    for fn in productFiles:
        zipped.write(fn, 'BoaDebugger/'+fn)    

if __name__ == '__main__':
    main()        
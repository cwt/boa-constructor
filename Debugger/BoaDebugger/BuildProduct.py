import zipfile

boaSrcModules = [
      '__init__', 'IsolatedDebugger', 'RemoteServer', 'Tasks', 
      'ZopeScriptDebugServer']

productFiles = [
      'BoaDebugger.py', 'CHANGES', 'README', 'refresh.txt', 'version.txt', 
      '__init__.py', 'help/debugger.stx', 'www/boa.gif']

def main():
    zipped = zipfile.ZipFile('BoaDebuggerProduct.zip', 'w')
    zipped.write('../__init__.py', 'Boa/ExternalLib/__init__.py')
    zipped.write('../../ExternalLib/xmlrpcserver.py', 
                'Boa/ExternalLib/xmlrpcserver.py')    

    for fn in boaSrcModules:
        zipped.write('../%s.py'%fn, 'Boa/%s.py'%fn)    

    for fn in productFiles:
        zipped.write(fn, fn)    

if __name__ == '__main__':
    main()        
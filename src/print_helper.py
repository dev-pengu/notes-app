import tempfile
import os, platform
try:
    import win32api
    import win32print
except ImportError:
    import subprocess


class PrintHelper():

    _data = None

    def __init__(self, **kwargs):
        try:
            self._data = kwargs['data']
        except KeyError:
            pass

    def print(self):
        if self._data != None:
            if platform.system() == 'Windows':
                filename = tempfile.mktemp('.txt')
                file = open(filename, 'w')
                file.write(self._data)

                win32api.ShellExecute(
                    0,
                    'print',
                    filename,
                    '/d:"%s"' % win32print.GetDefaultPrinter(),
                    '.',
                    0
                )
                file.close()
            elif platform.system() == 'Linux' or platform.system() == 'Darwin':
                lpr = subprocess.Popen('/usr/bin/lpr', stdin=subprocess.PIPE)
                lpr.stdin.write(self._data)
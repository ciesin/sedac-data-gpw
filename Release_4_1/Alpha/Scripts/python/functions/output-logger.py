# output-logger.py
# for script logging purposes, uses a class found online
# defined print_and_log_msg()
# jsquires - 08/06/2015

import sys

class Tee(object):
    """
    Allow forking of output to stdout and other files
    From: http://stackoverflow.com/questions/11325019/output-on-the-console-and-file-using-python
    @author Thrustmaster <http://stackoverflow.com/users/227884/thrustmaster>
    @author Eric Cousineau <eacousineau@gmail.com>
    """
    def __init__(self, *files):
        self.files = files
    
    def open(self):
        """ Redirect stdout """
        if not hasattr(sys, '_stdout'):
            # Only do this once just in case stdout was already initialized
            # @note Will fail if stdout for some reason changes
            sys._stdout = sys.stdout
        sys.stdout = self
        return self

    def close(self):
        """ Restore """
        stdout = sys._stdout
        for f in self.files:
            if f != stdout:
                f.close()
        sys.stdout = stdout
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)

def print_and_log_msg(message, logfile):
    """
    Prints messages to stdout and logs it in the given file.
    """
    try:
        t = Tee(sys.stdout, open(logfile, 'a')).open()
        print message
        t.close()
    except:
        print "unable to add message to logfile"

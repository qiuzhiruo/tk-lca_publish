"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

"""

import sys
import os
import platform

from tank.platform import Application

# import os
# if os.getenv('USER') == "haojia":
#     import sys
#     sys.path.append("/home/haojia/Work/SoftWare/pycharm-2022.1.3/debug-eggs/pydevd-pycharm.egg_FILES/")
#     import pydevd_pycharm
#     import pydevd
#     pydevd.stoptrace()
#     pydevd_pycharm.settrace('localhost', port=1234, stdoutToServer=True, stderrToServer=True)

class AboutTank(Application):
    
    def init_app(self):
        """
        Called as the application is being initialized
        """
        # import using special tank import mechanism
        tk_lca_publish = self.import_module("tk_lca_publish")
        # create a callback to run when our command is launched.
        # pass the app object as a parameter.
        cb = lambda : tk_lca_publish.show_dialog(self)
        # add stuff to main menu
        self.engine.register_command("Publish", cb)

    

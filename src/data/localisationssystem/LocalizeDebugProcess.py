from src.templates.workerprocess import WorkerProcess
import numpy as np


from threading import Thread
class LocalizeDebugProcess(WorkerProcess):
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs):
        """Process used for sending images over the network to a targeted IP via UDP protocol 
        (no feedback required). The image is compressed before sending it. 

        Used for visualizing your raspicam images on remote PC.
        
        Parameters
        ----------
        inPs : list(Pipe) 
            List of input pipes, only the first pipe is used to transfer the captured frames. 
        outPs : list(Pipe) 
            List of output pipes (not used at the moment)
        """

        super(LocalizeDebugProcess,self).__init__( inPs, outPs)
        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(LocalizeDebugProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        localizeShowTh = Thread(name='LocalizeShowProcessThread',target = self._run)
        localizeShowTh.daemon = True
        self.threads.append(localizeShowTh)


    def _run(self):
      
     
        while True:
            try:
                # Obtain image
               
                for  inP in self.inPs:
                    print(inP.recv())

            except Exception as e:
                print("Localize show error:")
                print(e)


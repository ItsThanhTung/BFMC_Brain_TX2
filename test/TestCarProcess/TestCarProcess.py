import serial

from src.templates.workerprocess            import WorkerProcess
from src.perception.CarHandlerThread        import CarHandlerThread
from threading import Thread

class SerialHandlerProcess(WorkerProcess):

    # ===================================== INIT =========================================
    def __init__(self,inPs, outP):
        """The functionality of this process is to redirectionate the commands from the RemoteControlReceiverProcess (or other process) to the 
        micro-controller via the serial port. The default frequency is 256000 and device file /dev/ttyACM0. It automatically save the sent 
        commands into a log file, named historyFile.txt. 
        
        Parameters
        ----------
        inPs : list(Pipes)
            A list of pipes, where the first element is used for receiving the command to control the vehicle from other process.
        outPs : None
            Has no role.
        """
        super(SerialHandlerProcess,self).__init__(inPs, outP)
        
        self.__CarHandlerTh = CarHandlerThread(shInPs= inPs, shOutP= outP)
        self.__TestTh = Thread()
        

    
    def run(self):
        super(SerialHandlerProcess,self).run()


    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """ Initializes the read and the write thread.
        """
        self.threads.append(self.__CarHandlerTh)

from src.templates.threadwithstop import ThreadWithStop
from multiprocessing.connection import wait
class NucleoListener(ThreadWithStop):
    def __init__(self, inPs, outPs):
        """
    
    Car Handler Thread object

    Parameters
    -------------


    """
        self._inPs = inPs
        self._outPs = outPs
        super(NucleoListener,self).__init__()
    
    def run(self):
        reader = list()
        for key in self._inPs:
            reader.append(self._inPs[key])

        while(self._running):
            for inP in wait(reader):
                try:
                    mess = inP.recv()
                except:
                    print("Pipe Error ", inP)
                else:
                    if mess["action"] == "5":
                        data = self._SpeedParser(mess["data"])
                        self._outPs["SPEED"].send(data)
                    elif mess["action"] == "8":
                        data = self._VLXParser(mess["data"])
                        self._outPs["VLX"].send(data)
                    elif mess["action"] == "9":
                        data = self._TravelledParser(mess["data"])
                        self._outPs["TRAVELLED"].send(data)
    
    def _VLXParser(self, rawData):
        # print("VLX RawData ", rawData)
        return rawData
    
    def _SpeedParser(self, rawData):
        # print("Speed RawData ", rawData)
        return rawData
    
    def _TravelledParser(self, rawData):
        # print("Travelled RawData ", rawData)
        return rawData
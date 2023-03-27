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
                        # self._outPs["SPEED"].send(data)
                        print("Encoder Speed ", data)
                    elif mess["action"] == "8":
                        data = self._VLXParser(mess["data"])
                        # self._outPs["VLX"].send(data)
                    elif mess["action"] == "9":
                        data = self._TravelledParser(mess["data"])
                        print("TRavelled ", data)

    
    def _VLXParser(self, rawData):
        Data = rawData.split(";",4)
        try:
            DataInt = [int(i) for i in Data[:4]]
        except:
            return [0,0,0,0]
        return DataInt
    
    def _SpeedParser(self, rawData):
        # return 0
        # print("Speed RawData ",rawData)
        Status, Data = rawData.split(";",2)[:2]
        Status = int(Status)
        if Status == 0:
            return float(Data)
        else:
            return 0
    
    def _TravelledParser(self, rawData):
        return 0
        Status, Data = rawData.split(";",2)[:2]
        Status = int(Status)
        if Status == 0:
            return float(Data)
        else:
            return 0
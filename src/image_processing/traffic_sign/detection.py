import numpy as np
import torch

from src.image_processing.traffic_sign.yolov5_utils.utils.augmentations import letterbox
# from src.image_processing.traffic_sign.yolov5_utils.utils.plots import colors, save_one_box
from src.image_processing.traffic_sign.yolov5_utils.models.experimental import attempt_load
from src.image_processing.traffic_sign.yolov5_utils.utils.torch_utils import select_device
from src.image_processing.traffic_sign.yolov5_utils.models.common import DetectMultiBackend
from src.image_processing.traffic_sign.yolov5_utils.utils.general import non_max_suppression,scale_coords
# from src.image_processing.traffic_sign.yolov5_utils.utils.plots import Annotator, colors

from multiprocessing import Condition

class Yolo(object):
    def __init__(self, streamP, outP, debugP, debug, is_tensorRt, source='',\
                        imgsize= (640,640), device='0',conf_thres=0.1, iou_thres=0.1,max_det=1000): 
        
        if is_tensorRt: 
            weights = 'ver5_up.torchscript'
        else: 
            weights = 'ver5_up.torchscript'
            
        self.img_size = imgsize
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights, device=self.device, dnn=False, data='./src/image_processing/traffic_sign/yolov5_utils/data/coco128.yaml')
        self.model.model.float()
        for i in range(10):
            with torch.no_grad():            
                a_ = self.model(torch.zeros(1,3,640,640).to('cuda').type(torch.float), augment=False, visualize=False)
                # print(type(a_))
        self.names=['car', 'crosswalk', 'highway_entry', 'highway_exit', 'no_entry', 'parking', 'pedestrian', 'priority', 'roundabout', 'stop', 'red','yellow','green','roadblock','go_straight']
        self.conf_thres=conf_thres
        self.iou_thres=iou_thres
        self.max_det=max_det
        self._running = False 
        self.stride=64
        self.delay=True
        
        self.stream_image = None
        self.image = None
        self.streamP = streamP
        
        self.image_condition = Condition()
        self.image_stream_condition = Condition()
        
        self.outP = outP
        self.debug = debug
        self.debugP = debugP
        
        
    def detect(self,img0):
        # img0=self.image_loader()
        img_resized,img=self.preprocess(img0)
        img = torch.from_numpy(img).to(self.device)
        # img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img = img / 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None] 
        with torch.no_grad():            
            pred = self.model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, None, agnostic=True, max_det=self.max_det)
        results = [[],[],[]]
        boxes=[]
        confs=[]
        clss=[]
        for i, det in enumerate(pred):  # per image
            # annotator = Annotator(img_resized, line_width=3, example=str(self.names))
            det=det.cpu().detach().numpy()
            
            if len(det):
                # print(det)
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
                # print(img.shape, img0.shape)
                # print(det)
                for (*xyxy, conf, cls) in reversed(det): 
                    c = int(cls)  # integer class
                    label = f'{self.names[c]} {conf:.2f}'
                    # annotator.box_label(xyxy, label, color=colors(c, True))
                    boxes.append(xyxy)
                    confs.append(float(conf))
                    clss.append(self.names[c])
        results = [boxes, confs, clss]
        # print(results)
        return img_resized, results
    
    def read_image(self):
        while True:
            try:
                data = self.streamP.recv()["image"]
                self.image_condition.acquire()
                self.image = data
                self.image_condition.notify()
                self.image_condition.release()
                
            except Exception as e:
                print("Object detection read_image error:", e)
                
    def stream_image_th(self):
        while True:
            try:
                self.image_stream_condition.acquire()
                if self.stream_image is None:
                    self.image_stream_condition.wait()
                    stream_image = self.stream_image
                    self.stream_image = None
                    self.image_stream_condition.release()
                else:
                    stream_image = self.stream_image
                    self.stream_image = None
                    self.image_stream_condition.release()
                    
                if self.debug == True:        
                    self.debugP.send({"image": stream_image})
                
            except Exception as e:
                print("Object detection stream_image error:", e)

    def detection_loop(self):
        while True:
            if True:
                self.image_condition.acquire()
                if self.image is None:
                    self.image_condition.wait()
                    image = self.image
                    self.image = None
                    self.image_condition.release()
                else:
                    image = self.image
                    self.image = None
                    self.image_condition.release()
                    
                if self.debug == True:  
                    self.image_stream_condition.acquire()
                    self.stream_image = image
                    self.image_stream_condition.notify()
                    self.image_stream_condition.release()
                    
                _, results = self.detect(image)
                self.outP.send({"results" : results})
                
                    
            # except Exception as e:
            #     print("Object detection detection_loop error:", e)

    def preprocess(self,img0):
        img_resized = letterbox(img0, self.img_size, stride=self.stride, auto=False)[0]
        img = img_resized.transpose((2, 0, 1))[::-1] 
        img = np.ascontiguousarray(img)
        return img_resized,img
    
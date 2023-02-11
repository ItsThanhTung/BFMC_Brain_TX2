import numpy as np
import torch

from src.image_processing.traffic_sign_remote.yolov5_utils.utils.augmentations import letterbox
from src.image_processing.traffic_sign_remote.yolov5_utils.models.experimental import attempt_load
from src.image_processing.traffic_sign_remote.yolov5_utils.utils.torch_utils import select_device
from src.image_processing.traffic_sign_remote.yolov5_utils.models.common import DetectMultiBackend
from src.image_processing.traffic_sign_remote.yolov5_utils.utils.general import non_max_suppression,scale_coords
from src.image_processing.traffic_sign_remote.yolov5_utils.utils.plots import Annotator, colors, save_one_box

from multiprocessing import Condition

class Yolo(object):
    def __init__(self, streamP, outP, is_tensorRt, source='',\
                        imgsize= (480,640), device='0',conf_thres=0.1, iou_thres=0.45,max_det=1000): 
        
        if is_tensorRt: 
            weights='sign2.engine'
        else: 
            weights='sign2.pt'
            
        self.img_size = imgsize
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights, device=self.device, dnn=False, data='./src/image_processing/traffic_sign/yolov5_utils/data/coco128.yaml')
        self.names=['car', 'crosswalk', 'highway_entry', 'highway_exit', 'no_entry', 'onewayroad', 'parking', 'pedestrian', 'priority', 'roadblock', 'roundabout', 'stop', 'trafficlight']
        self.conf_thres=conf_thres
        self.iou_thres=iou_thres
        self.max_det=max_det
        self._running = False 
        self.stride=64
        self.delay=True
        self.image = None
        self.streamP = streamP
        self.image_condition = Condition()
        self.outP = outP

    
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
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, None, False, max_det=self.max_det)
        results=[]
        for i, det in enumerate(pred):  # per image
            # annotator = Annotator(img_resized, line_width=3, example=str(self.names))
            det=det.cpu().detach().numpy()
            if len(det):
                # det[:, :4] = scale_coords(im.shape, det[:, :4], im0.shape).round()
                for (*xyxy, conf, cls) in reversed(det): 
                    c = int(cls)  # integer class
                    label = f'{self.names[c]} {conf:.2f}'
                    # annotator.box_label(xyxy, label, color=colors(c, True))
                    result = (xyxy, conf, self.names[c])
                    results.append(result)
            # img_resized = annotator.result()
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

    def detection_loop(self):
        while True:
            try:
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

                visualized_image, results = self.detect(image)
                
                print(results)
                
                if self.outP == True:        
                    self.outP.send({"image": visualized_image})
                    
            except Exception as e:
                print("Object detection detection_loop error:", e)

    def preprocess(self,img0):
        img_resized = letterbox(img0, self.img_size, stride=self.stride, auto=False)[0]
        img = img_resized.transpose((2, 0, 1))[::-1] 
        img = np.ascontiguousarray(img)
        return img_resized,img
    
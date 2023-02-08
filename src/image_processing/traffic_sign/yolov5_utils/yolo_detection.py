import argparse
import os
import sys
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
import base64
import json
from datetime import datetime
import requests
import threading
import queue
import time
import numpy as np


class YoloV5(object):
    def __init__(self,weights='/home/tx2jp462/Downloads/s_640.engine', device='', conf_thres=0.25, iou_thres=0.45,max_det=1000): 
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights, device=self.device, dnn=False, data=ROOT / 'data/coco128.yaml')
        
        self.names=[
            'person',
            'motorbike',
            'bicycle',
            'face',
            'plate',
            'longplate',
            'car',
            'truck',
            'van',
            'bus',
            'bagac']
        self.img_size = 640
        self.stride = int(self.model.stride)
        self.half=False
        self.conf_thres=conf_thres
        self.iou_thres=iou_thres
        self.max_det=max_det
        self.visualize=False
        self.c_processed_frame  = threading.Condition()  
        self.processed_backbone_buffer   = queue.Queue(maxsize=5)
        
        
    def detect(self,img0):
        img0,img=self.preprocess(img0)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img = img / 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None] 
        with torch.no_grad():
            print(img.size())
            st=time.time()
            pred = self.model(img, augment=False, visualize=False)
            print("infer time :",time.time()-st)
        im0,results=self.postprocess(pred,img0,img)
        if len(results)>0:
            self.processed_backbone_buffer.put((cv2.resize(im0,(int(im0.shape[1]/2),int(im0.shape[0]/2))),results)) 
            if self.processed_backbone_buffer.full():
                self.processed_backbone_buffer.get()
            with self.c_processed_frame:
                # print("size :",self.processed_backbone_buffer.qsize())
                if (self.processed_backbone_buffer.qsize() >= 1):
                    self.c_processed_frame.notifyAll()
        return im0, results

    def postprocess(self,pred,im0s,img):
        # print(pred[0].size())
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, None, False, max_det=self.max_det)
        # print(len(pred),"----------")
        results=[]
        for i, det in enumerate(pred):  # per image
            # print(det.size())
            im0= im0s.copy()
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if self.visualize:
                annotator = Annotator(im0, line_width=3, example=str(self.names))
            
            if len(det):
                # print(len(det))
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                for *xyxy, conf, cls in reversed(det):
                    if self.visualize:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = (f'{self.names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                    line = (cls, *xywh)
                    results.append(str(('%g ' * len(line)).rstrip() % line))
        
            if self.visualize:  
                im0 = annotator.result()
        # print(results) 
        return im0,results
    
    def preprocess(self,img0):
        img = letterbox(img0, self.img_size, stride=self.stride, auto=False)[0]
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)
        return img0,img
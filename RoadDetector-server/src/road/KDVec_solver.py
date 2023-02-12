import os

import torch
import cv2
import yaml

from .KDVec.model.KDVec import KDVec
from .KDVec.patch_based_inference import patch_inference
from .aug_cfg import test_aug


class KDVec_Solver:
    def __init__(self, image_path, save_types, gpu):
        if gpu == "cpu":
            self.device = torch.device("cpu")
        else:
            self.device = torch.device("cuda", gpu)
        with open('./road/KDVec/config.yaml', 'r') as cfg_file:
            self.config = yaml.load(cfg_file, Loader=yaml.FullLoader)
   
        self.save_types = save_types
        self.image_path = image_path
        # model
        self.model = KDVec(in_channel=3, backbone='hr-w48').to(self.device)
        checkpoint = torch.load("./road/trained_model/KDVec.pt")
        self.model.load_state_dict(checkpoint['net'])
        self.model.eval()
    
    def inference(self):
        # road detect
        data = cv2.imread(os.path.join(self.image_path, os.listdir(self.image_path)[0]))
        data = test_aug()(data).unsqueeze(0)  
        _, pred_graphs, _, _ = patch_inference(data.to(self.device), self.model, self.config)
        
        # road vis
        image = cv2.imread(os.path.join(self.image_path, os.listdir(self.image_path)[0]))
        graph = pred_graphs[0]
        for node_1, node_2 in graph.edges():
            cv2.line(image, node_1, node_2, color=(48, 126, 241), thickness=3)
        for node in graph.nodes():
            cv2.circle(image, node, radius=5, color=(75, 238, 251), thickness=-1)
        
        cv2.imwrite(os.path.join(self.image_path, "vec_vis.png"), image)
        return 

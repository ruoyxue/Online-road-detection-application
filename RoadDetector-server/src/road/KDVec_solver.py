import os

import torch
import cv2
import yaml
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .KDVec.model.KDVec import KDVec
from .KDVec.patch_based_inference import patch_inference
from .aug_cfg import test_aug
from .KDVec.globe_vars import progress


device = None
config = None
geojson = None
model = None

async def deploy_KDVec(gpu):
    global device, config, geojson, model
    device = torch.device("cuda", gpu)
    with open('./road/KDVec/config.yaml', 'r') as cfg_file:
        config = yaml.load(cfg_file, Loader=yaml.FullLoader)
    geojson = None

    # model
    loop = asyncio.get_running_loop()
    newexecutor = ThreadPoolExecutor()
    model = await loop.run_in_executor(newexecutor, deploy_model)
    

def deploy_model():
    model = KDVec(in_channel=3, backbone='hr-w48').to(device)
    checkpoint = torch.load("./road/trained_model/KDVec.pt", map_location=device)
    model.load_state_dict(checkpoint['net'])
    model.eval()
    return model


def inference_KDVec(image_path, northwest_lnglat, southeast_lnglat):
    global device, config, geojson, model
    # road detect
    geojson = None
    progress.set_value(0)

    data = cv2.imread(os.path.join(image_path, os.listdir(image_path)[0]))
    mean = (89.12, 95.82, 93.76)
    std = (46.42, 46.20, 50.23)
    data = normalise(data, mean, std).unsqueeze(0).to(device)
    pred_graphs =  patch_inference(data, model, config)
    
    # road vis
    image = cv2.imread(os.path.join(image_path, os.listdir(image_path)[0]))
    graph = pred_graphs[0]
    geojson = graph_to_geojson(
        graph=graph, image_shape=image.shape[:2],
        northwest_lnglat=northwest_lnglat,
        southeast_lnglat=southeast_lnglat
    )

    progress.set_value(1)
    with open(os.path.join(image_path, 'road.geojson'), 'w', encoding='utf-8') as fw:
        json.dump(geojson, fw, indent=4, ensure_ascii=False)

    for node_1, node_2 in graph.edges():
        cv2.line(image, node_1, node_2, color=(48, 126, 241), thickness=3)
    for node in graph.nodes():
        cv2.circle(image, node, radius=5, color=(75, 238, 251), thickness=-1)
    cv2.imwrite(os.path.join(image_path, "vec_vis.png"), image)
    
    return 


def show_graph_KDVec():
    global geojson
    return geojson

def graph_to_geojson(graph, northwest_lnglat, southeast_lnglat, image_shape):
    """ Simplify graph using rdp """
    def rowcol2latlon(row, col, min_Lat, min_Lon, max_Lat, max_Lon, image_shape):
        max_row, max_col = image_shape[:2]
        lon = (col / max_col) * (max_Lon - min_Lon) + min_Lon
        lat = (row / max_row) * (max_Lat - min_Lat) + min_Lat
        return lat, lon

    feature_list = []
    min_Lat = northwest_lnglat[1]
    min_Lon = northwest_lnglat[0]
    max_Lat = southeast_lnglat[1]
    max_Lon = southeast_lnglat[0]

    for node_A, node_B in graph.edges():
        lat_A, lon_A = rowcol2latlon(node_A[1], node_A[0], min_Lat, min_Lon, max_Lat, max_Lon, image_shape)
        lat_B, lon_B = rowcol2latlon(node_B[1], node_B[0], min_Lat, min_Lon, max_Lat, max_Lon, image_shape)

        feature_list.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon_A, lat_A], [lon_B, lat_B]]
            }
        })

        feature_list.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon_A, lat_A]
            }
        })

        feature_list.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon_B, lat_B]
            }
        })

    geojson_dict = {
        "type": "FeatureCollection",
        "features": feature_list
    }

    return geojson_dict


def normalise(image, mean, std):
    """
    Normalise data using mean and std

    Args:
        image (np.array)
        mean, std (Tuple): B G R
    """
    image = torch.Tensor(image)
    for i in range(len(mean)):
        image[:, :, i] = (image[:, :, i] - mean[i]) / std[i]
    image = image.permute(2, 0, 1)
    return image

import os
import shutil

import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from fastapi import APIRouter, Path, Query, HTTPException, BackgroundTasks
from typing import Optional, List, Union, Dict
from pydantic import BaseModel, Field
from starlette import status
from uuid import UUID, uuid4

from .KDVec_solver import deploy_KDVec, inference_KDVec, show_graph_KDVec
from .KDVec.globe_vars import progress

road_router = APIRouter()
model_name = None

class DeployModelInfo(BaseModel):
    """ Request body for model deployment """
    model_name: str = Field(..., description="model to deploy")
    gpu: int = Field(..., description="where to deploy model")


class DetectionInfo(BaseModel):
    """ Request body for road detection """
    image_path: str
    northwest_lnglat: List[float]
    southeast_lnglat: List[float]

class DeleteInfo(BaseModel):
    """ Request body for delete save directory """
    save_dir: str


class RenameInfo(BaseModel):
    """ Request body for rename save directory """
    old_name: str
    new_name: str


@road_router.post("/deploy_model", status_code=status.HTTP_200_OK)
async def deploy_model(model_deploy_info: DeployModelInfo):
    if model_deploy_info.model_name == 'KDVec':
        await deploy_KDVec(model_deploy_info.gpu)
        global model_name
        model_name = 'KDVec'
    return


@road_router.post("/start_detect", status_code=status.HTTP_200_OK)
def start_detect(info: DetectionInfo, background_tasks: BackgroundTasks):
    global model_name
    if model_name == 'KDVec':
        background_tasks.add_task(inference_KDVec, info.image_path, info.northwest_lnglat, info.southeast_lnglat)
    return


@road_router.get("/get_progress", status_code=status.HTTP_200_OK)
def get_progress():
    return progress.get_value()


@road_router.get("/show_graph", status_code=status.HTTP_200_OK)
def show_graph():
    global model_name
    if model_name == 'KDVec':
        return show_graph_KDVec()
    return


@road_router.put("/delete_layer", status_code=status.HTTP_200_OK)
def delete_layer(info: DeleteInfo):
    shutil.rmtree(path=os.path.join("./road/save_dir", info.save_dir))
    return 


@road_router.put("/rename_layer", status_code=status.HTTP_200_OK)
def rename_layer(info: RenameInfo):
    os.rename(os.path.join('./road/save_dir', info.old_name),
              os.path.join('./road/save_dir', info.new_name))
    return

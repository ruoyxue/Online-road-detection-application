from fastapi import APIRouter, Path, Query, HTTPException
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from starlette import status

from .KDVec_solver import KDVec_Solver

road_router = APIRouter()
solver = None


class DeployModelInfo(BaseModel):
    """ Request body for model deployment """
    model_name: str = Field(..., description="model to deploy")
    save_types: List[str]
    image_path: str
    gpu: Union[int, str] = Field(..., description="where to deploy model")


@road_router.post("/deploy_model", status_code=status.HTTP_200_OK)
def deploy_model(model_deploy_info: DeployModelInfo):
    global solver
    # try:
    if model_deploy_info.model_name == 'KDVec':
        solver = KDVec_Solver(
            save_types=model_deploy_info.save_types,
            image_path=model_deploy_info.image_path,
            gpu=model_deploy_info.gpu
        )
    # except:
    #     raise HTTPException(status_code=422, detail="Cannot deploy model on gpu/cpu")
    
    return

@road_router.post("/road_detect", status_code=status.HTTP_200_OK)
def road_detect():
    global solver
    solver.inference()
    return

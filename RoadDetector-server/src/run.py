"""
 @Author: Ruoyao
 @Email: ruoyao.xue@whu.edu.cn
 @DateTime: 2022.12.20
 @SoftWare: Road Detector
 @License: GPLv2, see License for full text
"""
import os

import uvicorn
import multiprocessing
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from common import tile_download_router, tile_splice_router
from road import road_router

app = FastAPI(title='Road Detector Docs')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #允许进行跨域请求的来源列表，*作为通配符
    allow_credentials=True,  #跨域请求支持cookie，默认为否
    allow_methods=["*"],  #允许跨域请求的HTTP方法
    allow_headers=["*"],  #允许跨域请求的HTTP头列表
)

# app.mount(path='/road/static', app=StaticFiles(directory='./road/static'), name='road static')

app.include_router(tile_download_router, prefix='/tile_download', tags=['download image tiles'])
app.include_router(tile_splice_router, prefix='/tile_splice', tags=['splice image tiles'])
app.include_router(road_router, prefix="/road", tags=["road detect"])

if __name__ == "__main__":
    uvicorn.run('run:app', host='127.0.0.1', port=8000, reload=True, debug=True, workers=4)

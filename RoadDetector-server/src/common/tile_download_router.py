import os
import socket
import ssl
import urllib.request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette import status

tile_download_router = APIRouter()


class TileDownloadInfo(BaseModel):
    """ Request body for tile download """
    download_url: str = Field(..., description="where to download")
    save_dir: str = Field(..., description="save directory")
    save_tile_name: str = Field(..., description="save image name")
    x: int = Field(ge=0, description="column coordinate")
    y: int = Field(ge=0, description="row coordinate")
    z: int = Field(ge=0, description="tile zoom level")
    time_out: float = Field(default=5, ge=0, description="time span in seconds for re-download")

    @staticmethod
    def makeQuadKey(tile_x: int, tile_y: int, level: int) -> str:
        """ Compute a unique quad key for a given tile and level"""
        quad_key = ""
        for i in range(level):
            bit = level - i
            digit = ord('0')
            mask = 1 << (bit - 1)  # if (bit - 1) > 0 else 1 >> (bit - 1)
            if (tile_x & mask) != 0:
                digit += 1
            if (tile_y & mask) != 0:
                digit += 2
            quad_key += chr(digit)
        return quad_key


@tile_download_router.post("/", status_code=status.HTTP_200_OK)
def download_tile(tile_download_info: TileDownloadInfo):
    """ Downloads a single tile from url """
    # download specific tile url w.r.t tile_info
    replaceMap = {
        "x": str(tile_download_info.x),
        "y": str(tile_download_info.y),
        "z": str(tile_download_info.z),
        "quad": TileDownloadInfo.makeQuadKey(tile_download_info.x, tile_download_info.y, tile_download_info.z)
    }

    for key, value in replaceMap.items():
        newKey = str("{" + str(key) + "}")
        url = tile_download_info.download_url.replace(newKey, value)
    # monkey patching SSL certificate issue, DONT use it in a prod/sensitive environment
    ssl._create_default_https_context = ssl._create_unverified_context

    os.makedirs(tile_download_info.save_dir, exist_ok=True)    
    socket.setdefaulttimeout(tile_download_info.time_out)
    save_path = os.path.join(tile_download_info.save_dir, tile_download_info.save_tile_name)
    auto_down(url=url, save_path=save_path)
    return


def auto_down(url: str, save_path: str):
    """
    Download the tile from url repeatedly until success

    Args:
        url (str): url of the tile to download
        save_path (str): path to save the downloaded tile
    """
    try:
        urllib.request.urlretrieve(url, save_path)
    except socket.timeout:
        auto_down(url, save_path)
        print("download timeout, re-downloading")
    except urllib.request.ContentTooShortError:
        auto_down(url, save_path)
        print("download error, re-downloading")
    except urllib.error.URLError:
        auto_down(url, save_path)
        print("url error, network is unreachable, re-downloading")

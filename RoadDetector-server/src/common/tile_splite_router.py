import os
import socket
import ssl
import urllib.request
import numpy as np

from fastapi import APIRouter
from pydantic import BaseModel, Field
from starlette import status
import cv2

tile_splice_router = APIRouter()


class TileSpliceInfo(BaseModel):
    """ Request body for tiles splice """
    save_tile_dir: str = Field(..., description="save image tiles directory")
    save_name: str = Field(..., description="save image name")


@tile_splice_router.post("/", status_code=status.HTTP_200_OK)
def splice_tile(tile_splice_info: TileSpliceInfo):
    """ splice tiles """
    image = paste_image_patches(tile_splice_info.save_tile_dir)
    cv2.imwrite(os.path.join(tile_splice_info.save_tile_dir, tile_splice_info.save_name), image)
    return


def paste_image_patches(image_patch_path):
	patch_loc_name_dict = {}
	row_list = []
	col_list = []
	for image_name in os.listdir(image_patch_path):
		col, row = image_name.split("-")[:2]
		row = int(float(row))
		col = int(float(col))
		row_list.append(row)
		col_list.append(col)
		patch_loc_name_dict[(row, col)] = image_name

	patch_height, patch_width, _ = cv2.imread(os.path.join(image_patch_path, patch_loc_name_dict[list(patch_loc_name_dict.keys())[0]])).shape
	
 	# find the shape of large image
	min_row_index, max_row_index = min(row_list), max(row_list)
	min_col_index, max_col_index = min(col_list), max(col_list)
	large_image_shape = ((max_row_index - min_row_index + 1) * patch_height,
							(max_col_index - min_col_index + 1) * patch_width, 3)
	large_image = np.zeros(large_image_shape, dtype=np.uint8)

	# map patches on large image
	for row, col in patch_loc_name_dict.keys():
		patch_image = cv2.imread(os.path.join(image_patch_path, patch_loc_name_dict[(row, col)]))
		new_row = row - min_row_index
		new_col = col - min_col_index
		large_image[new_row * patch_height: (new_row + 1) * patch_height,
					new_col * patch_width: (new_col + 1) * patch_width, :] = patch_image
	for file in os.listdir(image_patch_path):
		os.remove(os.path.join(image_patch_path, file))

	return large_image
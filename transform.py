import argparse
import json
import os
from glob import glob
from typing import List

import cv2
import dacite
import numpy as np

from data import Annotation, Rectangle, Coordinate
from utils import get_coord_tuple, get_rectangle_array, get_coord_array

BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
PINK = (203, 192, 255)
ORANGE = (0, 165, 255)

# A4画像サイズが height: 297mm, width: 210mmであることを考慮
BUFFER = 300
REAL_COORD_INFO = {
    "lower_left": {
        "x": 0+BUFFER,
        "y": 0+BUFFER
    },
    "lower_right": {
        "x": 891+BUFFER,
        "y": 0+BUFFER
    },
    "upper_right": {
        "x": 891+BUFFER,
        "y": 630+BUFFER
    },
    "upper_left": {
        "x": 0+BUFFER,
        "y": 630+BUFFER
    }
}
REAL_COORD = dacite.from_dict(
    data_class=Rectangle,
    data=REAL_COORD_INFO
)

def write_point(img: np.ndarray, ann: Annotation, output_path: str, circle_size: int = 40, thickness: int = 3) -> None:
    img_ = img.copy()
    cv2.circle(img_, get_coord_tuple(ann.paper.lower_left), circle_size, BLUE, thickness)
    cv2.circle(img_, get_coord_tuple(ann.paper.lower_right), circle_size, BLUE, thickness)
    cv2.circle(img_, get_coord_tuple(ann.paper.upper_right), circle_size, BLUE, thickness)
    cv2.circle(img_, get_coord_tuple(ann.paper.upper_left), circle_size, BLUE, thickness)
    cv2.circle(img_, get_coord_tuple(ann.pink_pen), circle_size, PINK, thickness)
    cv2.circle(img_, get_coord_tuple(ann.yellow_pen), circle_size, YELLOW, thickness)
    cv2.circle(img_, get_coord_tuple(ann.orange_pen), circle_size, ORANGE, thickness)
    cv2.imwrite(output_path, img_)

def transform(coord: Coordinate, transform_matrix: np.ndarray) -> Coordinate:
    coord = np.append(get_coord_array(coord), 1.0)
    coord = np.dot(transform_matrix, coord)
    transformed_coord = coord / coord[2]
    return Coordinate(x=int(transformed_coord[0]), y=int(transformed_coord[1]))

def transform_coord(ann: Annotation, transform_matrix: np.ndarray) -> Annotation:
    lower_left = transform(ann.paper.lower_left, transform_matrix)
    lower_right = transform(ann.paper.lower_right, transform_matrix)
    upper_right = transform(ann.paper.upper_right, transform_matrix)
    upper_left = transform(ann.paper.upper_left, transform_matrix)
    yellow_pen = transform(ann.yellow_pen, transform_matrix)
    pink_pen = transform(ann.pink_pen, transform_matrix)
    orange_pen = transform(ann.orange_pen, transform_matrix)
    return Annotation(
        paper=Rectangle(
            lower_left=lower_left,
            lower_right=lower_right,
            upper_right=upper_right,
            upper_left=upper_left
        ),
        yellow_pen=yellow_pen,
        pink_pen=pink_pen,
        orange_pen=orange_pen
    )

def main(img_path_list: List[str], annotation_path_list: List[str], output_dir: str) -> None:
    for i, (img_path, json_path) in enumerate(zip(img_path_list, annotation_path_list), start=1):
        img = cv2.imread(img_path)
        ann = read_csv(json_path)
        output_src_path = os.path.join(output_dir, f"src_img_{str(i).zfill(2)}.jpg")
        write_point(img, ann, output_src_path)
        transform_matrix = cv2.getPerspectiveTransform(get_rectangle_array(ann.paper), get_rectangle_array(REAL_COORD))
        transformed_img = cv2.warpPerspective(img, transform_matrix, get_coord_tuple(REAL_COORD.upper_right, buffer=BUFFER))
        transformed_ann = transform_coord(ann, transform_matrix)
        output_dst_path = os.path.join(output_dir, f"dst_img_{str(i).zfill(2)}.jpg")
        write_point(transformed_img, transformed_ann, output_dst_path, circle_size=20, thickness=2)

def read_csv(path) -> Annotation:
    with open(path, mode="r") as f:
        data = json.load(f)
        ann = dacite.from_dict(
            data_class=Annotation,
            data=data
        )
    return ann

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="./homography")
    parser.add_argument("--output_dir", default="./output")
    args = parser.parse_args()

    img_path_list = sorted(glob(os.path.join(args.input_dir, "**", "*.jpg"), recursive=True))
    annotation_path_list = sorted(glob(os.path.join(args.input_dir, "**", "*.json"), recursive=True))
    main(img_path_list, annotation_path_list, args.output_dir)
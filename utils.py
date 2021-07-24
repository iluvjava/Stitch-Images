import cv2
from os import walk
import numpy as np
import os
from typing import List
import matplotlib.pyplot as plt
from pathlib import Path
from fpdf import FPDF

NumericImg = List[np.ndarray]
MEDIA_IMAGE_POSTFIX = ["png", "jpg", "jpeg", "tiff", "bmp"]
OUTPUT_FOLDER = "out"  # this folder is ignored during scanning.


def ReadImage(filename:str) -> np.ndarray:
    """
        read image from a specified file.
    :param filename:
        The name of the file, path can be included.
    :param mode:
        The reading mode, an ENUM under cv2.
    :return:
        read image, it's gonna be a ndarray type from numpy
    """
    im = cv2.imread(filename)
    return im


def SaveAsImage(filenamepath:str, image:np.ndarray):
    cv2.imwrite(filenamepath, image)


def FilterOutImages(path:str, topdown=False):
    for root, dirs, files in walk(path, topdown=topdown):
        dirs[:] = [d for d in dirs if d != OUTPUT_FOLDER] # ignore output folders
        Filtered = [f for f in files if f.split(".")[-1] in MEDIA_IMAGE_POSTFIX]
        if len(Filtered) != 0:
            yield f"{root}\\", Filtered


def ConcateImageArray(images:NumericImg)-> np.ndarray:
    MaximalWidth = -float("inf")
    TotalHeight = 0
    for Img in images:
        TotalHeight += Img.shape[0]
        MaximalWidth = max(Img.shape[1], MaximalWidth)
    BigImg = np.zeros((TotalHeight, MaximalWidth, 3), dtype=np.uint8)
    s = 0  # accumulate heights
    for Img in images:
        h, w, _ = Img.shape
        BigImg[s: s + h, :w,...] = Img[:, :, ...]
        s += h
    return BigImg


def test():
    StitchedFiles = []   # dir to image content.
    for root, files in FilterOutImages(r"C:\Users\victo\Desktop\MLP\Spacpone Apogee\Issue1"):
        files = sorted(files)
        NpArrays = [ReadImage(f"{root}{f}") for f in files]
        StitchedFiles.append((root, ConcateImageArray(NpArrays)))
    plt.imshow(StitchedFiles[-1][-1])
    plt.show()
    for FilePath, ndarr in StitchedFiles:
        Dir = f"{FilePath}out"
        Path(Dir).mkdir(parents=True, exist_ok=True)
        SaveAsImage(f"{Dir}\\out.png", ndarr)


if __name__ == "__main__":
    test()
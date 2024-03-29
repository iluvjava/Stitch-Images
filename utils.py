import cv2
from os import walk
import numpy as np
import os
from typing import List, Iterable
import matplotlib.pyplot as plt
from pathlib import Path
from fpdf import FPDF
import re


NumericImg = List[np.ndarray]
MEDIA_IMAGE_POSTFIX = ["png", "jpg", "jpeg"]
OUTPUT_FOLDER = "out"  # this folder is ignored during scanning.


class NumericalFileName:
    """
        File names that has numerics in it, this is for custom comparison in
        python sort function.
        1. split the string into list of numerical parts and non numerical parts.

    """
    By = 1 # 1, numerics, else, string

    def __init__(this, filename:str):
        this.FileName = filename
        Splitted = re.split(r"(\d+)", filename)
        this.FileNameStringParts = [item for item in Splitted if not item.isnumeric()]
        this.FileNameNumerics = [int(item) for item in Splitted if item.isnumeric()]


    def __lt__(this, other):
        if NumericalFileName.By == 1:
            return this.FileNameNumerics < other.FileNameNumerics
        else:
            return this.FileNameStringParts < other.FileNameStringParts

    def __eq__(this, other):
        return this.FileName == other.FileName

    def __gt__(this, other):
        if this < other:
            return False
        if this == other:
            return False
        return True

    def __repr__(this):
        return str(this.FilenameSplit)


def SortedNumericalFileNames(filenames:Iterable[str]):
    """
        Given a list of file names that has random type of structures
        with numerics in it, this function sorts all the filenames that
        have the same structure using the numerical part of the file name.
    :param filenames:
        an iterable of file names
    :return:
        The sorted list of file names, in string
    """
    ToSort = [NumericalFileName(item) for item in filenames]
    NumericalFileName.By = 0
    ToSort.sort()
    NumericalFileName.By = 1
    ToSort.sort()
    return [item.FileName for item in ToSort]



def ReadImage(filename:str) -> np.ndarray:
    """
        read image from a specified file.
    :param filename:
        The name of the file, path can be included.
    :param mode:
        The reading mode, an ENUM under cv2.
    :return:
        read image, it's gonna be a ndarray type from numpy,
        None if there is something wrong, not exception will be thrown.
    """
    im = cv2.imread(filename)
    return im


def SaveAsImage(filenamepath:str, image:np.ndarray):
    """
        Saves the image as a file,
        - if sub directory or director doesn't exist,
        it will mkdir for you.
        - if file already exists, it will override it for you.

    :param filenamepath:
        The path of the file
    :param image:
        The image to save
    :return:
        Nothing
    """
    Path(filenamepath).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(filenamepath, image)


def FilterOutImages(path:str, depth=float("inf")):
    """
        Given the path, to a folder, filter out all the images.
    :param path:
        string, path to a folder. with `\` and ends with `\`
    :param depth:
        from the top level, it will only goes a certain depth into the
        directory tree.
    :return:
        It yields, not return.
    """
    Depth = depth
    for root, dirs, files in walk(path, topdown=True):
        if Depth == 0:
            dirs[:] = [] # block all sub director at this level.
        dirs[:] = [d for d in dirs if d != OUTPUT_FOLDER] # ignore output folders
        Filtered = [f for f in files if f.split(".")[-1] in MEDIA_IMAGE_POSTFIX]
        Filtered = SortedNumericalFileNames(Filtered)
        if len(Filtered) != 0:
            yield f"{root}", Filtered
        Depth -= 1


def ConcateImageArray(images:NumericImg)-> np.ndarray:
    """
        Given a list of mumpy images, it stitch all of them vertically
        together into one big image.
    :param images:
        a list of nd array of all the images.
    :return:
        numpy array of the stitched image.
    """
    MaximalWidth = -float("inf")
    TotalHeight = 0
    for Img in images:
        TotalHeight += Img.shape[0]
        MaximalWidth = max(Img.shape[1], MaximalWidth)
    BigImg = np.zeros((TotalHeight, MaximalWidth, 3), dtype=np.uint8)
    s = 0  # accumulate heights
    for Img in images:
        h, w, _ = Img.shape
        BigImg[s: s + h, :w, ...] = Img[:, :, ...]
        s += h
    return BigImg


def PathJoin(baseDir:str, fileName:str):
    return os.path.join(baseDir, fileName)


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
from utils import ReadImage, SaveAsImage, ConcateImageArray, FilterOutImages
from pathlib import Path
from fpdf import FPDF
from tqdm import tqdm
from PIL import Image, ExifTags

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def warn(mesg:str):
    print(bcolors.WARNING + mesg + bcolors.ENDC)


class Images:
    """
        For getting the meta data for an image, when stiching the images
        into a PDF files, we would need this.
    """
    def __init__(this, locator:str):
        this._Locator = locator
        this._Image = Image.open(locator)
        this._MetaData = {}
        exifdata = this._Image.getexifdata
        for tagid in exifdata:
            tagname = ExifTags.TAGS.get(tagid, tagid)
            value = exifdata.get(tagid)
            this._MetaData[tagname] = value

    @property
    def Height(this):
        return this._MetaData["YResolution"]

    @property
    def Width(this):
        return this._MetaData["XResolution"]


class MyComicPDF(FPDF):
    A4PageWidth = 210 # in mm, for an A4 paper
    A4PageHeight = 287

    def __init__(this, filename="out", unit:str="mm", format="A4"):
        super().__init__(unit=unit, format=format)
        this._FileName = filename
        this.set_margins()
        this.add_page()

    @property
    def fileName(this):
        return this._FileName

    def set_margins(this, left=0,top=0,right=0):
        super().set_margins(left, top, right)

    def FitImageaAndNewPage(this, filepath:str, lastpage:bool=False):
        # TODO: image dimension needs to be centered, and preserved the portion.
        this.image(name=filepath, x=0, y=0, w=MyComicPDF.A4PageWidth, h=0)
        if not lastpage: this.add_page()


class ImagesFolders:
    """
        Firewalls has been put onto this class, it will collect errors and exceptions

        * Exceptions and Errors:
            - The directory for the book doesn't exist: IOError

        * Stitching Policies:
            - Each chapter of the book is stitched vertically together, no scaling of the images
            are involved.
            - The widest image determine the width of the output image.
            - All other extra spaces are padded with black, or white.

        * PDF Conversion Policies:
            - If images are all of the same size (Same portions?),
             then all pages has the same portion as the images and the width is a fixed number.
            - If images are of different portions, then use A4 and it will place
            image in the center and preserves the portion.
    """

    def __init__(this, directory:str, depth=2):
        """
            The directory of the one book.
        :param directory:
            String, that can be interpreted by python pathlib methods.
        """
        this._MainDirStr = directory
        ThePath:Path = Path(directory)
        if not ThePath.exists():
            raise IOError()
        this._MainDir = ThePath  # The main folder of the book.
        this._ImagesBatchesItr = FilterOutImages(directory, depth=depth) # An iterator for images
        this._StitchedImages = [] # stitched imagees in the format of numpy array
        # root folder name is name of the PDF.
        this._Pdf = MyComicPDF(directory.split("\\")[-1])

    def _ReportTree(this, root:str, files:str, indent:str=""):
        Result = ""
        Result += f"{indent}dir: {root}, constains images: \n"
        for f in files:
            Result += f"{indent} - {f}\n"
        if len(files):
            Result += "This Directory doesn't seem to have image files. "
        return Result

    def __str__(this):
        ToPrint = ""
        ImagesCount = 0
        for Path, Files in this._ImagesBatchesItr:
            ImagesCount += len(Files)
            ToPrint += this._ReportTree(Path, Files)
        ToPrint += "\n"
        ToPrint += f"Total Number of Pages Found: {ImagesCount}"
        return ToPrint

    def ConcateImages(this):
        """
            Establish field: Stiched Images, as a map of all the files
            directories mapping to the file name.
            NOTE:
                Raise exception if failed to read any of the images!!!
        :return:
            None
        """
        StitchedImgs = []
        NewImageBatches = []
        for RootDir, Images in tqdm(this._ImagesBatchesItr):
            NewImageBatches.append((RootDir, Images))
            if len(Images) != 0:
                Images = sorted(Images)
                NpArrays = []
                with tqdm(Images, leave=False) as Pbar:
                    for f in Pbar:
                        Pbar.set_description(f"{f}")
                        ToStore = ReadImage(f"{RootDir}{f}")
                        if ToStore is None:
                            raise Exception(f"Failed to read one of the files in directory: {RootDir}{f}")
                        NpArrays.append(ToStore)

                    StitchedImgs.append((RootDir, ConcateImageArray(NpArrays)))
        this._StitchedImages = StitchedImgs
        this._ImagesBatchesItr = NewImageBatches

    def StoreImages(this):
        """
            Story this._StitchedImages from numpy array to images.
        :return:
            None
        """
        with tqdm(this._StitchedImages) as pb:
            for RootDir, Ndarray in pb:
                RootPath = Path(RootDir)
                Parent = Path(RootDir).parent.absolute()
                Flocator = str(Parent) + f"\\out\\{RootPath.name} out.png"
                SaveAsImage(f"{Flocator}", Ndarray)
                pb.set_description(f"saving to: {Flocator}")


    def StoreToPDF(this):
        ToStore = []
        for RootDir, Images in this._ImagesBatchesItr:
            for Image in Images:
                ToStore.append(f"{RootDir}{Image}")
        with tqdm(ToStore[:-1]) as pd:
            for Locator in pd:
                this._Pdf.FitImageaAndNewPage(Locator)
        this._Pdf.FitImageaAndNewPage(ToStore[-1], lastpage=True)
        Path(str(this._MainDir.absolute()) + "out").mkdir(parents=True, exist_ok=True)
        this._Pdf.output(this._MainDirStr + f"\\out\\{this._Pdf.fileName}.pdf")


def main():
    Subject = ImagesFolders(r"C:\Users\victo\Desktop\MLP\Spacpone Apogee\Issue1")
    Subject.ConcateImages()
    Subject.StoreImages()
    warn("This is a warning message. ")
    Subject.StoreToPDF()



if __name__ == "__main__":
    main()
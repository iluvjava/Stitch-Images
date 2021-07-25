from utils import ReadImage, SaveAsImage, ConcateImageArray, FilterOutImages
from pathlib import Path
from fpdf import FPDF
from tqdm import tqdm
from PIL import Image, ExifTags
import click

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


class ImageMetaData:
    """
        For getting the meta data for an image, when stiching the images
        into a PDF files, we would need this.
    """
    def __init__(this, locator:str):
        this._Locator = locator
        this._Image = Image.open(locator)

    @property
    def Height(this):
        return this._Image.size[1]

    @property
    def Width(this):
        return this._Image.size[0]


class MyPDF(FPDF):
    A4PageWidth = 210 # in mm, for an A4 paper
    A4PageHeight = 287

    def __init__(this, filename="out", unit:str="mm", format="A4"):
        super().__init__(unit=unit, format=format)
        this._FileName = filename
        this.set_margins()

    @property
    def fileName(this):
        return this._FileName

    def set_margins(this, left=0,top=0,right=0):
        super().set_margins(left, top, right)

    def FitImageaAndNewPage(this, filepath:str):
        Img = ImageMetaData(filepath)
        Height =int((Img.Height/Img.Width) * MyPDF.A4PageWidth) # Recompute Height
        this.add_page(format=(MyPDF.A4PageWidth, Height))
        this.image(
            name=filepath,
            x=0,
            y=0,
            w=MyPDF.A4PageWidth,
            h=0
        )



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
            - Each page is the same size as the image, but the width of all the pages
            are fixed to 210 mm.
    """

    def __init__(this, directory:str, depth=2):
        """
            The directory of the one book.
        :param directory:
            String, that can be interpreted by python pathlib methods.
        """

        ThePath:Path = Path(directory)
        if not ThePath.exists():
            raise IOError()
        this._MainDir = ThePath  # The main folder of the book.
        this._MainDirStr = str(ThePath)
        this._ImagesBatchesItr = list(FilterOutImages(directory, depth=depth)) # An iterator for images
        this._StitchedImages = [] # stitched imagees in the format of numpy array
        # root folder name is name of the PDF.
        this._Pdf = MyPDF(directory.split("\\")[-1])

    def _ReportTree(this, root:str, files:str, indent:str=""):
        Result = ""
        Result += f"{indent}dir: {root}, constains images: \n"
        for f in files:
            Result += f"{indent} - {f}\n"
        if len(files) == 0:
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
        for RootDir, Images in tqdm(this._ImagesBatchesItr):
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
        with tqdm(ToStore) as pd:
            for Locator in pd:
                this._Pdf.FitImageaAndNewPage(Locator)
        ToStoreDir = Path(str(this._MainDir.parent.absolute()) + r"\out")
        ToStoreDir.mkdir(parents=True, exist_ok=True)
        ToStoreDir = str(ToStoreDir.absolute())
        this._Pdf.output(rf"{ToStoreDir}\{this._Pdf.fileName}.pdf")

# ==============================================================================
#                       For Command Line Interface
# ==============================================================================


def test():
    Subject = ImagesFolders(r"C:\Users\victo\Desktop\MLP\Spacpone Apogee\Issue1")
    Subject.ConcateImages()
    Subject.StoreImages()
    warn("This is a warning message. ")
    Subject.StoreToPDF()
    Subject = ImagesFolders(r"C:\Users\victo\Desktop\MLP\Spacpone Apogee\Issue2")
    Subject.ConcateImages()
    Subject.StoreImages()
    warn("This is a warning message. ")
    Subject.StoreToPDF()

# Click library at the entry point
@click.command()
@click.option("-directory","-d",
              required=True,
              help="Specify an existing directory to your collections of comic pages." \
              "Directory should contains .png, .jpeg, or .jpg files. ")
@click.option("-level", "-l",
              default=2,
              type=click.IntRange(0, 20, clamp=True),
              help="specify how deep is your comic book directory. ")

def entrypoint(directory:str, level:int):

    try:
        Converter = ImagesFolders(directory=directory, depth=level)
    except IOError:
        print(f"Failed to read from directory: {directory}")
        return
    except Exception:
        print(f"Unexpected Error when constructing converter on directory: {directory}")
        return
    print(Converter)
    warn("The pages of the PDF output will have pages listed in the order above, continue? ")
    TheInput = input("Press any key to continue, <space> plus <enter> to abort")
    if TheInput == " ":
        print("Aborted")
        return
    Converter.ConcateImages()
    Converter.StoreImages()
    Converter.StoreToPDF()




if __name__ == "__main__":
    entrypoint()
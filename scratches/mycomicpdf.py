from fpdf import FPDF

class MyComicPDF(FPDF):
    PageWidth = 210 # in mm, for an A4 paper.
    def __init__(this, filename="out"):
        super().__init__()
        this._FileName = filename
        this.set_margins()
        this.add_page()

    def set_margins(this, left=0,top=0,right=0):
        super().set_margins(left, top, right)

    def FitImageaAndNewPage(this, filepath:str, LastPage=False):
        this.image(name=filepath, x=0, y=0, w=MyComicPDF.PageWidth, h=0)
        if not LastPage: this.add_page()



Instance:MyComicPDF = MyComicPDF("filename")
Instance.FitImageaAndNewPage(r"..\data\Azure_Comm_1.png")
Instance.FitImageaAndNewPage(r"C:\Users\victo\Desktop\MLP\Spacpone Apogee\Issue1\001\01.png", LastPage=True)
Instance.output("test.pdf", "F")

## DESIGN SHEET Brrruuuuuh
**Problems to solve:** 

1. Given a set of paths to files, filter out all images. \[DONE\] 
2. stitch all the images vertically together. \[Done\]
3. put images into pages of PDF file 

**Things to design:** 

* A class that scans for all the images in a folder. 
    * Folder exists? \[DONE\]
    * Depth = 2? \[DOEN\]
    * Folder has images?  
    * Print out and show it to the user? \[DONE\] 
    * API methods to perform the conversion to big images and PDF? \[DONE\]
  
* Fitting the image on A4. 
  * Test on ratio of the image and the 297, 210 dimension of the A4 paper.\[Canceled\]
  * Scale the page accordingly...? \[Canceled\] 
  * Change the size of the page depending on the image. \[DONE\]
  
* Use `fpdf2, opencv2` and `pillow` for media files manipulations

## What Does This Script Do? 

* Convert folders of images into one big image by stitching then vertically together into one big image, then put it into an folder `out` inside the parent directory. 
* Convert a nested directories of images into one big PDF file, where all images are sorted by directory's name and then the names of the images. 

### Expected Directory Format

```
MyComic Book  <-- Root Directory of Comic Book
- Chapter 1
  - 01.png
  - 02.png
  - (...)
- Chapter 2
  - 01.png
  - 02.png
  - (...)
- Chapter 3
  - 01.png
  - 02.png
  - (...)
  - Side Comic
    - 01.png
    - 02.png
    - (...)
- Epilogue
  - 01.png
  - 02.png
  - (...)

```

In this directory the script will: 
* Stitch all the images in each `chapters` vertically into one big image file. Then it's put under the `out` folder inside the parent directory of the folder for that chapter.
* The whole book, all images in each chapter will get converted into one big PDF file, put in the `out` folder inside parent directory of the comic book. (`"../out"`) 

### Do all images have to be in the same Size? 

- For the PDF output, No. 
- For that one big image that stitched together for each chapter, yes, it matters. 


## Setting up Environment to run the Script
* Cd to the directory you cloned the repo.
* Install python on the computer and make sure it's in under the path.
* Note: If `pip` doesn't work, replace `python -m pip` instead. Then things should work 

### With just python and pip on Windows/Linux, WITHOUT Virtual Environment. 
```
python -m pip install -r requirements.txt
```

### With python venv on Windows/Linux

```
pip install virtualenv
python -m venv .
cd Scripts
activate
cd ..
```

### With Pipenv + Pyenv on Whatever (Recommended)

* Hm..if you know pipenv and pyenv you are an expert I don't want to explain how to setup the environment. 
* This is the best way to setup the environemnt I think, and I have pipfile ready too.


## Run the script

```
python main.py --help
```

* Basically: 
  * Give the script the root directory of the comic book
  * Give the script the depth of the directories to go into, directory deeper than given depth will be ignored. 
  * Then the script will print out the stuff it did before actually doing it. 
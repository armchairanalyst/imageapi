from jinja2 import Template
from ImageAPIHandler import ImageData
import os
from tempfile import NamedTemporaryFile
from urllib import request
from utils import GenerateRandomString
from subprocess import Popen
import os
from rectpack import newPacker, PackingMode, PackingBin
from rectpack import GuillotineBafSas,SkylineMwf, GuillotineBssfSas, MaxRectsBaf, MaxRectsBl






from rectpack import GuillotineBssfSas, GuillotineBssfLas, \
    GuillotineBssfSlas, GuillotineBssfLlas, GuillotineBssfMaxas, \
    GuillotineBssfMinas, GuillotineBlsfSas, GuillotineBlsfLas, \
    GuillotineBlsfSlas, GuillotineBlsfLlas, GuillotineBlsfMaxas, \
    GuillotineBlsfMinas, GuillotineBafSas, GuillotineBafLas, \
    GuillotineBafSlas, GuillotineBafLlas, GuillotineBafMaxas, \
    GuillotineBafMinas

from rectpack import MaxRectsBl, MaxRectsBssf, MaxRectsBaf, MaxRectsBlsf

from rectpack import SkylineMwf, SkylineMwfl, SkylineBl, \
    SkylineBlWm, SkylineMwfWm, SkylineMwflWm


from rectpack import SORT_AREA, SORT_PERI, SORT_DIFF, SORT_SSIDE, \
    SORT_LSIDE, SORT_RATIO, SORT_NONE

from PIL import Image
from random import randint


pckalgo = SkylineMwf
srtalgo = SORT_NONE

wd = os.path.dirname(os.path.realpath(__file__))
savepath = os.path.join(wd,'static','selection')
templatepath = os.path.join(wd,'templates')

a4templatefile = "A4.svg"
a3templatefile = "A3.svg"

dpi = 144 #dots per inch
pxpermm = 5.5 # Calculated for 144 dpi, a decent resolution for print.

padding = -5
offsetx = 7
offsety = 7
bincount = 3

widthredfactor = 1
heightredfactor = 1

a4w = int(210.0/25.4 * dpi)
a4h = int(297.0/25.4 * dpi)

a3w = int(297.0/25.4 * dpi)
a3h = int(420.0/25.4 * dpi)

a4wmm = 210
a4hmm = 297

a3wmm = 297
a3hmm = 420

pxpermm = (210/25.4 * dpi)/a4wmm

longest_dimension = 400 # in pixels


print("Pixels per mm : "+ str(pxpermm))

svgImageTag =   '''  <image
                       y="{{y_pos}}"
                       x="{{x_pos}}"
                       id="{{id}}"
                       xlink:href="{{filename}}"
                       preserveAspectRatio="none"
                       height="{{height}}"
                       width="{{width}}" /> 
                '''

svgA4template=  '''
                <?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="210mm"
   height="297mm"
   viewBox="0 0 210 297"
   version="1.1"
   id="SVGRoot"
   inkscape:version="0.92.2 (5c3e80d, 2017-08-06)"
   sodipodi:docname="A4.svg">

  <defs
     id="defs10" />
  <metadata
     id="metadata13">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
         {{images}}
</svg>

'''

svgA3template = '''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="297mm"
   height="420mm"
   viewBox="0 0 297 420"
   version="1.1"
   id="SVGRoot"
   inkscape:version="0.92.2 (5c3e80d, 2017-08-06)"
   sodipodi:docname="A3.svg">
  
  <defs
     id="defs100" />
  <metadata
     id="metadata103">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     id="layer1"
     inkscape:groupmode="layer"
     inkscape:label="Layer 1">
    
         {{images}}
</svg>


'''



svgimagetemplate = None
documentTemplate = None
svgimagetemplate = Template(svgImageTag)

def loadTemplatesFromFiles():
    global svgA3template,svgA4template
    try:
        with open(os.path.join(templatepath,a4templatefile)) as f:
            svgA4template = f.read()
        with open(os.path.join(templatepath,a3templatefile)) as f:
            svgA3template = f.read()
            svgA3template = svgA3template
    except Exception as e:
        #Do nothing.
        pass

# Load templates from template folder.
loadTemplatesFromFiles()

def CreateSVGDocument(imagedatalist, size:str):
    # Curate the images by filling up SVG data
    global savepath,a4h,a4w,a3h,a3w,dpi,padding, longest_dimension, offsetx,offsety,srtalgo
    global widthredfactor
    global heightredfactor
    global bincount
    binw = 0
    binh = 0


    svgImageContent = ""
    packer = newPacker(mode=PackingMode.Offline, bin_algo=PackingBin.Global, pack_algo=pckalgo, sort_algo=srtalgo)


    if size == "A3":
        documentTemplate = Template(svgA3template)
        binw = a3wmm
        binh = a3hmm
        longest_dimension = 350
        packer.add_bin(width=binw*widthredfactor, height=binh*heightredfactor, count=bincount)
    else:
        documentTemplate = Template(svgA4template)
        binw = a4wmm
        binh = a4hmm
        longest_dimension = 300
        packer.add_bin(width=binw*widthredfactor, height=binh*widthredfactor, count=bincount)

    # Set the positions of the images before hand.
    # iterate through the images and set sizes as per dpi



    for image in imagedatalist:

        # Load image from disk.
        loc = os.path.join(savepath,image.src)

        img = Image.open(loc)
        (image.width,image.height) = img.size

        # scale the width and heights to match
        # document dpi
        ih = float(image.height)
        iw = float(image.width)

        # Calculate and scale the image based on longest dimension factor.

        if ih>iw:
            scalefactor = ih / float(longest_dimension)
        else:
            scalefactor = iw / float(longest_dimension)

        print("Scale Factor is : "+str(scalefactor))
        # This preserves the aspect ratio
        if scalefactor == 0.0:
            scalefactor = 1
        ih = ih / scalefactor
        iw = iw / scalefactor

        # calculate dimension of image in mm in the document.
        ih = int(ih / pxpermm)
        iw = int(iw / pxpermm)

        # ih = int((25.4 * ih) / dpi)
        # iw = int((25.4 * iw) / dpi)

        image.height = ih
        image.width = iw

        packer.add_rect(iw,ih,rid=image.id)

    packer.pack()

    '''
    packer.rect_list():
    Returns the list of packed rectangles, 
    each one represented by the tuple 
    
    (b, x, y, w, h, rid) where:

    b: Index for the bin the rectangle was packed into
    x: X coordinate for the rectangle bottom-left corner
    y: Y coordinate for the rectangle bottom-left corner
    w: Rectangle width
    h: Rectangle height
    rid: User provided id or None
    '''

    results = {}
    rlist = packer.rect_list()
    if len(rlist) == len(imagedatalist):

        for rect in rlist:
            results[rect[5]] = rect
        for image in imagedatalist:
            r = results[image.id]

            # x and y co-ordinate are given to bottom left of image.
            # we are converting co-ordinates to topleft.
            xpos = r[1] + offsetx
            ypos = r[2] + offsety

            rw = r[3]
            rh = r[4]

            # Translation to screen co-ordinates
            sx = xpos #xpos + binw/2
            sy = ypos #binh/2 - ypos

            image.xpos = sx
            image.ypos = sy
            image.width -= padding
            image.height -= padding
    else:
        print("Unable to pack images.. Going for a random packing.")
        # Set random locations for the images

        for image in imagedatalist:
            image.xpos = randint(0,100)
            image.ypos = randint(0,100)
    # start setting image positions based on obtained packing



    # Initialize the bin packing algo.


    try:
        for image in imagedatalist:
            # Download the image


            # TODO : Make a multi-threaded downloader
            svgImageContent += GenerateSVGImageTag(image,image.src)
    except Exception as e:
        print(e)
        return "500"

    doc = {}
    doc["images"] = svgImageContent
    content = documentTemplate.render(doc)
    file = NamedTemporaryFile(mode='w',dir=savepath,delete=False,suffix=".svg")
    fn = file.name
    file.write(content)
    file.close()
    print(fn)
    os.startfile(fn)
    return "200"

def GenerateSVGImageTag(imageData: ImageData, filename):
    global dpi
    data = {}


    data["x_pos"] = imageData.xpos
    data["y_pos"] = imageData.ypos
    data["id"] = str(imageData.id)
    data["filename"] = filename
    data["height"] = str(imageData.height)
    data["width"] = str(imageData.width)
    return svgimagetemplate.render(data)


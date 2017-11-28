import os
from utils import GenerateRandomString
import subprocess

publicdir = "selection/"
wd = os.path.dirname(os.path.realpath(__file__))
savedir = os.path.join(wd,'static','selection')

commandTemplate = '''wget {file} -O {filename} '''

def DownloadImage(url):
    print("Downloading : "+url)
    # First download the file to the public folder.
    fname = GenerateRandomString(5)+".jpg"
    command = commandTemplate.format(file=url, filename=os.path.join(savedir,fname))
    args = command.split(sep=' ')
    print(args)

    # Open a separate process to download the image. But return the image name
    # immediately.
    process = subprocess.Popen(args)
    # returns name.jpg
    return fname


def CheckImage(name):
    flist = os.listdir(savedir)
    if name in flist:
        return True
    return False

def DeleteImage(name):
    try:
        fname = os.path.join(savedir,name)
        if(os.path.isfile(fname)):
            #Delete the file.
            os.remove(fname)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def ClearSelections(filetype):
    l =-1 * len(filetype)
    res = []
    try:
        print("Save dir is : "+savedir)
        flist = os.listdir(savedir)
        for f in flist:
            if(str(f)[l:] == filetype):
                res.append(os.path.join(savedir,f))
        res = res
        [os.remove(f) for f in res]
    except Exception as e:
        print(e)

def GetCurrentSelection():
    global savedir
    # Ignores SVG files.
    flist = os.listdir(savedir)
    res = []
    for f in flist:
        if(str(f)[-3:] != "svg"):
            res.append(os.path.join(savedir,f))
    return res
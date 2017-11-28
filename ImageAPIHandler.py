from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from urllib import parse
import time
from json import JSONEncoder
import os, collections
from bs4 import BeautifulSoup
import ast
from utils import view_traceback


import shelve

import requests, base64

################################################################################################
wd = os.path.dirname(os.path.realpath(__file__))


logpath = os.path.join(os.path.expanduser('~'),"geckodriver.log")
print("Webdriver Logpath set to : "+logpath)


browser = None

################################################################################################

ffprofilepath = "ffprofile"
ffprofilepath = os.path.join(wd,ffprofilepath)
dirlist = os.listdir(ffprofilepath)
ffprofilepath = os.path.join(wd,ffprofilepath,dirlist[0])

################################################################################################

api_results_per_page = 12

################################################################################################

bgMoreResultsContainer = '#bop_container'
bgMoreResultsButton = '#bop_container .mm_seemore .btn_seemore'
bgSearchURL = 'https://www.bing.com/images/search?q={0}&qs=n&form=QBILPG'
bgPageLoadIndicator = '#mmComponent_images_1'
bgPageContent = '.dg_b'
bgImageContainer = 'li[data-idx]'
bgElementImageSelector = 'img[class*="mimg"]'
bgElementAnchorSelector = 'a[m]'
bgCurrentQuery = ""

bingSearchCache = {}

################################################################################################

maxImageWidth = 2048
maxImageHeight = 2048
minImageWidth = 100
minImageHeight = 100

maxResults = 10
bgResultsPerRow = 7
bgResultsPerPage = 49
################################################################################################
# CONSTANTS

scroll_wait = 2 # Seconds
global_searchid = 0

################################################################################################

# CACHE data


searchcache = {}
imagecache={}

################################################################################################


class ImageData:
    id = ""
    base64 = ""
    url = ""
    width = 0
    height = 0
    source = "Google Image Search"
    index = 0
    sdurl = ""
    hdurl=""
    src=""
    xpos = 0
    ypos = 0


    def __init__(self,id):
        # A unique ID is required to create an object
        # though other terms can be empty
        self.id = id

    # This representation is useful for
    # comparision when doing list processing
    def __repr__(self):
        return self.id

    def __str__(self):
        return self.id

    def contents(self):
        return ("ID : "+ self.id +
                "; base64 : " + self.base64 +
                "; url : " + self.url +
                "; width : " + self.width +
                "; height : " + self.height)

# Util Functions

def GetBingResultElements():

    # Gets available bing result elements from current page.
    elem = None
    bs = None
    elist = None

    elem = browser.find_element_by_css_selector(bgPageContent)
    bs = BeautifulSoup(elem.get_attribute('innerHTML'), 'html.parser')
    elist = bs.select(bgImageContainer)

    return elist

def InitializeBrowser():
    global browser,logpath,pjspath,wd
    profile_name = "SELENIUM"
    geckopath = os.path.join(wd,"geckodriver.exe")
    try:
        browser = webdriver.Firefox(log_path=logpath, executable_path=geckopath,firefox_profile=ffprofilepath)
        browser.implicitly_wait(3)
        #browser = webdriver.PhantomJS(logpath=logpath)
        #browser.implicitly_wait(10)
    except Exception as e:
        print("Error starting PhantomJS")
        view_traceback()

InitializeBrowser()

# API V 2

def LoadBingSearchPage(query):
    global bgSearchURL,bgPageLoadIndicator, bgCurrentQuery

    # Stateful request. Subsequent operations are
    # implicitly meant for this query.
    # TODO : Make this stateless.
    bgCurrentQuery = query

    # queries = bingSearchCache.keys()
    # try:
    #     if query in queries:
    #         return str(len(bingSearchCache[query]))
    # except Exception as e:
    #     view_traceback()
    #     return "-1"

    browser.get(bgSearchURL.format(query))
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, bgPageContent)))
    content = None
    content = browser.find_element_by_css_selector(bgPageLoadIndicator)
    if content is not None:
        return LoadBingSearchResults(query)
    else:
        return "-1"

def GetBingSearchImages(n, offset):

    global bingSearchCache,bgCurrentQuery
    imageCount = None
    try:
        imageCount = len(bingSearchCache[bgCurrentQuery])
        if imageCount == 0 or imageCount is None:
            LoadBingSearchPage(bgCurrentQuery)
    except Exception as e:
        imageCount = 0
        return "404"
    # Cleaning the input
    if n<=0:
        n=1
    if offset <=0:
        offset = imageCount
    if offset >= imageCount:
        # If asking for more than available images, return a default value.
        offset = imageCount-1
    if n+offset > imageCount:
        ScrollBingPage(2)
        # Update the results in the browser.
        LoadBingSearchResults(bgCurrentQuery)
        imageCount = len(bingSearchCache[bgCurrentQuery])
        #n = imageCount-(offset)
    try:
        if bingSearchCache:
            results = bingSearchCache[bgCurrentQuery]
            idxrange = range(n,n+offset+1)
            apiresults = []

            # Note sometimes, keys may be missing

            for key in idxrange:
                try:
                    apiresults.append(results[str(key)])
                except KeyError as ke:
                    pass

            jsonresponse = "{\n"
            for apiresult in apiresults:
                id = apiresult.id
                image = apiresult
                jsonresponse += "\"" + id + "\"" + ": "
                jsonresponse += JSONEncoder().encode({
                    "base64": image.base64,
                    "url": image.url,
                    "width": image.width,
                    "height": image.height,
                })
                jsonresponse += ","
            jsonresponse = jsonresponse[:-1]
            jsonresponse += "}\n"
            return jsonresponse
        else:
            return "500"
    except Exception as e:
        view_traceback()
        return "501"

# Return no. of results found, which inturn is based on maxResults
def LoadBingSearchResults(query):
    global maxResults,bgResultsPerRow
    #ScrollBingPage(2)

    elements = GetBingResultElements()
    results = {}
    for e in elements:
        try:
            image = ProcessBingImageElement(e)
            index = e["data-idx"]
            results[str(index)] = image
        except Exception as e:
            print("LoadBingSearchResults Error : "+e)
            view_traceback()


    # Save Images to in-memory cache
    # TODO : Convert to simple storage using sqlalchemy and sqllite3
    bingSearchCache[query] = results
    rescount = str(len(results))
    return rescount

def ScrollBingPageTillMaxResults():
    global bgImageContainer
    elist = None
    maxscrolls = int(maxResults / bgResultsPerPage)
    ScrollBingPage(maxscrolls)
    time.sleep(scroll_wait*2)
    elem = browser.find_element_by_css_selector(bgPageContent)
    bs = BeautifulSoup(elem.get_attribute('innerHTML'), 'html.parser')
    elist = bs.select(bgImageContainer)

    # Additional Checks
    maxtries = 5
    if len(elist) <= maxResults:
        if elist is not None and len(elist) > 0:
            while maxtries > 0:
                # Try for max maxtries times only
                print("Trying to scroll page : " + str(maxtries))
                maxtries -= 1
                if len(elist) < maxResults:
                    ScrollBingPage(1)
                    elem = browser.find_element_by_css_selector(bgPageContent)
                    bs = BeautifulSoup(elem.get_attribute('innerHTML'), 'html.parser')
                    elist = bs.select(bgImageContainer)
                else:
                    break
    return elist

def ScrollBingPage(nPages):
    # Scrolls a Bing Image search by a defined
    # number of pages.
    print("Scrolling target page.")
    global bgMoreResultsContainer,bgMoreResultsButton
    showMoreContainer = None
    showMoreButton = None

    try:
        # Need to scroll once to ensure presence of indicating element
        # quirk observed in Bing page.
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_wait)
        if nPages>2:
            nPages = nPages-2
            for i in range(nPages):
                showMoreContainer = browser.find_element_by_css_selector(bgMoreResultsContainer)
                cls = showMoreContainer.get_attribute("class")
                if "b_hide" in cls or cls == "":
                    # Button is hidden. Scrolling can be made directly
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                else:
                    showMoreButton = browser.find_element_by_css_selector(bgMoreResultsButton)
                    showMoreButton.click()
            return True
        else:
            return True
    except Exception as e:
        view_traceback()
        return False

# Generate an ImageData object from given
# Bing Image Container
def ProcessBingImageElement(element):

    global bgElementImageSelector, bgElementAnchorSelector
    imgele = element.select(bgElementImageSelector)[0]
    aele = element.select(bgElementAnchorSelector)[0]
    m = ast.literal_eval(aele["m"])
    image = ImageData(m["cid"])
    image.base64 = m["turl"]
    image.url = m["murl"]
    image.height = imgele["height"]
    image.width = imgele["width"]
    return image

def LoadImagesFromBrowser():

    global bingSearchCache,bgCurrentQuery

    print("Loading browser results..")
    ScrollBingPage(1)
    time.sleep(scroll_wait)
    elist = None
    try:
        bingSearchCache[bgCurrentQuery] = None
        elist = GetBingResultElements()
        results = {}
        for e in elist:
            try:
                image = ProcessBingImageElement(e)
                index = e["data-idx"]
                results[str(index)] = image
            except Exception as e:
                view_traceback()

        # Save Images to in-memory cache
        # TODO : Convert to simple storage using sqlalchemy and sqllite3
        bingSearchCache[bgCurrentQuery] = results
        rescount = str(len(results))
        print(rescount+" no. of images loaded onto cache for : "+bgCurrentQuery)
        return rescount
    except Exception as e:
        view_traceback()
        return "-1"



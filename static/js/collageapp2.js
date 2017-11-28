// Web page specific handling here..

// Globals
var imagesPerPage = 12;
var currentOffset = 1;
var totalPages = 0;
var currentPages = 0;

var prevImageSet= null;
var currentQuery = "";
var serverURL = 'http://127.0.0.1:7990/api/search/bing?';
var queryURL = 'http://127.0.0.1:7990/api/search/bing?';
var resultsURL = 'http://127.0.0.1:7990/api/search/bing/results?';
var saveImageURL = 'http://127.0.0.1:7990/api/image/save';
var loadBrowserResultsURL = 'http://127.0.0.1:7990/api/search/bing/loadfrombrowser';
var createDocumentURL = 'http://127.0.0.1:7990/api/document/create';
var browserResultsURL = 'http://127.0.0.1:7990/api/search/bing/';
var reloadBrowserURL = 'http://127.0.0.1:7990/api/browser/reload';
var selectImageURL = 'http://127.0.0.1:7990/api/addimage';
var currentSelectionURL = 'http://127.0.0.1:7990/api/currentselection';
var selTarget = "#selectiongrid";
var requestTimeout = 400000;
var imageidtag = "bbs_"

var gda3btntext = "Generate A3";
var gda4btntext = "Generate A4";

var selectedImagesTitle = "Images Selected";
var selectedImagesCount = 0;

var emptyImageURL = 'images/no-image-box.png';
var loadingImageURL = 'images/imageloading.png'
var canvascontainer = "#canvasgrid";
var imagecanvas = "#imagecanvas";
var loadingimage = "#loadingimage";
var selectedimages = {};

var pendingimages ={};
var isGeneratingDocument = false;

$(loadingimage).hide();
$(canvascontainer).hide();
loadImages(emptyImageURL);


// Continuously check for an load images from server.
var polldelay = 2000; // milliseconds
var checkImageURL = 'http://127.0.0.1:7990/api/checkimage?q=';
var removeImageURL = 'http://127.0.0.1:7990/api/removeimage?q=';

function pollTimer(){
    // Iterate through the pending image list, if it's not empty
    var keys = Object.keys(pendingimages);
    $.each(pendingimages,function(key,value){
        console.log("Checking for image key = "+key+" Value = "+value);
        filename = getFileName(value);
        console.log("Checking for.."+checkImageURL+filename);
        $.ajax({
            type: 'GET',
            dataType: 'text',
            url: checkImageURL+filename,
            timeout: 30000,
            success: function (data, textStatus) {
                if(data == "YES"){
                    delete pendingimages[key];
                    updateImageInSelection(key,value);
                }else{
                    // Do nothing...
                }
            },
            error: function (xhr, textStatus, errorThrown) {

                console.log("Error fetching status of Image");

            }
        });
    })

    setTimeout(pollTimer,polldelay);

    lightbox.option({
        'resizeDuration': 100,
        'wrapAround': true,
        'fadeDuration':50
    })
}

$(document).ready(function(){
    // Start the polling function.
    pollTimer();
    // Get the already selected images
    $.ajax({
        type: 'GET',
        dataType: 'text',
        contentType: 'application/json; charset=utf-8',
        url: currentSelectionURL,
        timeout: 30000,
        success: function (data, textStatus) {
            console.log(data);
            obj = JSON.parse(data);
            $.each(obj,function(key,value){
                // Add each value to the selection list.
                appendImageToSelection(GetRandomString(5),value,"","","","","");
            });

            updateSelectedImagesCount();
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log("Error removing status of Image");
        }
    });

    // Set button texts.
    $('#gda3button').text(gda3btntext);
    $('#gda4button').text(gda4btntext);
});


$("#searchtext").on('keyup', function (e) {
    if (e.keyCode == 13) {
        // Do something
        performSearch()
    }
});

function GetSelectedImagesTitle(count) {
    return count + " - " + selectedImagesTitle;
}

function loadImages(imageURL) {
    count = 1;
    for (count = 1; count <= 12; count++) {
        $("#pic" + count).attr('src', imageURL);
    }
}

function handleSearch(isNewQuery) {

    // Always performs search on the current query

    // If it's a new query, instruct server to load results
    if (isNewQuery) {
        LoadSearchResultsInServer(currentQuery);
    }
    // Load the first page once.
    LoadSearchResultsPage(currentOffset, imagesPerPage);

}

function reloadSearch() {
    currentOffset = 1;
    handleSearch(true);
}

function LoadSearchResultsInServer(text) {

    console.log("CurrentOffset : " + currentOffset);
    $('#canvasgrid').show();
    loadImages(loadingImageURL);
    url = queryURL + "q=" + text;
    $('#loadingStatus').text("Awaiting Results");
    $.ajax({
        type: 'GET',
        dataType: 'text',
        url: url,
        timeout: 30000,
        success: function (data, textStatus) {
            console.log(data);
            $('#loadingStatus').text(data + " Results found");
            $('#canvasgrid').hide();
            // Load the first page by default
            loadImages(emptyImageURL);
        },
        error: function (xhr, textStatus, errorThrown) {
            $('#loadingStatus').text("Error");
            $('#canvasgrid').hide();
            loadImages(emptyImageURL);
        }
    });



    $.get(url, function (data) {

    });


}

function LoadSearchResultsPage(n, offset) {
    // Fetch search results
    console.log("Fetching search results for " + currentQuery + " with n : " + n + " , offset : " + offset);
    if (currentQuery != "") {
        url = resultsURL + "n=" + n + "&o=" + offset;
        loadImages(loadingImageURL);
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: url,
            timeout: requestTimeout,
            success: function (data, textStatus) {
                console.log(data);
                // Load the first page by default
                displayResults(data);
            },
            error: function (xhr, textStatus, errorThrown) {
                loadImages(emptyImageURL);
                // Load the current results.


                console.log(errorThrown + ":" + textStatus + ":" + xhr);
            }
        });

    }
}

function loadBrowserResults() {
    if (currentQuery != "") {
        //currentOffset = 1;
        url = loadBrowserResultsURL;
        loadImages(loadingImageURL);
        $.ajax({
            type: 'GET',
            dataType: 'text',
            url: url,
            timeout: requestTimeout,
            success: function (data, textStatus) {
                console.log(data);
                currentOffset += imagesPerPage;
                $('#loadingStatus').text(data + " Results found");
                // Load the first page by default
                LoadSearchResultsPage(currentOffset, imagesPerPage);
            },
            error: function (xhr, textStatus, errorThrown) {
                loadImages(emptyImageURL);
                console.log(errorThrown + ":" + textStatus + ":" + xhr);
            }
        });

    }
}

function GetNextResultsPage() {
    if (currentQuery != "") {
        currentOffset += imagesPerPage;
        LoadSearchResultsPage(currentOffset, imagesPerPage);
    }
}

function GetPrevResultsPage() {
    if (currentQuery != "") {
        if (currentOffset - imagesPerPage < 0) {
            currentOffset = 1;
        } else {
            currentOffset -= imagesPerPage;
        }
        LoadSearchResultsPage(currentOffset, imagesPerPage);
    }
}

function displayResults(msg) {
    this.prevImageSet = msg;
    console.log("No. of results :" + Object.keys(msg).length);
    count = 1;
    Object.entries(msg).forEach(([key, value]) => {
        // Set contents of images.
        imageURL = value["url"];
        uid = key;
        if (imageURL != "") {
            $("#pic" + count).attr({
                'src': value["base64"],
                'uid': uid,
                'hdurl': imageURL
            });
        }
        count++;

    });

}

function handleInput(event) {
    if (event.keyCode == 13) {
        // do something
        performSearch();
    }
}

function handleSearchButton() {
    performSearch();
}

function performSearch() {
    var text = extractSearchText();
    newQuery = false;
    if (text != "")
        if (currentQuery != text) {
            currentQuery = text;
            currentOffset = 1;
            newQuery = true;
        }

    handleSearch(newQuery);

}

function extractSearchText() {
    var text = $("#searchtext").val();
    if (text != "" && text.length > 3)
        return text

    return "";

}

function selectImage(id, type) {

    var iid = "#" + id;
    var isrc = $(iid).attr('src');
    var iuid = $(iid).attr('uid');
    var ihdurl = $(iid).attr('hdurl');
    console.log("iuid = "+iuid);

    nw = $(iid).width();
    nh = $(iid).height();

    imgsrc = $(iid).attr('hdurl');
    console.log(imgsrc);
    var source = "";
    if (type == 'HD')
        source = ihdurl;
    else
        source = isrc;
    
    // Reset for all images to sd source, though images will be downloaded based
    // on user input.
    source = isrc;

    // Add a loading image.
    tempid = GetRandomString(5);

    appendLoadingImageToSelection(tempid);

    // Send the image details to the server and wait for a response.
    iObject = {}
    iObject["uid"]= iuid;
    iObject["hdurl"] = ihdurl;
    iObject["sdurl"] = isrc;
    iObject["type"] = type;

    var serverdata = JSON.stringify(iObject);

    // Add a dummy image
    
    console.log("Selected Image Data sent : "+serverdata);
    $.ajax({
        type: 'POST',
        dataType:'text',
        contentType: 'application/json; charset=utf-8',
        url: selectImageURL,
        data:serverdata,
        timeout: requestTimeout,
        success: function (data, textStatus) {
            console.log(data);

            pendingimages[tempid] = data;
            console.log(tempid+" image added to pending images list - "+data);
            // Data is the image URL
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(errorThrown + ":" + textStatus + ":" + xhr);
        }
    });

    $(selTarget).scrollTop($(selTarget)[0].scrollHeight);
    updateSelectedImagesCount();
}

function updateSelectedImagesCount(){
    $("#selectiontitle h3").text(GetSelectedImagesTitle($(selTarget).children().length))
}

function appendImageToSelection(id,source,iuid,ihdurl,sdurl,nw,nh){
    tid = id;
    $('<a>').attr({
        'id':'__'+tid,
        'href':source,
        'data-lightbox':'bhargavi'
    }).html($('<img />', {
        id: tid,
        src: source,
        oncontextmenu: "removeImage('"+tid+"')",
        'uid': iuid,
        'hdurl': ihdurl,
        'sdurl': sdurl,
        'w': Math.round(nw),
        'h': Math.round(nh),
    })).appendTo(selTarget);
}

function updateImageInSelection(id,source){
    var iid = "#"+id;
    var aiid = '#__'+id;
    $(iid).attr("src",source);
    console.log(aiid);
    $(aiid).attr("href",source);
}

function appendLoadingImageToSelection(id){
    tid = id;
    $('<a>').attr({
        'id':'__'+id,
        'data-lightbox':'bhargavi'
    }).html($('<img />', {
        id: tid,
        src: loadingImageURL,
        oncontextmenu: "removeImage('"+tid+"')"
    })).appendTo(selTarget);
}

function removeImageInServer(filename){
    $.ajax({
        type: 'GET',
        dataType: 'text',
        url: removeImageURL+filename,
        timeout: 30000,
        success: function (data, textStatus) {
            console.log("Removed image "+filename);
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log("Error removing status of Image");

        }
    });
}

function removeImage(id) {
    var iid = "#" + id;
    var aiid = '#'+'__'+id;
    console.log("Removing : " + (iid));
    source = $(iid).attr("src");
    var arr = source.split('?');
    source = arr[0];
    $(String(iid)).remove();
    $(String(aiid)).remove();
    filename = getFileName(source);
    console.log("Removing "+filename+" in server");
    removeImageInServer(filename);
    delete pendingimages[id];
    updateSelectedImagesCount();
}

function getFileName(relativeURL){
    return relativeURL.substring(relativeURL.lastIndexOf('/')+1);
}

function toDataURL(src, callback, outputFormat) {
    try {
        var img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = function () {
            console.log("Loading Image");
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var dataURL;
            canvas.height = this.naturalHeight;
            canvas.width = this.naturalWidth;
            ctx.drawImage(this, 0, 0);
            dataURL = canvas.toDataURL(outputFormat);
            callback(dataURL);
        };
        /*
        img.src = src;
        if (img.complete || img.complete === undefined) {
            img.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
            img.src = src;
        }
        */
    } catch (e) {
        console.log(e);
    }
}

function displayNotification(text, __className) {
    $.notify(text, {
        position: 'bottom right',
        autoHideDelay: 1000,
        className: __className
    });
}

function refreshBrowser() {
    // Reloads the browser in the backend.
    console.log("Reloading Browser");
    $.get(reloadBrowserURL, function (data) {
        if (data == "200") {
            $.notify("Browser reloaded", {
                className: "success"
            });
        } else {
            $.notify("Browser reloading failed", {
                className: "error"
            });
        }
    });
}

function generateDocument(size) {
    if (isGeneratingDocument == false) {
        isGeneratingDocument = true;
        console.log("Generating " + size + " Document");
        var itemselector = selTarget + " img";
        if (size == "A3")
            docurl = createDocumentURL + "/A3";
        else
            docurl = createDocumentURL + "/A4";
        var selectedImages = "";
        selectedimages = {};
        var uid = "";
        items = $(itemselector);
        if (items.length == 0) {
            console.log("No selections made..");
            return;
        }
        items.each(function () {
            image = $(this);
            imageContent = {}
            uid = image.attr('id');
            var src = image.attr('src').split('?')[0];
            imageContent["src"] = src;
            selectedimages[uid] = imageContent;
        });

        serverData = JSON.stringify(selectedimages);
        console.log(serverData);
        $('#gda3button').text("Generating Document...");
        $('#gda4button').text("Generating Document...");
        // Send the json object to the server
        $.ajax({
            type: 'POST',
            dataType: 'text',
            data: serverData,
            contentType: 'application/json; charset=utf-8',
            url: docurl,
            timeout: requestTimeout,
            success: function (data, textStatus) {
                isGeneratingDocument = false;
                $('#gda3button').text(gda3btntext);
                $('#gda4button').text(gda4btntext);
                console.log(data);
            },
            error: function (xhr, textStatus, errorThrown) {
                isGeneratingDocument = false;
                console.log(errorThrown + ":" + textStatus + ":" + xhr);
            }
        });
    }
    else{
        console.log("Document is being generated in the background.")
    }
}

function GetRandomString(len) {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  
    for (var i = 0; i <len; i++)
      text += possible.charAt(Math.floor(Math.random() * possible.length));
  
    return text;
  }

  function refreshImages(){
      // Get all images from the selection grid.
      items = $('#selectiongrid img');
      $.each(items,function(index,value){
          item = $(value);
          source = item.attr('src');

          var arr = source.split('?')
          if(arr.length > 1){
              source = arr[0];
          }
          console.log("Src is : "+source);
          item.attr('src',loadingImageURL);
          item.attr('src',source+"?q="+GetRandomString(3));
      })
  }

  
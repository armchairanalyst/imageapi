// Web page specific handling here..

// Globals
var imagesPerPage = 12;
var currentOffset = 1;
var currentQuery = "";
var serverURL = 'http://127.0.0.1:7990/api/search/bing?';
var queryURL = 'http://127.0.0.1:7990/api/search/bing?';
var resultsURL = 'http://127.0.0.1:7990/api/search/bing/results?';
var saveImageURL = 'http://127.0.0.1:7990/api/image/save';
var loadBrowserResultsURL = 'http://127.0.0.1:7990/api/search/bing/loadfrombrowser';
var createDocumentURL = 'http://127.0.0.1:7990/api/document/create';
var browserResultsURL = 'http://127.0.0.1:7990/api/search/bing/';
var reloadBrowserURL = 'http://127.0.0.1:7990/api/browser/reload';
var selTarget = "#selectiongrid";
var requestTimeout = 400000;

var selectedImagesTitle = "Images Selected";
var selectedImagesCount = 0;

var emptyImageURL = './images/no-image-box.png';
var loadingImageURL = './images/imageloading.gif'
var canvascontainer = "#canvasgrid";
var imagecanvas = "#imagecanvas";
var loadingimage = "#loadingimage";
var selectedimages = {};

$(loadingimage).hide();
$(canvascontainer).hide();
loadImages(emptyImageURL);


function GetSelectedImagesTitle(count){
    return count+" - "+selectedImagesTitle; 
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
    if(isNewQuery){
        LoadSearchResultsInServer(currentQuery);
    }
    // Load the first page once.
    LoadSearchResultsPage(currentOffset,imagesPerPage);

}

function reloadSearch(){
    currentOffset = 1;
    handleSearch(true);
}

function LoadSearchResultsInServer(text) {

    console.log("CurrentOffset : " + currentOffset);
    $('#canvasgrid').show();
    loadImages(loadingImageURL);
    url = queryURL+"q="+text;
    $('#loadingStatus').text("Awaiting Results");
    $.ajax({
        type: 'GET',
        dataType: 'text',
        url: url,
        timeout: 30000,
        success: function(data, textStatus ){
            console.log(data);
            $('#loadingStatus').text(data+" Results found");
            $('#canvasgrid').hide();
            // Load the first page by default
            loadImages(emptyImageURL);
        },
        error: function(xhr, textStatus, errorThrown){
            $('#loadingStatus').text("Error");
            $('#canvasgrid').hide();
            loadImages(emptyImageURL);
        }
      });



    $.get( url, function( data ) {
        
      });
    

}

function LoadSearchResultsPage(n,offset){
    // Fetch search results
    console.log("Fetching search results for "+currentQuery+" with n : "+n+" , offset : "+offset);
    if(currentQuery != ""){
        url = resultsURL+"n="+n+"&o="+offset;
        loadImages(loadingImageURL);
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: url,
            timeout: requestTimeout,
            success: function(data, textStatus ){
                console.log(data);
                // Load the first page by default
                displayResults(data);
            },
            error: function(xhr, textStatus, errorThrown){
                loadImages(emptyImageURL);
                console.log(errorThrown+":"+textStatus+":"+xhr);
            }
          });

    }
}

function loadBrowserResults(){
    if(currentQuery != ""){
        currentOffset = 1;
        url = loadBrowserResultsURL;
        loadImages(loadingImageURL);
        $.ajax({
            type: 'GET',
            dataType: 'text',
            url: url,
            timeout: requestTimeout,
            success: function(data, textStatus ){
                console.log(data);
                $('#loadingStatus').text(data+" Results found");
                // Load the first page by default
                LoadSearchResultsPage(currentOffset,imagesPerPage);
            },
            error: function(xhr, textStatus, errorThrown){
                loadImages(emptyImageURL);
                console.log(errorThrown+":"+textStatus+":"+xhr);
            }
          });

    }
}

function GetNextResultsPage() {
    if (currentQuery != "") {
        currentOffset += imagesPerPage;
        LoadSearchResultsPage(currentOffset,imagesPerPage);
    }
}

function GetPrevResultsPage() {
    if (currentQuery != "") {
        if (currentOffset - imagesPerPage < 0) {
            currentOffset = 1;
        } else {
            currentOffset -= imagesPerPage;
        }
        LoadSearchResultsPage(currentOffset,imagesPerPage);
    }
}

function displayResults(msg) {

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
                'hdurl':imageURL
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
        if(currentQuery != text)
        {
            currentQuery = text;
            currentOffset= 1;
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
    // use ihdurl for high quality images.

    // Generate and print the base 64 image data.
    //nw = $(iid).get(0).naturalWidth;
    //nh = $(iid).get(0).naturalHeight;
    //if (nw == 0 || nh == 0) {
    //    nw = $(iid).width();
    //    nh = $(iid).height();
    //}
    nw = $(iid).width();
    nh = $(iid).height();
    
    imgsrc = $(iid).attr('hdurl');
    console.log(imgsrc);
    var source = "";
    if(type == 'HD')
        source = ihdurl;
    else
        source = isrc;
    
    // Generate and save the 
    $('<img />', {
        id: "selectedPic" + id,
        src: source,
        oncontextmenu: "removeImage('selectedPic" + id + "')",
        'uid': iuid,
        'hdurl':ihdurl,
        'sdurl':isrc,
        'w':Math.round(nw),
        'h':Math.round(nh)
    }).appendTo(selTarget);
    $(selTarget).scrollTop($(selTarget)[0].scrollHeight);
    $("#selectiontitle h3").text(GetSelectedImagesTitle($(selTarget).children().length))
}

function removeImage(id) {
    var iid = "#" + id;
    console.log("Removing : "+(iid));
    $(iid).remove();
    $("#selectiontitle h3").text(GetSelectedImagesTitle($(selTarget).children().length))
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

function displayNotification(text, __className){
    $.notify(text,
    {
        position:'bottom right',
        autoHideDelay:1000,
        className:__className
    });
}


function refreshBrowser(){
    // Reloads the browser in the backend.
    console.log("Reloading Browser");
    $.get(reloadBrowserURL, function(data){
        if(data == "200"){
            $.notify("Browser reloaded",{className:"success"});
        } else {
            $.notify("Browser reloading failed",{className:"error"});
        }
    });
}

function generateDocument(){

    console.log("Generating Document");
    var itemselector = selTarget+" img";
    
    var selectedImages = "";
    selectedimages = {};
    var uid="";
    items = $(itemselector);
    items.each(function(){
        image = $(this);
        imageContent = {}
        uid = image.attr('uid');
        imageContent["uid"] = uid
        imageContent["src"] = image.attr('src');
        imageContent["hdurl"] = image.attr('hdurl');
        imageContent["w"] = image.attr('w');
        imageContent["h"] = image.attr('h');
        imageContent["sdurl"] = image.attr('sdurl');
        selectedimages[uid] = imageContent;
    });

    serverData = JSON.stringify(selectedimages);
    console.log(serverData);

    // Send the json object to the server
    $.ajax({
        type: 'POST',
        dataType: 'text',
        data:serverData,
        contentType: 'application/json; charset=utf-8',
        url: createDocumentURL,
        timeout: requestTimeout,
        success: function(data, textStatus ){
            console.log(data);
        },
        error: function(xhr, textStatus, errorThrown){
            console.log(errorThrown+":"+textStatus+":"+xhr);
        }
      });
}


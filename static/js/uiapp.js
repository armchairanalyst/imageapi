// Web page specific handling here..

// Globals
var imagesPerPage = 9;
var currentOffset = 0;
var currentQuery = "";

$('#loadingimage').hide();
function handleSearch(text) {

        alert("Searching for "+text);
        $('#loadingimage').show();
        return 0;
        // Assumed validated input from calling function
        // Send a post request to nodejs server.
        $.post("/api/search", {
            "query": text
        }).done(function (data) {
            // Handle display of incoming data here.
            console.log(data);
        });
}

function handleInput(event){
    if (event.keyCode == 13) {
        // do something
        performSearch();
    }
}

function handleSearchButton(){
    performSearch();
}

function performSearch(){
    var text = extractSearchText();
    if (text != ""){
        currentQuery = text;
        handleSearch(currentQuery);
    }
}

function extractSearchText(){
    var text = $("#searchinput").val();
    if (text != "" && text.length > 3)
        return text
    
    return "";
    
}



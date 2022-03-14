function TableToJSON(tabId, separator) {
    var myRows = [];
    var $headers = $("th");
    var $rows = $("tbody tr").each(function(index) {
      $cells = $(this).find("td");
      myRows[index] = {};
      $cells.each(function(cellIndex) {
        if(cellIndex<5){
            myRows[index][$($headers[cellIndex]).html()] = $(this).html();
        }
      });
    });

    // Let's put this in the object like you want and convert to JSON (Note: jQuery will also do this for you on the Ajax request)
    return JSON.stringify(myRows);
}
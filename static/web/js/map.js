var map;
var infoWindow;
var markersData = [];

function initialize() {

    var mapOptions = {   
        center: new google.maps.LatLng(22.564889, 78.240017),
        zoom: 4,
        mapTypeId: 'roadmap'
    };

    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    // a new Info Window is created
    infoWindow = new google.maps.InfoWindow();

    // Event that closes the Info Window with a click on the map
    google.maps.event.addListener(map, 'click', function() {
        infoWindow.close();
    });    
    
     //manually reported potholes
    
     var xhReq = new XMLHttpRequest();
     xhReq.open("GET", "/api/complaint", false);
     xhReq.send(null);
     var serverResponse = xhReq.responseText;
     var myObject = eval('(' + serverResponse + ')');
     for (i in myObject)
     {              
       var data = {lat:myObject[i]["Lat"], lng: myObject[i]["Long"] , name: myObject[i]["id"], type: "Manual" , time: myObject[i]["Info"], City:"Severity: "+ myObject[i]["Severity"], color:"green"}
       markersData.push(data)
     }
     
    //automatically detected potholes

     var xhReq = new XMLHttpRequest();
     xhReq.open("GET", "/auto_pothole/get_potholes", false);
     xhReq.send(null);
     var serverResponse = xhReq.responseText;
     var myObject = eval('(' + serverResponse + ')');

     for (i in myObject)
     { 
 
        if(myObject[i]["latitude"] != 0 && myObject[i]["classifier_output"] == 1)
        {         
           var rep = myObject[i]["reporter"]                    
           var color = "red"			
           var model = ""  
	   var date1 = new Date()                   
           var date = new Date(myObject[i]["detection_time"])
	   
	   if(date.getDate() == date1.getDate() && date.getMonth() == date1.getMonth() && date.getYear() == date1.getYear() && rep != 4)
	   {		
		color = "blue"
	   }
	   if(rep == 4)	
	   {
	 color = "green"
	   }
           var data = {lat:myObject[i]["latitude"], lng: myObject[i]["longitude"] , name: myObject[i]["id"], type: "Automated" , time:"Detection Time: " + date.toString().substring(0,24), City:model +"Samples per sec: " +myObject[i]["win_size"].toString() + "  Reporter: "+ rep, color: color}
	   markersData.push(data)
           
        }
     }	
 
    // Finally displayMarkers() function is called to begin the markers creation
    displayMarkers();
   
}


google.maps.event.addDomListener(window, 'load', initialize);



// This function will iterate over markersData array
// creating markers with createMarker function
function displayMarkers(){

    // this variable sets the map bounds according to markers position
    var bounds = new google.maps.LatLngBounds();

    // for loop traverses markersData array calling createMarker function for each marker 
    for (var i = 0; i < markersData.length; i++){

        var latlng = new google.maps.LatLng(markersData[i].lat, markersData[i].lng);
        var name = markersData[i].name;
        var type = markersData[i].type;
        var time = markersData[i].time;
        var City = markersData[i].City;
        var color = markersData[i].color;

        createMarker(latlng, name, type, time, City, color);

        // marker position is added to bounds variable
        bounds.extend(latlng);  
    }

    // Finally the bounds variable is used to set the map bounds
    // with fitBounds() function
    map.fitBounds(bounds);
}

// This function creates each marker and it sets their Info Window content
function createMarker(latlng, name, type, time, City, color){
    var marker = new google.maps.Marker({
        icon: {
        path: google.maps.SymbolPath.CIRCLE,
        strokeColor: color,
        scale: 3
        },
        map: map,
        position: latlng,
        title: name
    });

    // This event expects a click on a marker
    // When this event is fired the Info Window content is created
    // and the Info Window is opened.
    google.maps.event.addListener(marker, 'click', function() {

	if(type == "Automated")
	{
		// Creating the content to be inserted in the infowindow
		var iwContent = '<div id="iw_container">' +
		'<div class="iw_title">' + name + '</div>' +
		'<div class="iw_content">' + type + '<br />' +
		time + '<br />' +
		City + '</div></div>';
	}	

    // including content to the Info Window.
    infoWindow.setContent(iwContent);

    // opening the Info Window in the current map and at the current marker location.
    infoWindow.open(map, marker);
    });
}

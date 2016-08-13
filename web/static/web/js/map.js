var map;
var infoWindow;
var markers = [];
var markersData = [];

function initialize() {

    // Create a map with mapOptions specified
    // var mapOptions = {
    //     center: new google.maps.LatLng(22.564889, 78.240017),
    //     zoom: 4,
    //     mapTypeId: 'roadmap'
    // };

    var mapOptions = {
        // lat long of mumbai
        center: new google.maps.LatLng(19.0760, 72.8777),
        zoom: 11,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        panControl: true,
        scaleControl: true,
        streetViewControl: true,
        overviewMapControl: true,
        rotateControl: true,
        mapTypeControl: true,

        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
            mapTypeIds: [
                google.maps.MapTypeId.ROADMAP,
                google.maps.MapTypeId.TERRAIN
            ]
        },

        zoomControl: true,

        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL
        }
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    // a new Info Window is created
    // infoWindow = new google.maps.InfoWindow();

    // Event that closes the Info Window with a click on the map
    google.maps.event.addListener(map, 'click', function () {
        infoWindow.close();
    });

    /*
     * receiving data from server
     * */
    //manually reported potholes
    var xhReq = new XMLHttpRequest();
    xhReq.open("GET", "/api/complaint", false);
    xhReq.send(null);
    var serverResponse = xhReq.responseText;
    var eventObject = eval('(' + serverResponse + ')');
    for (i in eventObject) {
        var data = {
            lat: eventObject[i]["Lat"],
            lng: eventObject[i]["Long"],
            name: eventObject[i]["id"].toString(),
            type: "Manual",
            time: eventObject[i]["Info"],
            City: "Severity: " + eventObject[i]["Severity"],
            color: "green",
            size: 3
        };
        markersData.push(data)
    }

    //automatically detected potholes
    var xhReq = new XMLHttpRequest();
    xhReq.open("GET", "/auto_pothole/get_potholes", false);
    xhReq.send(null);
    var serverResponse = xhReq.responseText;
    var eventObject = eval('(' + serverResponse + ')');

    for (i in eventObject) {
        var intensityBySpeed = 0;
        if (eventObject[i]["event_speed"] > 5) {
            intensityBySpeed = eventObject[i]["classifier_intensity"] / eventObject[i]["event_speed"]
        }

        if (eventObject[i]["latitude"] != 0 && eventObject[i]["classifier_output"] == 1 && intensityBySpeed > 0.034) {
            var rep = eventObject[i]["reporter"];
            var markerColor = "#820000";
            var markerSize = 3.5;

            if (intensityBySpeed < 0.09) {
                markerColor = "#FF0000";
                markerSize = 3
            }
            if (intensityBySpeed < 0.06) {
                markerColor = "#FA7B7B";
                markerSize = 2.5
            }

            var date = new Date(eventObject[i]["detection_time"]);
            var data = {
                lat: eventObject[i]["latitude"],
                lng: eventObject[i]["longitude"],
                name: eventObject[i]["id"].toString(),
                type: "Automated",
                time: "Detection Time: " + date.toString().substring(0, 24),
                City: "Samples per sec: " + eventObject[i]["win_size"].toString() + "  Reporter: " + rep,
                color: markerColor,
                size: markerSize
            };

            markersData.push(data)
        }
    }

    // Finally displayMarkers() function is called to begin the markers creation
    displayMarkers();

    // Create clustering of markers with specified options
    var options = {
        maxZoom: 17,
        imagePath: '/media/marker_images/m'
    };
    var markerCluster = new MarkerClusterer(map, markers, options);
}
google.maps.event.addDomListener(window, 'load', initialize);


// This function will iterate over markersData array
// creating markers with createMarker function
function displayMarkers() {

    // this variable sets the map bounds according to markers position
    //var bounds = new google.maps.LatLngBounds();

    // for loop traverses markersData array calling createMarker function for each marker
    for (var i = 0; i < markersData.length; i++) {

        var latlng = new google.maps.LatLng(markersData[i].lat, markersData[i].lng);
        var name = markersData[i].name;
        var type = markersData[i].type;
        var time = markersData[i].time;
        var City = markersData[i].City;
        var color = markersData[i].color;
        var size = markersData[i].size;
        createMarker(latlng, name, type, time, City, color, size);

        // marker position is added to bounds variable
        //bounds.extend(latlng);
    }

    // Finally the bounds variable is used to set the map bounds
    // with fitBounds() function
    //map.fitBounds(bounds);
}

// This function creates each marker and it sets their Info Window content
function createMarker(latlng, name, type, time, City, color, size) {
    var marker = new google.maps.Marker({
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            strokeColor: color,
            scale: size
        },
        map: map,
        position: latlng,
        title: name
    });

    markers.push(marker);

    // This event expects a click on a marker
    // When this event is fired the Info Window content is created
    // and the Info Window is opened.
    google.maps.event.addListener(marker, 'click', function () {

        if (type == "Automated") {
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

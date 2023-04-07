
var geocoder;                 // used for searches
var map;                      // main Google Map object
var marker;                   // the moveable pin
var lastsent = 'FIRST';       // last request sent
// var busy = 0;
var requests = new Array();   // requests to process
var current_request = null;

var mtype = {
  HYBRID: google.maps.MapTypeId.HYBRID,
  ROADMAP: google.maps.MapTypeId.ROADMAP,
  SATELLITE: google.maps.MapTypeId.SATELLITE,
  TERRAIN: google.maps.MapTypeId.TERRAIN
}

function initialize() {

    // create map, marker, geocoder
    // bind control action events
    // start polling timer

    geocoder = new google.maps.Geocoder();
    var myOptions = {
        zoom: 3,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    }
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    var loc = new google.maps.LatLng(45., -45);
    map.setCenter(loc);
    marker = new google.maps.Marker({
        map: map,
        position: loc,
        draggable: true
    });
    google.maps.event.addListener(marker, "dragend", moveMarker);
    google.maps.event.addListener(map, "zoom_changed", moveMarker);
    google.maps.event.addListener(map, "bounds_changed", moveMarker);
    google.maps.event.addListener(map, "maptypeid_changed", moveMarker);
    google.maps.event.addListener(map, "dblclick", popMarker);

    jQ("#geoquery").keypress(findAddress);
    jQ("#descrip").keypress(newDescrip);
    jQ("#send").click(function(){sendPos(lastsent);});

    setTimeout(request_update, 1000);

}
function request_update() {                                                   
    // check for update periodically                               
    jQ.getJSON("getMessage", {}, process_update);                                               
}
function process_update(data) {
    // callback for request_update
    // add requests to queue, act on first

    if (data.__msg_type == "shutdown") {
        jQ("body").text("GeoTagger exit");
        return;
    }
    if (data.__msg_type == "request_position"
        || data.__msg_type == "show_position") {
        requests[requests.length] = data;
        if (!current_request) {
            next_request();
        }
    }
    // busy = 0;
    setTimeout(request_update, 1000);
}
function next_request() {

    // actual request processing

    if (requests.length) {
        current_request = requests.splice(0,1)[0];  // removes from list
        var prompt = "Please locate ";
        if (current_request.__msg_type == "show_position") {
            prompt = "";
        }
        jQ("#response").text(prompt+current_request.description)
          .animate({opacity: 0.0}, 750)
          .animate({opacity: 1.0}, 750)
          .animate({backgroundColor: 'pink'});
        jQ("#descrip").get(0).value = current_request.description;
        if (current_request.__msg_type == "show_position") {
            relocateMarker(current_request);
            sendPos(current_request);
            current_request = null;
        }
        moveMarker(0,0);  // init. current_request and set lastsent
    } else {
        jQ("#response").text("");
        current_request = null;
        moveMarker(0,0);  // init. current_request and set lastsent
        // in particular make sure we don't use an old current_request
        // referenced by lastsent, as it has a bogus __msg_type setting
    }
}
function findAddress(e) {
    if (e.which != 13) {
        return;
    }
    var address = jQ("#geoquery").get(0).value;

      geocoder.geocode( { 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
          map.setCenter(results[0].geometry.location);
          marker.setPosition(results[0].geometry.location);
        } else {
          alert("Geocode was not successful for the following reason: " + status);
        }
      });
}
function newDescrip(e) {
    moveMarker(0, 0);
}
function rnd(x,n) {
  return Math.round(x * Math.pow(10,n)) / Math.pow(10,n);
}
function moveMarker(e, inc) {

    // handle marker being moved...

    if (inc == null) {
        inc = 0;
    }

    var pos;
    if (current_request) {
        pos = current_request;
    } else {
        pos = {};
    }
    pos.lat = marker.getPosition().lat();
    pos.lng = marker.getPosition().lng();
    pos.zoom = map.getZoom()+inc;
    pos.maptype = map.getMapTypeId();
    pos.description = jQ("#descrip").get(0).value;
    var txt = rnd(pos.lat,6) +
              " " + rnd(pos.lng,6) +
              " " + pos.zoom +
              " " + pos.maptype;
    jQ("#info").text(txt);
    lastsent = pos;
}
function relocateMarker(data) {
    var loc = new google.maps.LatLng(data.lat, data.lng);
    var zoom = data.zoom;  // see below
    if (data.maptype) {
        map.setMapTypeId(mtype[data.maptype.toUpperCase()]);
    }
    map.setCenter(loc);    // callback clobbers values in data
    if (zoom) {
        map.setZoom(zoom);
    }
    marker.setPosition(loc);
}
function popMarker(e) {
    marker.setPosition(e.latLng);
    if (map.getZoom() < 19) {
        moveMarker(0, 1);
    } else {
        moveMarker(0, 0);
    }
}
function sendPos(pos) {
    if (pos == "FIRST") {
        alert("Select a position first");
        return;
    }
    pos.description = jQ("#descrip").get(0).value;  // else lose last char.
    var response = jQ.getJSON('sendPos', {data: jQ.toJSON(pos)}); // , gotResponse);
    next_request();
}
function gotResponse(data) {
    // jQ("#response").text(data);
}


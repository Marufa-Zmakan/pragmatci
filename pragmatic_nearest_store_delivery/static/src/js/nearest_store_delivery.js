odoo.define("pragmatic_nearest_store_delivery.nearest_store_delivery", function(require) {
'use strict';

//    var rpc = require('web.rpc');
//    var ajax = require('web.ajax');
//    var core = require('web.core');
//    var translation = require('web.translation');
//    var _t = translation._t;

    function createMarker(map, position, icon_url, infowindow, geocoder) {
        const marker = new google.maps.Marker({
            map: map,
            position: position,
            icon: {
                 url: icon_url,
                 size: new google.maps.Size(25, 25)
            }
        });
        google.maps.event.addListener(marker, "click", () => {
            geocoder.geocode({'latLng': marker.getPosition()}, function(results, status){
                if(status == google.maps.GeocoderStatus.OK) {
                    if(results[0]) {
                        console.log("Formatted address: ",results[0].formatted_address);
                        infowindow.setContent(results[0].formatted_address);
                        infowindow.open(map, marker);
                    }
                }
            });
        });
    }

    function addStoreMarkers(map, infowindow, geocoder) {
        let storeAddrs = $("#stores").val();
        try {
            storeAddrs = JSON.parse(storeAddrs);
        } catch(e) {
            alert(e);
            return;
        }
        const storeIcon = "/pragmatic_nearest_store_delivery/static/src/img/store-icon.png";
        storeAddrs.forEach(function(store) {
            createMarker(map, store, storeIcon, infowindow, geocoder);
        });
    }

    function initNearestStoreMap(){
        console.log("InitNearestStoreMap === ");
        const infowindow = new google.maps.InfoWindow();
        const geocoder = new google.maps.Geocoder();
        let custAddr = $("#customer").val();
        try{
            custAddr = JSON.parse(custAddr);
        } catch(e) {
            alert(e);
            return;
        }
        const map = new google.maps.Map(document.getElementById('store-map'), {
            zoom: 12,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            center: custAddr
        });
        const partnerIcon = '/website_google_map/static/src/img/partners.png';
        createMarker(map, custAddr, partnerIcon, infowindow, geocoder);
        addStoreMarkers(map, infowindow, geocoder);
    }

    $(document).ready(function() {
        // load google map
        if (location.pathname.includes('/page/store/map/view')) {
            initNearestStoreMap();
        }
    });
});
odoo.define("pragmatic_odoo_delivery_boy.update_driver_location", function(require) {
    'use strict';

    var session = require('web.session');


    $(document).ready(function() {
    var path_name = window.location.pathname
    path_name = JSON.stringify(path_name);

    if (path_name.indexOf("/pos") !== 1)
    {

        function update_current_driver_location() {
            console.log("In update_current_driver_location")

            if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position)
        {console.log('getCurrentPosition',position.coords.latitude,position.coords.longitude)
        var pos = {
                        'lat': position.coords.latitude,
                        'lng': position.coords.longitude
                    };

                    $.ajax({
                        url: "/update-current-driver-location",
                        async: true,
                        timeout: 4000,
                        data: pos,
                        success: function(res) {
                            let data = JSON.parse(res)
                            $('#route_values').val(JSON.stringify(data['routes']))
                        },
                    });

                    },
        function(err){},
        {enableHighAccuracy: true,maximumAge: 0});

//                navigator.geolocation.getCurrentPosition(function(position) {
//
//                });
            }



        }

        var counter_interval = setInterval(function() {

            if (session.user_id || session.uid) {

                $.ajax({
                    type: "GET",
                    url: '/check_is_driver',
                    cache: "false",
                    success: function(res) {
                        if(res){
                        var res = JSON.parse(res);

                        if (res.flag == 1) {
                            update_current_driver_location()
                        }
 }
                    }
                });

            }

        }, 60000);


        if (!session.user_id && !session.uid) {
            clearInterval(counter_interval);
            console.log('Interval Cleared')
        }

    }
    });
});
odoo.define('home_delivery_odoo_pos_website_mobile_pragtech.floors', function (require) {
"use strict";

    var gui = require('point_of_sale.gui');
    var floors = require('pos_restaurant.floors');
    var chrome = require('point_of_sale.chrome');
    var models = require('point_of_sale.models');
    var core = require('web.core')
    var QWeb = core.qweb;


    var TakeAwayHomeDeliveryButtons = floors.FloorScreenWidget.include({

        init: function(parent, options) {
            this._super(parent, options);
            QWeb.render('FloorScreenWidget',{widget:this});
        },

        renderElement: function(){
            var self = this;
            this._super();

//            self.$('.take_away_button').click(function() {
//                self.pos.config.iface_floorplan = false;
//                var orders = self.pos.get_order_list();
//                var take_away_orders = orders.filter(order => order.delivery_type === 'take_away');
//                if(!take_away_orders.length) {
//                    self.pos.table = null;
//                    self.pos.add_new_order();
//                    var order = self.pos.get_order();
//                    if(order){
//                        order.set_delivery_type("take_away");
//                        order.set_delivery_type_name("Take Away");
//                    }
//                }else{
//                    self.pos.set_order(take_away_orders[0]);
//                }
//                self.pos.config.iface_floorplan = true;
//                self.gui.show_screen('products');
//            });


            self.$('.home_delivery_button').click(function() {
                            console.log("In js on click home_delivery_button")

                self.pos.config.iface_floorplan = false;
                var orders = self.pos.get_order_list();
                            console.log("orders: ",orders)

                var home_delivery_orders = orders.filter(order => order.delivery_type === 'home_delivery');
                            console.log("home_delivery_orders: ",home_delivery_orders)
                            console.log("home_delivery_orders: ",home_delivery_orders.length)

                if(!home_delivery_orders.length)
                {
                                            console.log("home_delivery_orders: ",home_delivery_orders)

                    self.pos.table = null;
                    self.pos.add_new_order();
                    var order = self.pos.get_order();
                                                        console.log("In if order take away: ",order)

                    if(order){
                                                                                console.log("In if order22222222222")

                        order.set_delivery_type("home_delivery");
                        order.set_delivery_type_name("Home Delivery");
                    }
                }else{
                    self.pos.set_order(home_delivery_orders[0]);
                }
                self.pos.config.iface_floorplan = true;
                self.gui.show_screen('products');
            });
        },
    });

    var _super_order_model = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(){
            _super_order_model.initialize.apply(this,arguments);
        },
        set_delivery_type: function(delivery_type){
            this.delivery_type = delivery_type;
        },
        get_delivery_type: function(){
            return this.delivery_type;
        },
        set_delivery_type_name: function(delivery_type_name) {
            this.delivery_type_name = delivery_type_name;
        },
        get_delivery_type_name: function(){
            return this.delivery_type_name;
        },
        export_as_JSON: function () {
            var json = _super_order_model.export_as_JSON.apply(this, arguments);
            json.delivery_type = this.get_delivery_type() || "default";
            json.delivery_type_name = this.get_delivery_type_name() || "Default";
            return json;
        },

        init_from_JSON: function (json) {
            _super_order_model.init_from_JSON.apply(this, arguments);
            this.delivery_type = json.delivery_type || "default";
            this.delivery_type_name = json.delivery_type_name || "Default";
        },

        export_for_printing: function() {
            var json = _super_order_model.export_for_printing.apply(this,arguments);
            json.delivery_type = this.get_delivery_type();
            return json;
        },

    });

    var CustomFloorsBackButton = chrome.OrderSelectorWidget.include({

        renderElement: function(){
            var self = this;
            this._super();

            self.$('.main_floor_button').click(function() {
                self.gui.show_screen('floors')
            })

         }

    })


    return {
//        TakeAwayHomeDeliveryButtons: TakeAwayHomeDeliveryButtons,
        CustomFloorsBackButton: CustomFloorsBackButton,
    }

   });
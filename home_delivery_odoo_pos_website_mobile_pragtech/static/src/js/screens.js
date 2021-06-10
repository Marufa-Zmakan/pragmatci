odoo.define('home_delivery_odoo_pos_website_mobile_pragtech.screens', function (require) {
"use strict";


    var gui = require('point_of_sale.gui');
    var pos_screens = require('point_of_sale.screens')
    var PopupWidget = require('point_of_sale.popups');
    var rpc = require('web.rpc');
    var models = require('point_of_sale.models');


//    models.load_fields("account.journal", "home_delivery_journal_user");


//    models.load_models({
//        model: 'res.groups',
//        fields: [], // fields that will be used from your model
//        domain: function(self){ return [['name','=','POS Delivery Person']]; }, // domain filter
//        loaded: function(self,data){
//        // a function that will be executed on loading
//        console.log("GRP:::::::::::::",data)
//        self.group_s = data;}
//    });

//    models.load_models({
//        model: 'res.users',
//        fields: ['id','name','login'], // fields that will be used from your model
//        domain: function(self){ return [['groups_id','=',self.group_s[0].id]]; }, // domain filter
//        loaded: function(self,data){
//        // a function that will be executed on loading
//        console.log("DATA:::::::::::::",data)
//        self.users_lst = data;}
//    });

      models.load_models({
        model: 'res.partner',
        fields: [], // fields that will be used from your model
        domain: function(self){ return [['is_driver','=',true]]; }, // domain filter
        loaded: function(self,data){
        // a function that will be executed on loading
//        console.log("DATA:::::::::::::",data)
        self.users_lst = data;}
    });



    var ShowHomeDeliveryButton = pos_screens.ActionButtonWidget.extend({

        template : 'ShowHomeDeliveryButton',

        init : function(parent, options) {
			options = options || {};
			this._super(parent, options);
//			console.log("Pop up window initialization");
		},

		button_click: function(){
          var self = this;
          this.gui.show_popup('home_delivery_order');
        },


    });


    var HomeDeliveryOrderPopupWidget = PopupWidget.extend({
        template: 'HomeDeliveryOrderPopupWidget',
        init : function(parent, options) {
			options = options || {};
//			console.log("Initailization::::::::;;;")
			this._super(parent, options);
		},

		events: {
            'click .button.cancel': 'click_cancel',
            'click .button.clear': 'click_clear',
            'click .button.create_home_delivery': 'create_home_delivery',
            'click .button.other_info_button' : 'click_other_info',
            'click .button.address_button' : 'click_address',
        },


		renderElement : function() {
			var self = this;
//			console.log("In render of Lock")
			this._super();
			 $("#customer-shipping-address").hide();
			 $('#other_information_div').hide();
			self.$('.address_button').click(function() {
//				console.log("click_address Clicked");
				self.click_address();
			});
			self.$('.other_info_button').click(function() {
//				console.log("click_other_info Clicked");
				self.click_other_info();
			});
            self.$("#address_checkbox").click(function() {
//                console.log("address_checkbox",$(this).is(":checked"))
                self.show_shipping_address();
            });
            self.$('#datetimepicker1').datetimepicker();


		},

        click_other_info: function(){
//           $(".other_info_button").css("background-color","#14e871");
            $(".other_info_button").css("background-color","#df3957");
            $(".address_button").css("background-color","");
           $("#customer-shipping-address").hide();
           $("#default_shipping_address").hide();
           $("#other_information_div").show();
        },

        click_address: function(){
//            $(".address_button").css("background-color","#14e871");
           $(".address_button").css("background-color","#df3957", "color","#fff");
           $('.other_info_button').css('background-color', '');
           $("#default_shipping_address").show();
           $("#other_information_div").hide();

            if($('#address_checkbox').is(":checked")) {
                $("#customer-shipping-address").show(300);
            } else {
                $("#customer-shipping-address").hide(200);
            }
        },

        show_shipping_address : function()
        {
            var selected_customer =this.pos.get_order().get_client();
//            console.log("SELECTED CUSTOMER::;;;;;;",selected_customer)
            if($('#address_checkbox').is(":checked"))
            {
                /*if(selected_customer != null)
                {
                   $('.customer-address-name').val(selected_customer.name)
                   $('.customer-address-email').val(selected_customer.email)
                   $('.customer-address-mobile').val(selected_customer.mobile)
                   $('.customer-address-locality').val(selected_customer.street)
                   $('.customer-address-street').val(selected_customer.street2)
                   $('.customer-address-city').val(selected_customer.city)
                   $('.customer-address-zip').val(selected_customer.zip)
                }*/
               $('.customer-address-name').prop('required', true);
               $('.customer-address-email').prop('required', true);
               $('.customer-address-mobile').prop('required', true);
               $('.customer-address-locality').prop('required', true);
               $('.customer-address-city').prop('required', true);
               $('.customer-address-zip').prop('required', true);

               $("#customer-shipping-address").show(300);
            }
            else
             {
               $('.customer-address-name').prop('required', false);
               $('.customer-address-email').prop('required', false);
               $('.customer-address-mobile').prop('required', false);
               $('.customer-address-locality').prop('required', false);
               $('.customer-address-city').prop('required', false);
               $('.customer-address-zip').prop('required', false);

               $("#customer-shipping-address").hide(200);
            }
        },

        click_cancel: function(){
            this.gui.close_popup();
            if (this.options.cancel) {
                this.options.cancel.call(this);
            }
        },

        click_clear: function(){

            if($("#customer-shipping-address").is(":visible"))
            {
                $('#customer-shipping-address').find('input').val('');

            }
            else if($("#other_information_div").not(":visible"))
            {
                 $('#other_information_div').find('input,select').val('');
            }

        },

        check_required_inputs : function() {
            var required = $('input').filter('[required]:visible');
            var allRequired = true;
            required.each(function(){
                if($(this).val() == ''){
//                    alert("Please fill all the required fields")
                    allRequired = false;
                    return false

                }
            });
            if(!allRequired)
            {
                return false
            }
            else
            {
                return true
            }

        },

        create_home_delivery: function(e){
            e.preventDefault();
            console.log("IN CREATE HOME DELIVERY::::::::::",this.pos.get_order())
            var order = this.pos.get_order();
            order.set_delivery_type("home_delivery");
            order.set_delivery_type_name("Home Delivery");
            var line_products = _.map(order.get_orderlines(), function (line) {return line.product; });
//            console.log("PRODUCTS:::::::::",line_products);
            var product_lst = []
            var lines=order.get_orderlines()


            for(var i =0; i < lines.length; i++)
            {
//                console.log(line_products[i].id);
                var line_products = lines[i].product;
//                console.log("LNE PROD",line_products)
                if(line_products)
                {
                    var product = {}
                    product['id'] = line_products.id
                    product['categ_id'] = line_products.categ_id
                    product['list_price'] = line_products.list_price
                    product['lst_price'] = line_products.lst_price
                    product['standard_price'] = line_products.standard_price
                    product['product_tmpl_id'] = line_products.product_tmpl_id
                    product['display_name'] = line_products.display_name
                    product['uom_id'] = line_products.uom_id
                    product['qty'] = lines[i].get_quantity()
                    product['price_unit'] = lines[i].get_unit_price()
                    product_lst.push(product)
                }

             }

            var check_req = this.check_required_inputs()
//            console.log("CHECK REQ::::::::::::;;;",check_req)

            var create_delivery ={}
            var shipping_address = {}
            var ship_to_diff_addr = false
            var selected_customer =order.get_client();
//            console.log("SELECTED CUSTOMER::;;;;;;",selected_customer)
            var order_name = order.name
//            console.log("ORDER NAME",order_name)
            if(selected_customer == null)
            {
               alert("Set a customer first")
            }
            else if(order.get_orderlines().length == 0)
            {
               alert("Add a product")
            }
            else if(check_req == false)
            {
                alert("Please fill the *required fields")
            }
            else
            {
                /* ################################################################# */

                create_delivery['partner_id'] = selected_customer.id
                create_delivery['name'] = order_name
                create_delivery['product_lst'] = product_lst
                create_delivery['session_id'] = this.pos.pos_session.id
//                create_delivery['cashier'] = this.pos.get_cashier().id;
                create_delivery['cashier'] = this.pos.get_cashier().user_id[0];
                create_delivery['delivery_type'] = order.delivery_type;

                $('#other_information_div').find('input, select, textarea').each(function() {
                    console.log("ALL::::::::::::::;;;",$(this).attr('name'));
//                    console.log("ALL details2222: ",$(this).attr('id'));
                                        console.log("ALL SHIPPING ADDR id::::::::::::::;;;",$(this).attr('id'));


                    if($(this).attr('id') == 'delivery_person')
                    {
//                        alert($(this).find("option:selected").text()+' clicked!');
//                        console.log("lLLLLLLLLLLLLLLLL",parseInt($(this).val()))
                        create_delivery['delivery_person'] = parseInt($(this).val())
                    }
                    if($(this).attr('id') == 'delivery_datetime')
                    {
                        if($.trim($(this).val()) != ""){
//                            console.log(moment($(this).val()).format('YYYY-MM-DD, HH-mm-ss'));
                            create_delivery['delivery_time'] = $(this).val()
                            create_delivery['display_delivery_time'] = $(this).val()
                        }
                    }
                    if($(this).attr('id') == 'delivery_note')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['order_note'] = $(this).val()
                        }
                    }
                });
                $('#customer-shipping-address').find('input').each(function(){
//                    console.log("1232323: ",$(this))
                    console.log("ALL SHIPPING ADDR::::::::::::::;;;",$(this).attr('name'));
                    if($(this).attr('name') == 'customer_name')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['customer_name'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }
                    if($(this).attr('name') == 'mobile')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['phone'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }
                    if($(this).attr('name') == 'email')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['email'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }
                    if($(this).attr('name') == 'locality')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['street'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }
                    if($(this).attr('name') == 'street')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['street2'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }
                    if($(this).attr('name') == 'city')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['city'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }
                    if($(this).attr('name') == 'zip')
                    {
                        if($.trim($(this).val()) != ""){
                            create_delivery['zip'] = $(this).val()
                            ship_to_diff_addr = true
                        }
                    }


                });
//                create_delivery['shipping_address'] = shipping_address
                create_delivery['ship_to_diff_addr'] = ship_to_diff_addr
                 if($('#delivery_person').find("option:selected").text() != "")
                {
                    this.pos.delivery_person_name = $('#delivery_person').find("option:selected").text().trim();
                }
                this.pos.delivery_details = create_delivery
//                console.log("this.pos;;;;;;;;;;;;;;;;;;;;",this.pos)
                console.log("CREATE DELIVERY DICT:::::::::::",create_delivery)
//                console.log("POS OBJECT::::::::::::::::::;",this.pos.delivery_details)
                rpc.query({
                    route: '/create/homedelivery',
                    params: create_delivery,
                }).then(function(result){
//                    console.log("RESULT::::::::::",result)
                    if(result == false)
                    {
                        alert('Something went wrong')
                    }
                    else if(result == "already created")
                    {
                        alert("Delivery Order already exists/created")
                    }
                    else if(result == true)
                    {
                        alert('Delivery Order created successfully')
                    }


                });

                this.gui.close_popup();

            }

        },

    });




gui.define_popup({name:'home_delivery_order', widget: HomeDeliveryOrderPopupWidget});

    pos_screens.define_action_button({
    'name': 'home_delivery',
    'widget': ShowHomeDeliveryButton,
    'condition': function(){
        return this.pos.config.home_delivery;
    },
    });

return {
    ShowHomeDeliveryButton: ShowHomeDeliveryButton,
    HomeDeliveryOrderPopupWidget :HomeDeliveryOrderPopupWidget,
}

});

odoo.define("home_delivery_odoo_pos_website_mobile_pragtech.control_app", function(require){
	"use strict";

	$(document).ready(function(){

	    $('#driver_message').hide();

             // Collect Payment
        $('.collect_payment_pos').click(function(e){
            var order_id = $(this).attr('order_id');
            var order_source = "ERP";
            if($(this).data('orderSource') == "POS")
            {
                order_source = $(this).data('orderSource');
            }
            var value = {
                "order_id" : order_id,
                "order_source" : order_source,
            }
            $.ajax({
                url : "/collect-payment-pos",
                data : value,
                cache : "false",

                success : function(res) {
                    var vals = $.parseJSON(res);
                    window.location.reload();
                },

                Error : function(x, e) {
                    alert("Some error");
                }
            });
        });

	    $('.joblist_cancel_pos_order').on('click', function(){
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id,
	    	}
	    	$.ajax({
	    		url: "/cancel/posorder",
	    		data: data,
	    		success: function(res) {
	    			var res = JSON.parse(res);
	    			if(res.status){
	    				window.history.back();
	    			}
	    		},
	    		Error : function(x, e) {
	    			alert("Some error");
	    		}
	    	});
	    });

	    $('.joblist_delivered_pos_order').on('click', function(){
	        var elem = document.getElementById("delivered_button");
            elem.value = "BACK AT RESTAURANT";
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id,
	    	}
	    	$.ajax({
	    		url: "/delivered/pos_order",
	    		data: data,
	    		success: function(res) {
	    			var res = JSON.parse(res);
	    			if(res.status){
	    				window.history.back();
	    			}
	    		},
	    		Error : function(x, e) {
	    			alert("Some error");
	    		}
	    	});
        });

        $('.joblist_cancel_pos_order_driver').on('click', function(){
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id
	    	}
	    	$.ajax({
	    		url: "/driver/cancel/pos_order",
	    		data: data,
	    	})
	    	.done(function(res){
                var res = JSON.parse(res);
                if(res.status){
                    window.history.back();
                }
            })
            .fail(function(resp){
                alert("Something went wrong")
            });
	    });

	    $('.joblist_pos_order_pay_now').on('click', function (){
            var elem = document.getElementById("pay_now_button1");
            var order_number = document.getElementById("order_number").value
            elem.value = "PAID";
            var payment_status = elem.value
            var value = {
            'payment_status': payment_status,
            'order_number': order_number
            }

             $.ajax({
                url : '/paid/pos_order/status',
                data : value
            })
            .done(function(res){
               $('.joblist_pos_order_pay_now').hide()
               elem.value = "PAID";
            })
            .fail(function(resp){
                alert("Something went wrong!!!!!")
            })
         });

         $('#selectPayment').change(function(event){
            var selectPayment = document.getElementById("selectPayment")
            var order_number = document.getElementById("order_number").value
            var selectedValue = selectPayment.options[selectPayment.selectedIndex].value;
            var value = {
            'selectedValue': selectedValue,
            'order_number': order_number
            }
            $.ajax({
                url : '/select/payment/pos/status',
                data : value
            })
	    });

        //Load driver on modal

	    $('#driver_msg_issue').on('show.bs.modal', function(e) {
	    	$('#driver_message').show();
	    });
        	    $('#select_driver').on('show.bs.modal', function(e) {
	    	$('#loading-indicator').show();
	        var $modal = $(this);
	        var warehouse_id = e.relatedTarget.id;
	        var order_id = $(e.relatedTarget).attr('order_id');
			var value = {
				"warehouse_id" : warehouse_id,
			}
			$.ajax({
				url : "/get-driver",
				data : value,
				cache : "false",
				success : function(res) {
					var html = '<input type="hidden" name="warehouse_id" value="'+warehouse_id+'"/>'
					var result = $.parseJSON(res);

					$.each(result,function(key,value){
						html +="<input id="+order_id+" type='radio' name='driver_radio' value='"+value['id']+"' data-text='"+value['name']+"'>"+value['name']+"</input><br/>"
					});
					var count = 0;
						$modal.find('.driver-list').html(html);
					$('#loading-indicator').hide();
				},
				Error : function(x, e) {
					alert("Some error");
					$('#loading-indicator').hide();
				}
			});
	    });


//	    $('#driver_msg_issue .confirm_driver').click(function(e){
//	        console.log("In issue js")
//            var message_driver = $("#pos_message_driver").val()
//			var driver_id = parseInt($('input[name=driver_radio]:checked').val())
//			var order_id = parseInt($('input[name=driver_radio]:checked').attr('id'))
//			var warehouse_id = parseInt($('input[name=warehouse_id]').val())
//			var driver_name_tr = $('#driver_name').val();
//			var value = {
//					"payment_status_driver" : message_driver,
//            }
//            console.log("value:: ",value)
//            $.ajax({
//                url : "/pos/driver/issue/message",
//                data : value,
//                cache : "false",
//                success : function(res) {
//                    var vals = $.parseJSON(res)
//                    var new_driver_name=$('input[name=driver_radio]:checked').data('text');
//                    $('#'+driver_name_tr +' > #order_driver_name > span').text(driver_name_tr);
//                    $('#driver_msg_issue').modal('hide');
//                    alert("Message Sent!!!");
////						window.location="/page/manage-sale-order-delivery";
//                },
//                Error : function(x, e) {
//                    alert("Some error");
//                }
//            });
//		});
        	$('.pos_confirm_driver').click(function(e){
//        	    console.log("In confirm_driver")
                var pos_delivery_number = $("#pos_delivery_number").val()
                var driver_message = $("#pos_message_driver").val()

    			var value = {
					"pos_delivery_number" : pos_delivery_number,
					"driver_message" : driver_message,
				}
//				console.log("value console driver message:: ",value)
//
				$.ajax({
					url : "/pos/driver/issue/message",
					data : value,
					cache : "false",
					success : function(res) {
						window.location = '/page/job/list/driver'
					},
					Error : function(x, e) {
						alert("Some error");
					}
				});
		});


        $('.driver_joblist_back').on('click',function(){
            window.history.back()
        })

        $('.joblist_back').on('click',function(){
            window.history.back();
        })

               $('.pos_joblist_accept_order').on('click',function()
       {
           var order_number = document.getElementById("order_number").value
            var value = {
					"delivery_order_status" : "accept",
					"order_number" : order_number
			}
            $.ajax({
                    url : '/pos/order/driver_accept_reject_status',
                    data : value,
                    success: function(res) {
                        var vals = $.parseJSON(res)
                        if (vals['status'] == true)
                        {
                            window.location.reload();
                        }
                    }
            });
       });

               $('.pos_joblist_delivered_order').on('click', function (){
	     	var elem = document.getElementById("paid_delivered_button");
            elem.style.display = "none";
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id,
	    	}
	    	$.ajax({
	    		url: "/pos/delivered/order",
	    		data: data,
	    		success: function(res) {
	    			var res = JSON.parse(res);
	    			if(res.status){
	    				window.history.back();
	    			}
	    		},
	    		Error : function(x, e) {
	    			alert("Some error");
	    		}
	    	});
	    });

        	    $('#start_delivery').click(function(){

	        var pickings = $("#picking_ids").val();
	        var pos_orders = $("#pos_ids").val();

			var value = {
					'pickings' : pickings,
					'pos_orders': pos_orders,
					'total_distance' : $("#total_distance").val(),
				}

	        $.ajax({
					url : "/update_pickings",
					timeout: 4000,
					data : value,
					success : function(res){}
				});

			var value = {
					'start' : 1,
				}

            location.reload()
	        $.ajax({
					url : "/page/job/list/driver",
					timeout: 4000,
					data : value,
					success : function(res){}
				});
        })


	});

});
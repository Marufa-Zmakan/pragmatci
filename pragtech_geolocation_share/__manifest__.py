# -*- coding: utf-8 -*-
#################################################################################
{
  "name"                 :  "Website Customer Geolocation Address",
  "summary"              :  """Share geolocation on shipping page""",
  "category"             :  "website",
  'version'              : '13.0.5',
  "sequence"             :  1,
  'license'              : 'AGPL-3',
  'author'               : 'Pragmatic TechSoft Pvt Ltd.',
  'website'              : 'http://www.pragtech.co.in',
  "description"          :  """This module works very well with latest version of Odoo 13.0
--------------------------------------------------------------""",
  "depends"              :  ['website_sale'],
  "data"                 :  [

                              'views/website_templates.xml',
                              'views/template_checkout.xml',
                              'views/res_partner_view.xml',
                              'data/data_geolocation.xml',



                             ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,

}
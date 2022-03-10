from itertools import product
from odoo import models, fields, api
import json




class ProductProduct(models.Model):
    _inherit = 'product.product'

    hfoc_lot_html = fields.Html('Lot')
    hfoc_total_in_receipt = fields.Float('Por Llegar')
    hfoc_total_sales = fields.Float('Vendido')
    hfoc_ref_sales = fields.Html('Ventas')
    hfoc_ref_sales_list = fields.Text('Sale List')
    hfoc_lot_list = fields.Text('Lot list')


    def action_hfoc_open_product_lot(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_production_lot_form")
        list_lot = (self.hfoc_lot_list).replace(" ","").replace("]","").replace("[","").replace("'","").split(",")
        
        action['domain'] = [('product_id', '=', self.id),('id','in',list_lot)]
        action['context'] = {
            'default_product_id': self.id,
            'set_product_readonly': True,
            'default_company_id': (self.company_id or self.env.company).id,
        }
        action['target'] = 'new'
        action['flags'] = {'action_buttons': False}
        return action
    
    def action_hfoc_open_sales(self):
        self.ensure_one()        

        list_sales = (self.hfoc_ref_sales_list).replace(" ","").replace("]","").replace("[","").replace("'","").split(",")
        sales_ids = self.env['sale.order'].search([ ('name', 'in', list_sales ),('invoice_status','!=','invoiced') ])

        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        
        action['domain'] = [('id', 'in', sales_ids.ids)]
        action['context'] = {}
        action['target'] = 'new'
        action['flags'] = {'action_buttons': False}
        return action



class HfocStockReport(models.TransientModel):
    _name = 'hfoc.stock.report'
    _description = "hfoc stock report"

    name = fields.Char('Name', default="search product")
    search = fields.Char('Filter')
    company_id = fields.Many2one('res.company', 'Company')

    product_ids = fields.Many2many('product.product', string='Informacion Productos', readonly=True , ondelete='restrict', copy=False )


    def search_product_report(self):
        list_ids = []
        domain = [  ('name', 'ilike', self.search),
                    ('sale_ok', '=', True),
                    ('company_id','=',self.company_id.id or False),
                    ('detailed_type','=','product'),('active','=',True)]
        product_ids = self.env['product.product'].search(domain)
        for product in product_ids:
            if product.virtual_available != 0.00 or product.qty_available != 0.00:
                list_ids.append(product.id)

        
        
        self.product_ids = self.env['product.product'].search([('id','in',list_ids)])
        
        for line in self.product_ids:
            line.hfoc_lot_html = ''
            content = ''
            content_sale = ''
            count = 0
            content_sale_list = []
            content_lot_list = []
            hfoc_total_in_receipt = 0
            for lot in self.env['stock.production.lot'].search([('product_id', '=', line.id),('quant_ids','!=', False)]):                
                # list_lot.append(lot.name)
                if lot.product_qty > 0:
                    content_lot_list.append(lot.id)
                    if count != 5:
                        content += "<span style='color:white;padding: 2px 7px 1px 7px;background: #1b853b;border-radius: 10.5px;margin: 3px;' >"+lot.name+"</span>"
                    else:
                        content += "<br/><span style='color:white;padding: 2px 7px 1px 7px;background: #1b853b;border-radius: 10.5px;margin: 3px;' >"+lot.name+"</span>"
                    if count == 5:
                        count = 0
                    else:
                        count += 1
            line.hfoc_lot_list = content_lot_list
            line.hfoc_lot_html = content
            hfoc_total_sales = 0
            count = 0
            for lts in self.env['sale.order.line'].search([('product_id', '=', line.id),('state','in', ('sale','done')),  ('company_id','=', self.env.company.id ), ('invoice_status','!=','invoiced') ]):
                content_sale_list.append(lts.order_id.name.replace(" ",""))
                hfoc_total_sales += lts.product_uom_qty
            
                if count != 5:
                    content_sale += "<span style='color:white;padding: 2px 7px 1px 7px;background: #1b853b;border-radius: 10.5px;margin: 3px;' >"+lts.order_id.name.replace(" ","")+"</span>"
                
                else:
                    content_sale += "<br/><span style='color:white;padding: 2px 7px 1px 7px;background: #1b853b;border-radius: 10.5px;margin: 3px;' >"+lts.order_id.name.replace(" ","")+"</span>"
                
                if count == 5:
                    count = 0
                else:
                    count += 1
            line.hfoc_ref_sales_list = content_sale_list
            line.hfoc_ref_sales = content_sale
            line.hfoc_total_sales = hfoc_total_sales


            for stock_in in self.env['stock.move'].search([('product_id', '=', line.id),('state','not in', ('draft','done','cancel')),('reference','ilike', '/IN/')]):
                hfoc_total_in_receipt += stock_in.product_uom_qty

            line.hfoc_total_in_receipt = hfoc_total_in_receipt
                



    






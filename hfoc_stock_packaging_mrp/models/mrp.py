from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, Warning


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    hfoc_hide_package = fields.Boolean('Hide Package', copy=False)
    hfoc_owner_id = fields.Many2one('res.partner', string='Assign Owner')  
    
    def action_hfoc_see_packages(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_package_view")
        packages = []
        for line in self.finished_move_line_ids:
            packages.append(line.result_package_id.id)
        action['domain'] = [('id', 'in', packages)]
        action['context'] = {}
        return action

    def button_put_in_pack(self):
        for self in self:
            num_val = 0
            if len(self.product_id.packaging_ids)> 0:
                num_val = self.product_id.packaging_ids[0].qty
                qty_done = 0.0
                if num_val > 0:
                    if self.qty_producing > 0:
                        num_pallets = int(round((self.qty_producing/num_val)+0.5,0))
                        for i in range(0,num_pallets):
                            if i+1 == num_pallets and self.qty_producing%num_val!=0:
                                qty_done = self.qty_producing%num_val
                            else:
                                qty_done = num_val
                            stock_move_live = []
                            
                            numb=self.env['ir.sequence'].next_by_code('stock.quant.package')


                            if i < len(self.finished_move_line_ids):
                                self.finished_move_line_ids[int(i)].qty_done = qty_done
                                self.finished_move_line_ids[int(i)].result_package_id = self.env['stock.quant.package'].create({'name': numb })

                            else:

                                stock_move_live.append(({
                                            'date': self.finished_move_line_ids[0].date,
                                            'reference': self.finished_move_line_ids[0].reference,
                                            'origin': self.finished_move_line_ids[0].origin,
                                            'move_id': self.finished_move_line_ids[0].move_id.id,
                                            'product_id': self.finished_move_line_ids[0].product_id.id,
                                            'product_uom_id': self.finished_move_line_ids[0].product_uom_id.id,                                        
                                            'location_id': self.finished_move_line_ids[0].location_id.id,
                                            'location_dest_id': self.finished_move_line_ids[0].location_dest_id.id,
                                            'qty_done': qty_done,
                                            'lot_id': self.finished_move_line_ids[0].lot_id.id,
                                            'package_id': self.finished_move_line_ids[0].package_id.id,
                                            'result_package_id': self.env['stock.quant.package'].create({'name': numb }).id,
                                            'owner_id': self.finished_move_line_ids[0].owner_id.id,
                                            'company_id': self.finished_move_line_ids[0].company_id.id,
                                            'production_id': self.finished_move_line_ids[0].production_id.id,
                                            'workorder_id': self.finished_move_line_ids[0].workorder_id.id,
                                            'state': self.finished_move_line_ids[0].state
                                            }))

                                self.finished_move_line_ids.create(stock_move_live)
                        self.hfoc_hide_package = True
                        if self.hfoc_owner_id:
                            for up in self.finished_move_line_ids:
                                up.owner_id = self.hfoc_owner_id.id
            else:
                raise UserError(_('The product needs a Packaging.'))
            

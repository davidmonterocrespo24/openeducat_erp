from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import float_is_zero

class AccountMove(models.Model):
    _inherit = 'account.move'


    def get_hf_invoiced_lot_values(self):
        for self in self:
            head = """<table class="o_list_table table table-sm table-hover table-striped o_list_table_ungrouped o_section_and_note_list_view" style="table-layout: fixed;"   >
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th class="text-right">Quantity</th>
                                <th class="text-right">SN/LN</th>
                            </tr>
                        </thead>
                        <tbody>"""
            footer = """</tbody>
                        </table>"""
            body = ''
            for line in self._get_invoiced_lot_values():
                body += "<tr><td>"+line['product_name']+"</td><td class='text-right'>"+line['quantity']+' '+line['uom_name']+"</td><td class='text-right' >"+line['lot_name']+"</td><tr>"
            

            self.hfoc_lots = head+body+footer

    hfoc_lots = fields.Html(string='Lots', compute=get_hf_invoiced_lot_values )



    






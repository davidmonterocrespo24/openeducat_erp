from odoo import models, fields, api, _
from .gtin import GTIN
from datetime import date
from odoo.exceptions import UserError, Warning



    
class ResPartnerProvelot(models.Model):
    _name = 'res.partner.provelot'
    _description = "res partner provelot"
    
    _sql_constraints = [('hfoc_name', 'unique(name)', 'Code already exists.'),]   
        
    name = fields.Char(string='Code' )
    ref_prove = fields.Char(string='Ref Vendor' )
    hfoc_number_lot = fields.Integer(string='Lot number')
    hfoc_partner_id = fields.Many2one('res.partner', string='Provedor')
    hfoc_partner_id_parent = fields.Many2one('res.partner', string='Supplier')    


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hfoc_vendor_lot =  fields.Char(string='Vendor Lot')
    hfoc_label = fields.Char(string='Label')
    hfoc_zip2 = fields.Char(string='Code Zip2')
    hfoc_partner_provelot = fields.One2many('res.partner.provelot', 'hfoc_partner_id_parent', 'Code Prove Lots')
    

class ProductDedailLabel(models.Model):
    _inherit = 'product.template'

    @api.depends('barcode')
    def _onchange_hfoc_gtin(self):
        for self in self:
            if len(str(self.barcode))>9:
                self.hfoc_gtin = str(GTIN(raw=str(self.barcode.zfill(10))))
            else:
                self.hfoc_gtin = ""  


    hfoc_pcs = fields.Char(string='PCS', default='0 PCS')
    hfoc_nationality = fields.Char(string='Nationality', default='Product of Mexico')
    hfoc_business = fields.Char(string='Business', default='Ivan Big Tree, LLC')
    hfoc_street = fields.Char(string='Street', default='McAllen, TX')
    hfoc_gtin = fields.Char(string='GTIN', compute="_onchange_hfoc_gtin", store=True )

     

class StockMoveLotdetail(models.Model):
    _name = 'stock.move.lotdetail'
    _description = "stock move lotdetail"
        
    hfoc_num_lot = fields.Integer(string='Qty packages' )
    hfoc_stock_move = fields.Many2one('stock.move', string='Stock Move')
    hfoc_harvest_date = fields.Date(string='Harvest date')
    hfoc_tag = fields.Char(string='Tag')
    hfoc_owner_id = fields.Many2one('res.partner', string='Assign Owner') 
    hfoc_stock_move2 = fields.Many2one('stock.move', string='Stock Move 2')
    hfoc_partner_provelot = fields.Many2one('res.partner.provelot', string='V. Code')



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    hfoc_partner_provelot = fields.Many2one('res.partner.provelot', string='Vn. Code')
    hfoc_harvest_date = fields.Date(string='Harvest date')
    hfoc_tag = fields.Char(string='Tag')   
    hide_ccss_bottom = fields.Boolean('Hide ccss bottom ?')
    hfoc_lot_id = fields.Many2one('res.partner.provelot', string='Vnd. Code')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for self in self:
            if self.picking_type_code in ('incoming'):
                if self.move_ids_without_package:
                    for product in self.move_ids_without_package:
                        if product.move_line_nosuggest_ids:
                            for info in product.move_line_nosuggest_ids:
                                if info.lot_id:
                                    info.owner_id = info.hfoc_partner_provelot.hfoc_partner_id_parent or self.owner_id
                                    info.lot_id.hfoc_tag = info.hfoc_tag
                                    info.lot_id.hfoc_harvest_date = info.hfoc_harvest_date
                                    info.lot_id.hfoc_owner_id = info.hfoc_partner_provelot.hfoc_partner_id_parent
                                    info.lot_id.hfoc_partner_provelot = info.hfoc_partner_provelot

        return res
    


    def buttom_create_package_id(self):
        for self in self:            
            
            if not self.hfoc_partner_provelot:
                raise UserError(_('Not selected: Vendor Code.'))
            elif not self.hfoc_harvest_date:
                raise UserError(_('Not selected: Harvest date.'))
            for line in self.move_ids_without_package:
                if not line.product_packaging_id:
                    raise UserError(_('Not selected: Packaging in '+str(line.product_id.name)+'.'))
                
            hfoc_number_lot_global = self.hfoc_partner_provelot.hfoc_number_lot+1
            self.hfoc_partner_provelot.hfoc_number_lot = hfoc_number_lot_global
            
            for lp in self.move_ids_without_package:                
                move_detail_total = 0
                pallets = []
                num_pallets = 0
                if lp.hfoc_move_detail:
                    for line in lp.hfoc_move_detail:
                        move_detail_total = move_detail_total + line.hfoc_num_lot
                        hfoc_number_lot = line.hfoc_partner_provelot.hfoc_number_lot+1
                        line.hfoc_partner_provelot.hfoc_number_lot = hfoc_number_lot
                        
                        if line.hfoc_num_lot%lp.product_packaging_id.qty != 0:
                            num_pallets = int(round((line.hfoc_num_lot/lp.product_packaging_id.qty)+0.5,0))
                        else:
                            num_pallets = int(round((line.hfoc_num_lot/lp.product_packaging_id.qty),0))
                        
                        for i in range(0,num_pallets):           
                            numb=self.env['ir.sequence'].next_by_code('stock.quant.package')
                            id_pallet = self.env['stock.quant.package'].create({
                                    'name': numb
                            })

                            if i+1 == num_pallets and line.hfoc_num_lot%lp.product_packaging_id.qty!=0:
                                qty_done = line.hfoc_num_lot%lp.product_packaging_id.qty
                            else:
                                qty_done = lp.product_packaging_id.qty
                            lot_name = line.hfoc_partner_provelot.name+(str(hfoc_number_lot))+str(date.today().year)[-2:]
                            lot_id = self.env['stock.production.lot'].search([('name','=',lot_name),('product_id','=',lp.product_id.id)], limit=1)
                            if lot_id:
                                pass
                            else:
                                lot_id = self.env['stock.production.lot'].create({
                                    'name': lot_name,
                                    'product_id':lp.product_id.id,
                                    'company_id':self.company_id.id
                            })
                            pallets.append(({
                                            'picking_id': lp.picking_id.id,
                                            'move_id': lp.id,
                                            'product_id': lp.product_id.id,
                                            'product_uom_id': lp.product_id.uom_id.id,
                                            'location_id':lp.location_id.id,
                                            'location_dest_id':lp.location_dest_id.id,
                                            'company_id':self.company_id.id,
                                            'result_package_id': id_pallet.id,
                                            'hfoc_harvest_date': line.hfoc_harvest_date,
                                            'lot_name': lot_name,                                            
                                            'lot_id': lot_id.id,
                                            'hfoc_partner_provelot': line.hfoc_partner_provelot.id,
                                            'hfoc_tag': line.hfoc_tag,
                                            'qty_done':qty_done}))

                
                main_lot_total = lp.product_uom_qty - move_detail_total
                
                if main_lot_total > 0:
                    if main_lot_total%lp.product_packaging_id.qty != 0:
                        num_pallets = int(round((main_lot_total/lp.product_packaging_id.qty)+0.5,0))
                    else:
                        num_pallets = int(round((main_lot_total/lp.product_packaging_id.qty),0))
                    for i in range(0,num_pallets):           
                        numb=self.env['ir.sequence'].next_by_code('stock.quant.package')
                        id_pallet = self.env['stock.quant.package'].create({
                                'name': numb
                        })
                        qty_done = 0.0
                        if i+1 == num_pallets and main_lot_total%lp.product_packaging_id.qty!=0:
                            qty_done = main_lot_total%lp.product_packaging_id.qty
                        else:
                            qty_done = lp.product_packaging_id.qty


                        lot_name = self.hfoc_partner_provelot.name+(str(hfoc_number_lot_global))+str(date.today().year)[-2:]
                        lot_id = self.env['stock.production.lot'].search([('name','=',lot_name),('product_id','=',lp.product_id.id)], limit=1)
                        if lot_id:
                            pass
                        else:
                            lot_id = self.env['stock.production.lot'].create({
                                'name': lot_name,
                                'product_id':lp.product_id.id,
                                'company_id':self.company_id.id
                        })
                        
                        pallets.append(({
                                        'picking_id': lp.picking_id.id,
                                        'move_id': lp.id,
                                        'product_id': lp.product_id.id,
                                        'product_uom_id': lp.product_id.uom_id.id,
                                        'location_id':lp.location_id.id,
                                        'location_dest_id':lp.location_dest_id.id,
                                        'company_id':self.company_id.id,
                                        'result_package_id': id_pallet.id,
                                        'hfoc_harvest_date': self.hfoc_harvest_date,
                                        'lot_name': lot_name,
                                        'lot_id': lot_id.id,
                                        'hfoc_partner_provelot': self.hfoc_partner_provelot.id,
                                        'hfoc_tag': self.hfoc_tag,
                                        'qty_done':qty_done}))
                lp.move_line_nosuggest_ids.unlink()
                lp.move_line_nosuggest_ids = lp.move_line_nosuggest_ids.create(pallets)            
    

    def buttom_hfoc_number_ccss(self):
        for self in self:            
            for line in self.env['ir.sequence'].search([('code','=','sequence.ccss')]):
                if len(line.prefix) < 11:
                    raise UserError(_('Prefix SSCC length error.'))    
            if self.move_ids_without_package:                
                for line in self.move_ids_without_package:
                    sequence_ccss =self.env['ir.sequence'].next_by_code('sequence.ccss')
                    line.hfoc_number_sequence = sequence_ccss
                    
                    if len(line.hfoc_number_sequence)>10:
                        line.hfoc_code_ccss = (line.hfoc_number_sequence.zfill(17)+ str(GTIN(raw=line.hfoc_number_sequence.zfill(17)))[-1]).zfill(18)
                    else:
                        line.hfoc_code_ccss = ''
                self.hide_ccss_bottom = True

class StockMove(models.Model):
    _inherit = 'stock.move'    

    _sql_constraints = [
    ('hfoc_number_sequence_uniq', 'unique(hfoc_number_sequence)', 'Barcode SSCC already exists.'),    
    ]
    
    hfoc_move_detail = fields.One2many('stock.move.lotdetail', 'hfoc_stock_move', 'Details Lots')
    hfoc_number_sequence = fields.Char(string='GS1 Profix + Number')
    hfoc_code_ccss = fields.Char(string='SSCC' ,  store=True )


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    hfoc_harvest_date = fields.Date(string='Harvest date')
    hfoc_partner_provelot = fields.Many2one('res.partner.provelot', string='Vndr Code')
    hfoc_tag = fields.Char(string='Tag')


    @api.onchange('lot_id')
    def _onchange_hfoc_lot_id(self):
        for self in self:
            if self.lot_id:
                self.owner_id = self.lot_id.hfoc_owner_id



class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    @api.depends('hfoc_harvest_date','hfoc_owner_id','product_id')
    def _onchange_hfoc_harvest_date(self):
        for self in self:            
            if len(str(self.product_id.barcode))>9 and self.hfoc_partner_provelot.name and self.hfoc_harvest_date:
                vendor_code = self.hfoc_partner_provelot.name
                harvest_date = str(self.hfoc_harvest_date.year)+str(self.hfoc_harvest_date.month).zfill(2)+str(self.hfoc_harvest_date.day).zfill(2)
                self.hfoc_gtin_full = ('01'+str(self.hfoc_gtin_product)+'13'+harvest_date+'10'+vendor_code).upper()
                self.hfoc_gtin_full_str = ('(01)'+str(self.hfoc_gtin_product)+'(13)'+harvest_date+'(10)'+vendor_code).upper()
            else:
                self.hfoc_gtin_full = ''
                self.hfoc_gtin_full_str  = ''
    
    @api.depends('hfoc_harvest_date','hfoc_owner_id','product_id') 
    def _onchange_hfoc_vpc(self):
        for self in self:
            if self.hfoc_gtin_full != '':
                table = [
                    0, 49345, 49537, 320, 49921, 960, 640, 49729, 50689, 1728, 1920, 51009, 1280,
                    50625, 50305, 1088, 52225, 3264, 3456, 52545, 3840, 53185, 52865, 3648, 2560,
                    51905, 52097, 2880, 51457, 2496, 2176, 51265, 55297, 6336, 6528, 55617, 6912,
                    56257, 55937, 6720, 7680, 57025, 57217, 8000, 56577, 7616, 7296, 56385, 5120,
                    54465, 54657, 5440, 55041, 6080, 5760, 54849, 53761, 4800, 4992, 54081, 4352,
                    53697, 53377, 4160, 61441, 12480, 12672, 61761, 13056, 62401, 62081, 12864,
                    13824, 63169, 63361, 14144, 62721, 13760, 13440, 62529, 15360, 64705, 64897,
                    15680, 65281, 16320, 16000, 65089, 64001, 15040, 15232, 64321, 14592, 63937,
                    63617, 14400, 10240, 59585, 59777, 10560, 60161, 11200, 10880, 59969, 60929,
                    11968, 12160, 61249, 11520, 60865, 60545, 11328, 58369, 9408, 9600, 58689,
                    9984, 59329, 59009, 9792, 8704, 58049, 58241, 9024, 57601, 8640, 8320, 57409,
                    40961, 24768, 24960, 41281, 25344, 41921, 41601, 25152, 26112, 42689, 42881,
                    26432, 42241, 26048, 25728, 42049, 27648, 44225, 44417, 27968, 44801, 28608,
                    28288, 44609, 43521, 27328, 27520, 43841, 26880, 43457, 43137, 26688, 30720,
                    47297, 47489, 31040, 47873, 31680, 31360, 47681, 48641, 32448, 32640, 48961,
                    32000, 48577, 48257, 31808, 46081, 29888, 30080, 46401, 30464, 47041, 46721,
                    30272, 29184, 45761, 45953, 29504, 45313, 29120, 28800, 45121, 20480, 37057,
                    37249, 20800, 37633, 21440, 21120, 37441, 38401, 22208, 22400, 38721, 21760,
                    38337, 38017, 21568, 39937, 23744, 23936, 40257, 24320, 40897, 40577, 24128,
                    23040, 39617, 39809, 23360, 39169, 22976, 22656, 38977, 34817, 18624, 18816,
                    35137, 19200, 35777, 35457, 19008, 19968, 36545, 36737, 20288, 36097, 19904,
                    19584, 35905, 17408, 33985, 34177, 17728, 34561, 18368, 18048, 34369, 33281,
                    17088, 17280, 33601, 16640, 33217, 32897, 16448]

                crc=0
                data= str(self.hfoc_gtin_full)
                
                data=bytes(data,encoding="ascii")
                for byte in data:
                    index=((crc^byte)%256)
                    crc = (crc>>8)^table[index]
                self.hfoc_vpc = str(int(crc%10000)).zfill(4)[-4:] 
            else:
                self.hfoc_vpc = ""
    
    
    @api.depends('product_id')
    def _onchange_hfoc_gtin(self):
        for self in self:
            if len(str(self.product_id.barcode))>9:
                self.hfoc_gtin_product = str(GTIN(raw=str(self.product_id.barcode.zfill(10))))
            else:
                self.hfoc_gtin_product = ""  
    
    hfoc_gtin_product = fields.Char(string='GTIN Product', compute="_onchange_hfoc_gtin", store=True )

    hfoc_gtin_full = fields.Char(string='GTIN' , compute="_onchange_hfoc_harvest_date", store=True )    
    hfoc_gtin_full_str = fields.Char(string='GTIN STR' , compute="_onchange_hfoc_harvest_date", store=True )
        
    hfoc_vpc = fields.Char(string='Voice Pick Code' , compute="_onchange_hfoc_vpc", store=True)   


    hfoc_harvest_date = fields.Date(string='Harvest date')
    hfoc_tag = fields.Char(string='Tag')
    hfoc_owner_id = fields.Many2one('res.partner', string='Assign Owner')
    hfoc_lot_ref = fields.Many2one('stock.production.lot', string='Lot ref', domain=[('quant_ids','!=', False)] )    
    hfoc_partner_provelot = fields.Many2one('res.partner.provelot', string='Vdr. Code')


    @api.onchange('hfoc_lot_ref')
    def _onchange_hfoc_lot_ref(self):
        for self in self:
            self.hfoc_harvest_date = self.hfoc_lot_ref.hfoc_harvest_date
            self.hfoc_tag = self.hfoc_lot_ref.hfoc_tag
            self.hfoc_owner_id = self.hfoc_lot_ref.hfoc_owner_id
            self.hfoc_partner_provelot = self.hfoc_lot_ref.hfoc_partner_provelot
            self.ref = self.hfoc_lot_ref.ref

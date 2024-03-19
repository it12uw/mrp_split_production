from odoo import _, models, fields
from odoo.exceptions import UserError


class MrpWorkOrderInherit(models.Model):
    _inherit = "mrp.workorder"
    _description ='Inherit MRP Work Order'

    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    product_qty = fields.Float(related='production_id.product_qty')
    
    
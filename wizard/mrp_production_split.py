from odoo import api, fields, models
from odoo.tools import float_round, float_compare

class MrpProductionSplit(models.TransientModel):
    _name = 'mrp.production.split'
    _description = "Wizard to Split a Production"

    production_split_multi_id = fields.Many2one('mrp.production.split.multi', 'Split Productions')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    product_id = fields.Many2one(related='production_id.product_id')
    product_qty = fields.Float(related='production_id.product_qty')
    product_uom_id = fields.Many2one(related='production_id.product_uom_id')
    production_capacity = fields.Float(related='production_id.production_capacity')
    quantity_to_split = fields.Float(string='Quantity to Split')

    production_detailed_vals_ids = fields.One2many('mrp.production.split.line', 'mrp_production_split_id','Split Details', compute="_compute_details", store=True, readonly=False)

    # Action Tombol Split Productions
    def action_split_workorder(self):
        workorder_baru = self.production_id.copy(default={'name': self.production_id.name + ' (Split)','qty_producing': self.quantity_to_split})
        self.production_id.qty_producing -= self.quantity_to_split
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'res_id': workorder_baru.id,
            'target': 'current',
        }

class MrpProductionSplitLine(models.TransientModel):
    _name='mrp.production.split.line'
    _description='Mrp Production Split Line'    
    
    mrp_production_split_id = fields.Many2one(
        'mrp.production.split', 'Split Production', required=True, ondelete="cascade")
    quantity = fields.Float('Quantity To Produce', digits='Product Unit of Measure', required=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        domain=lambda self: [('groups_id', 'in', self.env.ref('mrp.group_mrp_user').id)])
    date = fields.Datetime('Schedule Date')

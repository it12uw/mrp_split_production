from odoo import api, fields, models
from odoo.tools import float_round, float_compare


class MrpProductionSplitMulti(models.TransientModel):
    _name = 'mrp.production.split.multi'
    _description = "Wizard to Split Multiple Productions"
 
    production_ids = fields.One2many('mrp.production.split', 'production_split_multi_id', 'Productions To Split')


class MrpProductionSplit(models.TransientModel):
    _name = 'mrp.production.split'
    _description = "Wizard to Split a Production"

    production_split_multi_id = fields.Many2one('mrp.production.split.multi', 'Split Productions')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    product_id = fields.Many2one(related='production_id.product_id')
    product_qty = fields.Float(related='production_id.product_qty')
    product_uom_id = fields.Many2one(related='production_id.product_uom_id')
    production_capacity = fields.Float(related='production_id.production_capacity')
    quantity_to_split = fields.Integer(
        "Split Into ?", default=0, compute="_compute_quantity_to_split",
        store=True, readonly=False)
    production_detailed_vals_ids = fields.One2many(
        'mrp.production.split.line', 'mrp_production_split_id',
        'Split Details', compute="_compute_details", store=True, readonly=False)
    valid_details = fields.Boolean("Valid", compute="_compute_valid_details")

    @api.depends('production_detailed_vals_ids')
    def _compute_quantity_to_split(self):
        for wizard in self:
            wizard.quantity_to_split = len(wizard.production_detailed_vals_ids)

    @api.depends('quantity_to_split')
    def _compute_details(self):
        for wizard in self:
            commands = []
            if wizard.quantity_to_split < 1 or not wizard.production_id:
                wizard.production_detailed_vals_ids = commands
                continue
            quantity = float_round(wizard.product_qty / wizard.quantity_to_split, precision_rounding=wizard.product_uom_id.rounding)
            remaining_quantity = wizard.product_qty
            for _ in range(wizard.quantity_to_split - 1):
                commands.append((0, 0, {
                    'quantity': quantity,
                    'user_id': wizard.production_id.user_id.id,
                    'date': wizard.production_id.date_start,
                }))
                remaining_quantity = float_round(remaining_quantity - quantity, precision_rounding=wizard.product_uom_id.rounding)
            commands.append((0, 0, {
                'quantity': remaining_quantity,
                'user_id': wizard.production_id.user_id.id,
                'date': wizard.production_id.date_start,
            }))
            wizard.production_detailed_vals_ids = commands

    @api.depends('production_detailed_vals_ids')
    def _compute_valid_details(self):
        self.valid_details = False
        for wizard in self:
            if wizard.production_detailed_vals_ids:
                wizard.valid_details = float_compare(wizard.product_qty, sum(wizard.production_detailed_vals_ids.mapped('quantity')), precision_rounding=wizard.product_uom_id.rounding) == 0

    def action_split(self):
        # Mengambil jumlah yang ingin di-split untuk setiap Work Order
        quantities = [detail.quantity for detail in self.production_detailed_vals_ids]

        # Memanggil metode _split_productions dengan jumlah yang ingin di-split
        productions = self.production_id._split_productions(quantities)

        for production, detail in zip(productions, self.production_detailed_vals_ids):
            production.user_id = detail.user_id
            production.date_start = detail.date

        if self.production_split_multi_id:
            saved_production_split_multi_id = self.production_split_multi_id.id
            self.production_split_multi_id.production_ids = [(5, 0, 0)]
            action = self.env['ir.actions.actions']._for_xml_id('split_production.action_mrp_production_split_multi')
            action['res_id'] = saved_production_split_multi_id
            return action

    def action_prepare_split(self):
        action = self.env['ir.actions.actions']._for_xml_id('split_production.action_mrp_production_split')
        action['res_id'] = self.id
        return action

    def action_return_to_list(self):
        self.production_detailed_vals_ids = [(5, 0, 0)]
        self.quantity_to_split = 0
        action = self.env['ir.actions.actions']._for_xml_id('split_production.action_mrp_production_split_multi')
        action['res_id'] = self.production_split_multi_id.id
        return action
    
class MrpProductionSplitLine(models.TransientModel):
    _name = 'mrp.production.split.line'
    _description = "Split Production Detail"

    mrp_production_split_id = fields.Many2one('mrp.production.split', 'Split Production', required=True, ondelete="cascade")
    quantity = fields.Float('Quantity To Produce', digits='Product Unit of Measure', required=True)
    user_id = fields.Many2one('res.users', 'Responsible',domain=lambda self: [('groups_id', 'in', self.env.ref('mrp.group_mrp_user').id)])
    date = fields.Datetime('Schedule Date')
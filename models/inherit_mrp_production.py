from odoo import _, models, fields
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_capacity = fields.Float(compute='_compute_production_capacity', help="Quantity that can be produced with the current stock of components")
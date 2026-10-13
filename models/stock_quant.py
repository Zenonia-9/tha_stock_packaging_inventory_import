from odoo import _, models
from odoo.exceptions import UserError

from .common import require_manager


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def tha_action_download_packaging_counts(self):
        require_manager(self.env)
        if not self or any(not quant.id for quant in self):
            raise UserError(_('Save and select existing Physical Inventory lines before downloading a count sheet.'))
        return self.env['tha.inventory.count.template']._export_quants(self).download_action()

    def tha_action_upload_packaging_counts(self):
        require_manager(self.env)
        return {
            'type': 'ir.actions.act_window', 'name': _('Upload Packaging Counts'),
            'res_model': 'tha.inventory.count.upload', 'view_mode': 'form', 'target': 'new',
            'context': {'default_company_id': self.env.company.id},
        }

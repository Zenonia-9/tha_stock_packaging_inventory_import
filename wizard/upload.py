import base64
import binascii

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..models.common import MAX_FILE_BYTES, require_manager


class InventoryCountUpload(models.TransientModel):
    _name = 'tha.inventory.count.upload'
    _description = 'Upload a packaging physical count sheet'

    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    file_data = fields.Binary(string='Counting Workbook', required=True)
    filename = fields.Char()

    def action_preview(self):
        self.ensure_one()
        require_manager(self.env)
        if self.company_id != self.env.company:
            raise UserError(_('The selected company changed. Reopen the upload action.'))
        if not self.filename or not self.filename.lower().endswith('.xlsx'):
            raise UserError(_('Select the .xlsx packaging counting workbook.'))
        if not self.file_data or len(self.file_data) > MAX_FILE_BYTES * 4 // 3 + 4:
            raise UserError(_('Upload a file no larger than 10 MB.'))
        try:
            data = base64.b64decode(self.file_data, validate=True)
        except (ValueError, binascii.Error) as error:
            raise UserError(_('The uploaded file could not be read.')) from error
        return self.env['tha.inventory.count.import']._preview_upload(data, self.filename).open_action()

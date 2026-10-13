import base64
import math

from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError

from .common import internal, require_internal, require_manager


class InventoryCountImport(models.Model):
    _name = 'tha.inventory.count.import'
    _description = 'Packaging inventory count import batch'
    _order = 'id desc'

    name = fields.Char(required=True, readonly=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True)
    template_id = fields.Many2one('tha.inventory.count.template', required=True, readonly=True, ondelete='restrict')
    state = fields.Selection([('preview', 'Preview'), ('done', 'Counts Updated')], default='preview', required=True, readonly=True)
    file_data = fields.Binary(attachment=True, readonly=True)
    filename = fields.Char(readonly=True)
    line_ids = fields.One2many('tha.inventory.count.import.line', 'batch_id', readonly=True)
    imported_by = fields.Many2one('res.users', readonly=True)
    imported_at = fields.Datetime(readonly=True)
    line_count = fields.Integer(compute='_compute_line_count')

    @api.depends('line_ids')
    def _compute_line_count(self):
        for batch in self:
            batch.line_count = len(batch.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        require_internal(self.env)
        return super().create(vals_list)

    def write(self, vals):
        require_internal(self.env)
        return super().write(vals)

    def unlink(self):
        require_internal(self.env)
        return super().unlink()

    @api.model
    def _preview_upload(self, data, filename):
        require_manager(self.env)
        template, lines = self.env['tha.inventory.count.template']._read_upload(data)
        return internal(self).create({
            'name': _('Packaging count import — %s', fields.Datetime.now()),
            'company_id': self.env.company.id, 'template_id': template.id,
            'filename': filename or 'Packaging Counts.xlsx', 'file_data': base64.b64encode(data),
            'line_ids': [Command.create(line) for line in lines],
        })

    def action_confirm(self):
        self.ensure_one()
        require_manager(self.env)
        self.check_access('write')
        self.lock_for_update()
        self.invalidate_recordset(['state'])
        if self.state != 'preview':
            raise UserError(_('This batch has already updated its counts.'))
        if self.company_id != self.env.company:
            raise UserError(_('Switch to the company used by this batch before confirming.'))
        quants = self.line_ids.mapped('quant_id').exists()
        if len(quants) != len(self.line_ids):
            raise UserError(_('An inventory line was deleted or is duplicated. Upload a fresh template.'))
        quants.check_access('write')
        # ORM locks prevent two imports or an ordinary count edit from racing.
        quants.lock_for_update(allow_referencing=True)
        templates = quants.product_id.product_tmpl_id
        templates.lock_for_update(allow_referencing=True)
        quants.product_id.invalidate_recordset()
        templates.invalidate_recordset()
        units = quants.product_id.uom_id | quants.product_id.uom_ids
        ancestors = units
        while units.relative_uom_id - ancestors:
            units = units.relative_uom_id - ancestors
            ancestors |= units
        ancestors.lock_for_update(allow_referencing=True)
        quants.invalidate_recordset()
        templates.invalidate_recordset()
        ancestors.invalidate_recordset()
        updates = []
        snapshot_rows = self.template_id.snapshot['rows']
        for line in self.line_ids:
            row = snapshot_rows.get(str(line.stock_line_id))
            if not row:
                raise UserError(_('The template no longer contains this inventory line.'))
            quant, total = self.template_id._check_live(row, line.counts)
            if (quant.inventory_quantity_set != line.old_count_set
                    or not math.isclose(quant.inventory_quantity, line.old_count, rel_tol=0, abs_tol=1e-12)
                    or not math.isclose(quant.quantity, line.on_hand, rel_tol=0, abs_tol=1e-12)):
                raise UserError(_('An inventory count or on-hand quantity changed after the preview. Upload again to review the current values.'))
            if not math.isclose(total, line.new_count, rel_tol=0, abs_tol=1e-12):
                raise UserError(_('The converted total changed after preview. Download a fresh template.'))
            updates.append((quant, total))
        # Validate every row before any write. The request is one database transaction.
        for quant, total in updates:
            quant.with_context(inventory_mode=True).write({
                'inventory_quantity': total, 'inventory_quantity_set': True,
            })
        internal(self).write({'state': 'done', 'imported_by': self.env.user.id, 'imported_at': fields.Datetime.now()})
        return self.open_action()

    def open_action(self):
        self.ensure_one()
        self.check_access('read')
        return {'type': 'ir.actions.act_window', 'name': _('Packaging Count Import'),
                'res_model': self._name, 'res_id': self.id, 'view_mode': 'form', 'target': 'current'}

    def action_view_inventory(self):
        self.ensure_one()
        require_manager(self.env)
        self.check_access('read')
        action = self.env['stock.quant'].action_view_inventory()
        action['domain'] = [('id', 'in', self.line_ids.mapped('stock_line_id'))]
        return action


class InventoryCountImportLine(models.Model):
    _name = 'tha.inventory.count.import.line'
    _description = 'Packaging count conversion and previous inventory count'
    _order = 'source_row, id'

    batch_id = fields.Many2one('tha.inventory.count.import', required=True, ondelete='cascade', readonly=True)
    company_id = fields.Many2one(related='batch_id.company_id', store=True)
    quant_id = fields.Many2one('stock.quant', ondelete='set null', readonly=True)
    stock_line_id = fields.Integer(readonly=True)
    source_row = fields.Integer(readonly=True)
    product_name = fields.Char(readonly=True)
    location_name = fields.Char(readonly=True)
    lot_name = fields.Char(readonly=True)
    package_name = fields.Char(readonly=True)
    owner_name = fields.Char(readonly=True)
    unit_name = fields.Char(readonly=True)
    counts = fields.Json(readonly=True)
    count_details = fields.Text(string='Entered Counts and Conversions', readonly=True)
    old_count = fields.Float(string='Previous Count', digits='Product Unit', readonly=True)
    old_count_set = fields.Boolean(string='Previously Counted', readonly=True)
    on_hand = fields.Float(digits='Product Unit', readonly=True)
    new_count = fields.Float(string='New Count', digits='Product Unit', readonly=True)
    difference = fields.Float(string='Difference from On Hand', digits='Product Unit', compute='_compute_difference')

    @api.depends('new_count', 'on_hand')
    def _compute_difference(self):
        for line in self:
            line.difference = line.new_count - line.on_hand

    @api.model_create_multi
    def create(self, vals_list):
        require_internal(self.env)
        return super().create(vals_list)

    def write(self, vals):
        require_internal(self.env)
        return super().write(vals)

    def unlink(self):
        require_internal(self.env)
        return super().unlink()

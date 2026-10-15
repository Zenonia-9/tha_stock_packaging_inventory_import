import math

from odoo import _
from odoo.exceptions import AccessError, UserError


# RPC callers cannot manufacture this object by supplying a context flag.
_INTERNAL = object()
MAX_ROWS = 20000
MAX_FILE_BYTES = 10 * 1024 * 1024


def internal(records):
    return records.with_context(_tha_packaging_operation=_INTERNAL)


def require_internal(env):
    if env.context.get('_tha_packaging_operation') is not _INTERNAL:
        raise AccessError(_('Use the packaging count actions to change these records.'))


def require_manager(env):
    if not env.user.has_group('stock.group_stock_manager'):
        raise AccessError(_('Only Inventory administrators can import packaging counts.'))


def root_unit(unit):
    while unit.relative_uom_id:
        unit = unit.relative_uom_id
    return unit


def conversion(unit, inventory_unit, product):
    if not unit.active or root_unit(unit) != root_unit(inventory_unit):
        raise UserError(_(
            'The packaging must be active and use the same reference unit as the inventory unit.\n'
            'Product: %(product)s\nPackaging: %(packaging)s\nInventory unit: %(inventory_unit)s',
            product=product.display_name, packaging=unit.display_name,
            inventory_unit=inventory_unit.display_name,
        ))
    factor = unit._compute_quantity(1.0, inventory_unit, round=False)
    if not math.isfinite(factor) or factor <= 0:
        raise UserError(_('The packaging conversion must be a positive finite quantity.'))
    return factor


def identity(quant):
    return {
        'quant_id': quant.id,
        'product_id': quant.product_id.id,
        'location_id': quant.location_id.id,
        'lot_id': quant.lot_id.id or 0,
        'package_id': quant.package_id.id or 0,
        'owner_id': quant.owner_id.id or 0,
        'inventory_uom_id': quant.product_id.uom_id.id,
        'company_id': quant.company_id.id,
    }


def check_quant(quant, expected=None):
    require_manager(quant.env)
    if not quant.exists():
        raise UserError(_('An inventory line no longer exists. Download a fresh template.'))
    quant.check_access('read')
    if quant.company_id != quant.env.company:
        raise UserError(_('All inventory lines must belong to the currently selected company.'))
    if quant.location_id.usage not in ('internal', 'transit'):
        raise UserError(_('Only internal and transit inventory lines can be counted.'))
    if not quant.product_id.active or not quant.product_id.is_storable:
        raise UserError(_('The inventory product must be active and track inventory.'))
    if expected and identity(quant) != expected:
        raise UserError(_('An inventory line changed product, location, tracking dimensions or inventory unit. Download a fresh template.'))

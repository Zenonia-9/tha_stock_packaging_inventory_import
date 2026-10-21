{
    'name': 'Physical Inventory Counts by Packaging',
    'version': '19.0.1.0.5',
    'category': 'Inventory/Inventory',
    'summary': 'Update existing physical inventory lines from one-row packaging counts',
    'depends': ['stock'],
    'external_dependencies': {'python': ['openpyxl', 'xlsxwriter']},
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/import_batch_views.xml',
        'wizard/upload_views.xml',
        'views/stock_quant_views.xml',
    ],
    'author': 'Thein Htoo Aung',
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}

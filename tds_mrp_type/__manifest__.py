{
    'name': 'TDS Manufacturing Type',
    'version': '18.0',
    'description': 'add a manufacturing type to mrp',
    'author': 'TDS Dev Team',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/manufacturing_type.xml',
        'views/mrp_order.xml',
        'views/mrp_bom.xml'

    ],
    
}
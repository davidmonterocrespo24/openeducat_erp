{
    'name': 'HFoc Stock Packaging',
    'version': '0.1',
    'category': 'stock',
    'summary': 'HFoc Stock Packaging',
    'license':'LGPL-3',
    'description': """
    HFoc Stock Packaging
    """,
    'author' : 'HFOC11',
    'depends': ['base','stock','purchase_stock'],
    'data': [       
        'security/ir.model.access.csv',       
        'reports/stock_picking_product_pdf.xml',
        'reports/stock_quant_package_pdf.xml',
        'reports/stock_street_package_pdf.xml',
        'reports/report.xml',
        'data/data.xml',
        'views/product.xml',
    ],    
    "installable": True,
    "application": False,

}

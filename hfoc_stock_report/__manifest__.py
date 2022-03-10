{
    'name': 'HFoc Stock Report',
    'version': '0.1',
    'category': 'project',
    'summary': 'HFoc Stock Report',
    'license':'LGPL-3',
    'description': """
    HFoc Stock Report
    """,
    'author' : 'HFOC11',
    'depends': ['base','stock','sale'],
    'data': [
        'security/ir.model.access.csv', 
        'views/hfoc_stock_report.xml',
    ],    
    "installable": True,
    "application": False,

}

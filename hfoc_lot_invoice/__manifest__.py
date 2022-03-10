{
    'name': 'HFoc Lot in invoice',
    'version': '0.1',
    'category': 'account',
    'summary': 'HFoc Lot in invoice',
    'license':'LGPL-3',
    'description': """
    HFoc Lot in invoice
    """,
    'author' : 'HFOC11',
    'depends': ['base','account','stock'],
    'data': [
        'views/account_move.xml',
    ],    
    "installable": True,
    "application": False,

}

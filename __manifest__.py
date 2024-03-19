{
    "name": "MRP Production Split",
    "summary": "Split Manufacturing Orders into smaller",
    "version": "14.0.1.0.0",
    "author": "Steven Morison (stevenmorizon123@gmail.com)",
    "website": "https://github.com/it12uw/mrp_split_production.git",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp","product","stock","resource"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_inherit_view.xml",
        "views/mrp_workorder_inherit_view.xml",
        "wizard/mrp_production_split.xml",
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

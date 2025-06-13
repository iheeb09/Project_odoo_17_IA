{
    'name': 'Department Recruitment Analysis',
    'version': '1.0.0',
    'summary': 'Predict and analyze recruitment needs by department',
    'category': 'Human Resources',
    'depends': ['hr', 'hr_recruitment'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/department_analysis_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

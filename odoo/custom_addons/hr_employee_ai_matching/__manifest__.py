{
    "name": "Employee AI Matching",
    "version": "1.0.0",
    "category": "Human Resources",
    "summary": "Matching IA entre CV et description de poste",
    "author": "GHM",
    "license": "LGPL-3",
    "depends": ["hr"],
    "data": [

        "security/ir.model.access.csv",

        "views/hr_matching_job_action.xml",

        "views/hr_matching_job_views.xml",
        "views/menu.xml"
    ],
    "installable": True,
    "application": False
}

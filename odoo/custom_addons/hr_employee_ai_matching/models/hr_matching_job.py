from odoo import models, fields, api
from odoo.exceptions import UserError
import fitz  # PyMuPDF
import base64
import requests
import logging

_logger = logging.getLogger(__name__)


class HRMatchingJob(models.Model):
    _name = "hr.matching.job"
    _description = "Job Opening + CVs to Compare"

    name = fields.Char("Job Title", required=True)
    description = fields.Text("Job Description", required=True)

    cv_ids = fields.One2many("hr.matching.cv", "job_id", string="CVs to Compare")
    result_ids = fields.One2many("hr.matching.result", "job_id", string="AI Results")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = "Untitled Job"
        return super().create(vals_list)

    def action_compute_matching(self):
        if not self.description:
            raise UserError("Please provide the job description")

        if not self.cv_ids:
            raise UserError("Please add at least one CV to compare")

        extracted_cvs = []
        for cv in self.cv_ids:
            if not cv.cv_pdf:
                continue
            try:
                pdf_bytes = base64.b64decode(cv.cv_pdf)
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = "\n".join(page.get_text() for page in doc)
                extracted_cvs.append({
                    "name": cv.name or "CV_sans_nom.pdf",
                    "text": text.strip()
                })
            except Exception as e:
                raise UserError(f"Error reading PDF  {cv.name} : {e}")

        try:
            response = requests.post(
                "http://fastapicv:8045/match/multiple",
                json={
                    "job_description": self.description.strip(),
                    "cvs": extracted_cvs
                },
                timeout=150
            )
            response.raise_for_status()
            results = response.json()

            # Nettoyer les anciens résultats
            self.result_ids.unlink()

            for res in results:
                self.env["hr.matching.result"].create({
                    "job_id": self.id,
                    "cv_name": res["cv_name"],
                    "score": res["score"] * 100
                })

            _logger.info(" AI results saved for job %s", self.name)

        except requests.RequestException as e:
            _logger.error("❌ Erreur API : %s", e)
            raise UserError("Erreur de connexion à l'API FastAPI.")

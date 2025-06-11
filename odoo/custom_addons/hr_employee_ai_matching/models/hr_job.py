from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import fitz
import requests
import logging

_logger = logging.getLogger(__name__)

class HrJob(models.Model):
    _inherit = 'hr.job'

    cv_upload_ids = fields.One2many('hr.matching.cv', 'job_id', string="CV Uploads")
    matching_result_ids = fields.One2many('hr.matching.result', 'job_id', string="Matching Results")

    def action_compute_matching(self):
        self.ensure_one()

        if not self.description:
            raise UserError("Please provide the Job Summary (description).")

        if not self.cv_upload_ids:
            raise UserError("Please upload at least one CV.")

        extracted_cvs = []
        for cv in self.cv_upload_ids:
            if not cv.cv_pdf:
                continue
            try:
                pdf_bytes = base64.b64decode(cv.cv_pdf)
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    text = "\n".join(page.get_text() for page in doc)
                extracted_cvs.append({
                    "name": cv.name or "Unnamed CV",
                    "text": text.strip()
                })
            except Exception as e:
                _logger.exception("Error reading PDF: %s", cv.name)
                raise UserError(f"Error reading PDF {cv.name}: {e}")

        if not extracted_cvs:
            raise UserError("No valid CVs with PDF content were found.")

        try:
            api_url = "http://fastapicv:8045/match/multiple"
            payload = {
                "job_description": self.description.strip(),
                "cvs": extracted_cvs
            }
            response = requests.post(api_url, json=payload, timeout=150)
            response.raise_for_status()
            results = response.json()

            self.matching_result_ids.unlink()

            for res in results:
                self.env["hr.matching.result"].create({
                    "job_id": self.id,
                    "cv_name": res.get("cv_name"),
                    "score": res.get("score", 0.0) * 100
                })

            _logger.info("AI results successfully saved for job: %s", self.name)

        except requests.RequestException as e:
            _logger.error("❌ FastAPI connection error: %s", str(e))
            raise UserError("Failed to connect to the FastAPI service.")

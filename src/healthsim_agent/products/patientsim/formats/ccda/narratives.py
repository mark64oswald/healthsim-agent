"""C-CDA narrative builders for human-readable content."""

from __future__ import annotations

import html
from typing import Any


class NarrativeBuilder:
    """Builds HTML narrative content for C-CDA sections."""

    def build_problems_narrative(self, diagnoses: list[Any]) -> str:
        """Build problems section narrative."""
        if not diagnoses:
            return "<text>No known problems</text>"

        rows = []
        for diag in diagnoses:
            status = "Active" if getattr(diag, "is_active", True) else "Resolved"
            onset = ""
            if hasattr(diag, "diagnosed_date") and diag.diagnosed_date:
                onset = diag.diagnosed_date.strftime("%Y-%m-%d")
            rows.append(
                f"<tr>"
                f"<td>{self._escape(diag.description)}</td>"
                f"<td>{diag.code}</td>"
                f"<td>{status}</td>"
                f"<td>{onset}</td>"
                f"</tr>"
            )

        return f"""<text>
  <table border="1" width="100%">
    <thead>
      <tr><th>Problem</th><th>Code</th><th>Status</th><th>Onset</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</text>"""

    def build_medications_narrative(self, medications: list[Any]) -> str:
        """Build medications section narrative."""
        if not medications:
            return "<text>No known medications</text>"

        rows = []
        for med in medications:
            dose = f"{getattr(med, 'dose', '')} {getattr(med, 'unit', '')}".strip()
            freq = getattr(med, "frequency", "")
            status = getattr(med, "status", "active")
            rows.append(
                f"<tr>"
                f"<td>{self._escape(med.drug_name)}</td>"
                f"<td>{dose}</td>"
                f"<td>{freq}</td>"
                f"<td>{status}</td>"
                f"</tr>"
            )

        return f"""<text>
  <table border="1" width="100%">
    <thead>
      <tr><th>Medication</th><th>Dose</th><th>Frequency</th><th>Status</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</text>"""

    def build_allergies_narrative(self, allergies: list[Any]) -> str:
        """Build allergies section narrative."""
        if not allergies:
            return "<text>No known allergies</text>"

        rows = []
        for allergy in allergies:
            reaction = getattr(allergy, "reaction", "")
            severity = getattr(allergy, "severity", "")
            rows.append(
                f"<tr>"
                f"<td>{self._escape(allergy.substance)}</td>"
                f"<td>{self._escape(reaction)}</td>"
                f"<td>{severity}</td>"
                f"</tr>"
            )

        return f"""<text>
  <table border="1" width="100%">
    <thead>
      <tr><th>Substance</th><th>Reaction</th><th>Severity</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</text>"""

    def build_results_narrative(self, labs: list[Any]) -> str:
        """Build results section narrative."""
        if not labs:
            return "<text>No laboratory results</text>"

        rows = []
        for lab in labs:
            collected = ""
            if hasattr(lab, "collected_time") and lab.collected_time:
                collected = lab.collected_time.strftime("%Y-%m-%d")
            unit = getattr(lab, "unit", "")
            ref_range = getattr(lab, "reference_range", "")
            rows.append(
                f"<tr>"
                f"<td>{self._escape(lab.test_name)}</td>"
                f"<td>{lab.value} {unit}</td>"
                f"<td>{ref_range}</td>"
                f"<td>{collected}</td>"
                f"</tr>"
            )

        return f"""<text>
  <table border="1" width="100%">
    <thead>
      <tr><th>Test</th><th>Result</th><th>Reference</th><th>Date</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</text>"""

    def build_vital_signs_narrative(self, vitals: list[Any]) -> str:
        """Build vital signs section narrative."""
        if not vitals:
            return "<text>No vital signs recorded</text>"

        rows = []
        for v in vitals:
            obs_time = ""
            if hasattr(v, "observation_time") and v.observation_time:
                obs_time = v.observation_time.strftime("%Y-%m-%d %H:%M")

            bp = ""
            if getattr(v, "systolic_bp", None):
                bp = f"{v.systolic_bp}/{getattr(v, 'diastolic_bp', '')}"

            rows.append(
                f"<tr>"
                f"<td>{obs_time}</td>"
                f"<td>{bp}</td>"
                f"<td>{getattr(v, 'heart_rate', '') or ''}</td>"
                f"<td>{getattr(v, 'respiratory_rate', '') or ''}</td>"
                f"<td>{getattr(v, 'temperature', '') or ''}</td>"
                f"<td>{getattr(v, 'spo2', '') or ''}</td>"
                f"</tr>"
            )

        return f"""<text>
  <table border="1" width="100%">
    <thead>
      <tr><th>Date/Time</th><th>BP</th><th>HR</th><th>RR</th><th>Temp</th><th>SpO2</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</text>"""

    def build_procedures_narrative(self, procedures: list[Any]) -> str:
        """Build procedures section narrative."""
        if not procedures:
            return "<text>No procedures documented</text>"

        rows = []
        for proc in procedures:
            proc_date = ""
            if hasattr(proc, "procedure_date") and proc.procedure_date:
                proc_date = proc.procedure_date.strftime("%Y-%m-%d")
            rows.append(
                f"<tr>"
                f"<td>{self._escape(proc.description)}</td>"
                f"<td>{proc.code}</td>"
                f"<td>{proc_date}</td>"
                f"</tr>"
            )

        return f"""<text>
  <table border="1" width="100%">
    <thead>
      <tr><th>Procedure</th><th>Code</th><th>Date</th></tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</text>"""

    def _escape(self, text: str | None) -> str:
        if text is None:
            return ""
        return html.escape(str(text))

"""C-CDA transformer.

Converts PatientSim objects to C-CDA XML documents.
"""

import html
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from healthsim_agent.products.patientsim.formats.ccda.header import HeaderBuilder


class DocumentType(Enum):
    """C-CDA document types with template OID, LOINC code, and display name."""

    CCD = ("2.16.840.1.113883.10.20.22.1.2", "34133-9", "Continuity of Care Document")
    DISCHARGE_SUMMARY = ("2.16.840.1.113883.10.20.22.1.8", "18842-5", "Discharge Summary")
    REFERRAL_NOTE = ("2.16.840.1.113883.10.20.22.1.14", "57133-1", "Referral Note")
    TRANSFER_SUMMARY = ("2.16.840.1.113883.10.20.22.1.13", "18761-7", "Transfer Summary")

    @property
    def template_oid(self) -> str:
        return self.value[0]

    @property
    def loinc_code(self) -> str:
        return self.value[1]

    @property
    def display_name(self) -> str:
        return self.value[2]


@dataclass
class CCDAConfig:
    """Configuration for C-CDA document generation."""

    document_type: DocumentType
    organization_name: str
    organization_oid: str
    author_name: str | None = None
    author_npi: str | None = None
    custodian_name: str | None = field(default=None)
    custodian_oid: str | None = field(default=None)

    def __post_init__(self) -> None:
        if self.custodian_name is None:
            self.custodian_name = self.organization_name
        if self.custodian_oid is None:
            self.custodian_oid = self.organization_oid


class CCDATransformer:
    """Transforms PatientSim objects to C-CDA XML documents."""

    SNOMED_OID = "2.16.840.1.113883.6.96"
    LOINC_OID = "2.16.840.1.113883.6.1"
    RXNORM_OID = "2.16.840.1.113883.6.88"
    ICD10_OID = "2.16.840.1.113883.6.90"

    PROBLEMS_SECTION_OID = "2.16.840.1.113883.10.20.22.2.5.1"
    MEDICATIONS_SECTION_OID = "2.16.840.1.113883.10.20.22.2.1.1"
    RESULTS_SECTION_OID = "2.16.840.1.113883.10.20.22.2.3.1"
    VITAL_SIGNS_SECTION_OID = "2.16.840.1.113883.10.20.22.2.4.1"
    PROCEDURES_SECTION_OID = "2.16.840.1.113883.10.20.22.2.7.1"

    PROBLEM_CONCERN_OID = "2.16.840.1.113883.10.20.22.4.3"
    PROBLEM_OBSERVATION_OID = "2.16.840.1.113883.10.20.22.4.4"
    MEDICATION_ACTIVITY_OID = "2.16.840.1.113883.10.20.22.4.16"
    RESULT_ORGANIZER_OID = "2.16.840.1.113883.10.20.22.4.1"
    RESULT_OBSERVATION_OID = "2.16.840.1.113883.10.20.22.4.2"
    VITAL_SIGNS_ORGANIZER_OID = "2.16.840.1.113883.10.20.22.4.26"
    VITAL_SIGNS_OBSERVATION_OID = "2.16.840.1.113883.10.20.22.4.27"
    PROCEDURE_ACTIVITY_OID = "2.16.840.1.113883.10.20.22.4.14"

    def __init__(self, config: CCDAConfig) -> None:
        self.config = config
        self._header_builder = HeaderBuilder(config)

    def transform(
        self,
        patient: Any,
        encounters: list[Any] | None = None,
        diagnoses: list[Any] | None = None,
        medications: list[Any] | None = None,
        labs: list[Any] | None = None,
        vitals: list[Any] | None = None,
        procedures: list[Any] | None = None,
    ) -> str:
        """Transform PatientSim data to C-CDA XML document."""
        primary_encounter = encounters[0] if encounters else None

        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            self._build_clinical_document_open(),
            self._header_builder.build_header(patient, primary_encounter),
            "<component>",
            "<structuredBody>",
        ]

        if diagnoses:
            xml_parts.append(self._build_problems_section(diagnoses))
        if medications:
            xml_parts.append(self._build_medications_section(medications))
        if labs:
            xml_parts.append(self._build_results_section(labs))
        if vitals:
            xml_parts.append(self._build_vital_signs_section(vitals))
        if procedures:
            xml_parts.append(self._build_procedures_section(procedures))

        xml_parts.extend(["</structuredBody>", "</component>", "</ClinicalDocument>"])
        return "\n".join(xml_parts)

    def _build_clinical_document_open(self) -> str:
        doc_type = self.config.document_type
        doc_id = str(uuid.uuid4())
        effective_time = datetime.now().strftime("%Y%m%d%H%M%S")

        return f"""<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <realmCode code="US"/>
  <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
  <templateId root="2.16.840.1.113883.10.20.22.1.1" extension="2015-08-01"/>
  <templateId root="{doc_type.template_oid}" extension="2015-08-01"/>
  <id root="{self.config.organization_oid}" extension="{doc_id}"/>
  <code code="{doc_type.loinc_code}" codeSystem="{self.LOINC_OID}" displayName="{doc_type.display_name}"/>
  <title>{doc_type.display_name}</title>
  <effectiveTime value="{effective_time}"/>
  <confidentialityCode code="N" codeSystem="2.16.840.1.113883.5.25"/>
  <languageCode code="en-US"/>"""

    def _build_problems_section(self, diagnoses: list[Any]) -> str:
        rows = []
        for diag in diagnoses:
            status = "Active" if getattr(diag, "is_active", True) else "Resolved"
            rows.append(
                f"<tr><td>{self._escape_xml(diag.description)}</td>"
                f"<td>{diag.code}</td><td>{status}</td></tr>"
            )

        narrative = f"""<text>
  <table border="1"><thead><tr><th>Problem</th><th>Code</th><th>Status</th></tr></thead>
  <tbody>{"".join(rows)}</tbody></table>
</text>"""

        entries = [self._build_problem_entry(d) for d in diagnoses]

        return f"""<component>
  <section>
    <templateId root="{self.PROBLEMS_SECTION_OID}"/>
    <code code="11450-4" codeSystem="{self.LOINC_OID}" displayName="Problem List"/>
    <title>Problems</title>
    {narrative}
    {"".join(entries)}
  </section>
</component>"""

    def _build_problem_entry(self, diag: Any) -> str:
        entry_id = str(uuid.uuid4())
        obs_id = str(uuid.uuid4())
        status_code = "active" if getattr(diag, "is_active", True) else "completed"
        onset = ""
        if hasattr(diag, "diagnosed_date") and diag.diagnosed_date:
            onset = diag.diagnosed_date.strftime("%Y%m%d")

        return f"""<entry typeCode="DRIV">
  <act classCode="ACT" moodCode="EVN">
    <templateId root="{self.PROBLEM_CONCERN_OID}"/>
    <id root="{entry_id}"/>
    <code code="CONC" codeSystem="2.16.840.1.113883.5.6"/>
    <statusCode code="{status_code}"/>
    <effectiveTime><low value="{onset}"/></effectiveTime>
    <entryRelationship typeCode="SUBJ">
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="{self.PROBLEM_OBSERVATION_OID}"/>
        <id root="{obs_id}"/>
        <code code="64572001" codeSystem="{self.SNOMED_OID}"/>
        <statusCode code="completed"/>
        <value xsi:type="CD" code="{diag.code}" codeSystem="{self.ICD10_OID}" displayName="{self._escape_xml(diag.description)}"/>
      </observation>
    </entryRelationship>
  </act>
</entry>"""

    def _build_medications_section(self, medications: list[Any]) -> str:
        rows = []
        for med in medications:
            status = getattr(med, "status", "active")
            dose = getattr(med, "dose", "")
            unit = getattr(med, "unit", "")
            freq = getattr(med, "frequency", "")
            rows.append(
                f"<tr><td>{self._escape_xml(med.drug_name)}</td>"
                f"<td>{dose} {unit}</td><td>{freq}</td><td>{status}</td></tr>"
            )

        narrative = f"""<text>
  <table border="1"><thead><tr><th>Medication</th><th>Dose</th><th>Frequency</th><th>Status</th></tr></thead>
  <tbody>{"".join(rows)}</tbody></table>
</text>"""

        entries = [self._build_medication_entry(m) for m in medications]

        return f"""<component>
  <section>
    <templateId root="{self.MEDICATIONS_SECTION_OID}"/>
    <code code="10160-0" codeSystem="{self.LOINC_OID}" displayName="History of Medication Use"/>
    <title>Medications</title>
    {narrative}
    {"".join(entries)}
  </section>
</component>"""

    def _build_medication_entry(self, med: Any) -> str:
        entry_id = str(uuid.uuid4())
        status = "active" if getattr(med, "status", "active") == "active" else "completed"
        rxnorm = getattr(med, "rxnorm_code", "") or ""

        return f"""<entry typeCode="DRIV">
  <substanceAdministration classCode="SBADM" moodCode="EVN">
    <templateId root="{self.MEDICATION_ACTIVITY_OID}"/>
    <id root="{entry_id}"/>
    <statusCode code="{status}"/>
    <consumable>
      <manufacturedProduct classCode="MANU">
        <manufacturedMaterial>
          <code code="{rxnorm}" codeSystem="{self.RXNORM_OID}" displayName="{self._escape_xml(med.drug_name)}"/>
        </manufacturedMaterial>
      </manufacturedProduct>
    </consumable>
  </substanceAdministration>
</entry>"""

    def _build_results_section(self, labs: list[Any]) -> str:
        rows = []
        for lab in labs:
            collected = ""
            if hasattr(lab, "collected_time") and lab.collected_time:
                collected = lab.collected_time.strftime("%Y-%m-%d")
            rows.append(
                f"<tr><td>{self._escape_xml(lab.test_name)}</td>"
                f"<td>{lab.value} {getattr(lab, 'unit', '')}</td><td>{collected}</td></tr>"
            )

        narrative = f"""<text>
  <table border="1"><thead><tr><th>Test</th><th>Result</th><th>Date</th></tr></thead>
  <tbody>{"".join(rows)}</tbody></table>
</text>"""

        entries = [self._build_result_entry(l) for l in labs]

        return f"""<component>
  <section>
    <templateId root="{self.RESULTS_SECTION_OID}"/>
    <code code="30954-2" codeSystem="{self.LOINC_OID}" displayName="Results"/>
    <title>Results</title>
    {narrative}
    {"".join(entries)}
  </section>
</component>"""

    def _build_result_entry(self, lab: Any) -> str:
        org_id = str(uuid.uuid4())
        obs_id = str(uuid.uuid4())
        loinc = getattr(lab, "loinc_code", "") or ""
        collected = ""
        if hasattr(lab, "collected_time") and lab.collected_time:
            collected = lab.collected_time.strftime("%Y%m%d%H%M%S")

        return f"""<entry typeCode="DRIV">
  <organizer classCode="CLUSTER" moodCode="EVN">
    <templateId root="{self.RESULT_ORGANIZER_OID}"/>
    <id root="{org_id}"/>
    <code code="{loinc}" codeSystem="{self.LOINC_OID}" displayName="{self._escape_xml(lab.test_name)}"/>
    <statusCode code="completed"/>
    <component>
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="{self.RESULT_OBSERVATION_OID}"/>
        <id root="{obs_id}"/>
        <code code="{loinc}" codeSystem="{self.LOINC_OID}"/>
        <statusCode code="completed"/>
        <effectiveTime value="{collected}"/>
        <value xsi:type="PQ" value="{lab.value}" unit="{getattr(lab, 'unit', '')}"/>
      </observation>
    </component>
  </organizer>
</entry>"""

    def _build_vital_signs_section(self, vitals: list[Any]) -> str:
        rows = []
        for v in vitals:
            obs_time = ""
            if hasattr(v, "observation_time") and v.observation_time:
                obs_time = v.observation_time.strftime("%Y-%m-%d %H:%M")
            bp = ""
            if getattr(v, "systolic_bp", None):
                bp = f"{v.systolic_bp}/{getattr(v, 'diastolic_bp', '')}"
            rows.append(
                f"<tr><td>{obs_time}</td><td>{bp}</td>"
                f"<td>{getattr(v, 'heart_rate', '') or ''}</td>"
                f"<td>{getattr(v, 'respiratory_rate', '') or ''}</td></tr>"
            )

        narrative = f"""<text>
  <table border="1"><thead><tr><th>Date</th><th>BP</th><th>HR</th><th>RR</th></tr></thead>
  <tbody>{"".join(rows)}</tbody></table>
</text>"""

        entries = [self._build_vital_signs_entry(v) for v in vitals]

        return f"""<component>
  <section>
    <templateId root="{self.VITAL_SIGNS_SECTION_OID}"/>
    <code code="8716-3" codeSystem="{self.LOINC_OID}" displayName="Vital Signs"/>
    <title>Vital Signs</title>
    {narrative}
    {"".join(entries)}
  </section>
</component>"""

    def _build_vital_signs_entry(self, vital: Any) -> str:
        org_id = str(uuid.uuid4())
        obs_time = ""
        if hasattr(vital, "observation_time") and vital.observation_time:
            obs_time = vital.observation_time.strftime("%Y%m%d%H%M%S")

        observations = []
        mappings = [
            ("systolic_bp", "8480-6", "Systolic BP", "mm[Hg]"),
            ("diastolic_bp", "8462-4", "Diastolic BP", "mm[Hg]"),
            ("heart_rate", "8867-4", "Heart rate", "/min"),
            ("respiratory_rate", "9279-1", "Respiratory rate", "/min"),
            ("temperature", "8310-5", "Temperature", "[degF]"),
            ("spo2", "2708-6", "SpO2", "%"),
        ]

        for attr, loinc, display, unit in mappings:
            value = getattr(vital, attr, None)
            if value is not None:
                obs_id = str(uuid.uuid4())
                observations.append(
                    f"""<component>
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="{self.VITAL_SIGNS_OBSERVATION_OID}"/>
        <id root="{obs_id}"/>
        <code code="{loinc}" codeSystem="{self.LOINC_OID}" displayName="{display}"/>
        <statusCode code="completed"/>
        <effectiveTime value="{obs_time}"/>
        <value xsi:type="PQ" value="{value}" unit="{unit}"/>
      </observation>
    </component>"""
                )

        return f"""<entry typeCode="DRIV">
  <organizer classCode="CLUSTER" moodCode="EVN">
    <templateId root="{self.VITAL_SIGNS_ORGANIZER_OID}"/>
    <id root="{org_id}"/>
    <code code="46680005" codeSystem="{self.SNOMED_OID}" displayName="Vital signs"/>
    <statusCode code="completed"/>
    <effectiveTime value="{obs_time}"/>
    {"".join(observations)}
  </organizer>
</entry>"""

    def _build_procedures_section(self, procedures: list[Any]) -> str:
        rows = []
        for p in procedures:
            proc_date = ""
            if hasattr(p, "procedure_date") and p.procedure_date:
                proc_date = p.procedure_date.strftime("%Y-%m-%d")
            rows.append(
                f"<tr><td>{self._escape_xml(p.description)}</td>"
                f"<td>{p.code}</td><td>{proc_date}</td></tr>"
            )

        narrative = f"""<text>
  <table border="1"><thead><tr><th>Procedure</th><th>Code</th><th>Date</th></tr></thead>
  <tbody>{"".join(rows)}</tbody></table>
</text>"""

        entries = [self._build_procedure_entry(p) for p in procedures]

        return f"""<component>
  <section>
    <templateId root="{self.PROCEDURES_SECTION_OID}"/>
    <code code="47519-4" codeSystem="{self.LOINC_OID}" displayName="History of Procedures"/>
    <title>Procedures</title>
    {narrative}
    {"".join(entries)}
  </section>
</component>"""

    def _build_procedure_entry(self, proc: Any) -> str:
        entry_id = str(uuid.uuid4())
        proc_time = ""
        if hasattr(proc, "procedure_date") and proc.procedure_date:
            proc_time = proc.procedure_date.strftime("%Y%m%d")

        code_system = self.SNOMED_OID
        if hasattr(proc, "code_system") and proc.code_system and "cpt" in proc.code_system.lower():
            code_system = "2.16.840.1.113883.6.12"

        return f"""<entry typeCode="DRIV">
  <procedure classCode="PROC" moodCode="EVN">
    <templateId root="{self.PROCEDURE_ACTIVITY_OID}"/>
    <id root="{entry_id}"/>
    <code code="{proc.code}" codeSystem="{code_system}" displayName="{self._escape_xml(proc.description)}"/>
    <statusCode code="completed"/>
    <effectiveTime value="{proc_time}"/>
  </procedure>
</entry>"""

    def _escape_xml(self, text: str | None) -> str:
        if text is None:
            return ""
        return html.escape(str(text))

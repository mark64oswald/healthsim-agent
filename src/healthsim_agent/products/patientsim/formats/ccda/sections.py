"""C-CDA section builders for structured clinical content."""

from __future__ import annotations

import uuid
from typing import Any

from healthsim_agent.products.patientsim.formats.ccda.vocabulary import (
    CODE_SYSTEMS,
    CodedValue,
    create_loinc_code,
    create_snomed_code,
)


class SectionBuilder:
    """Builds individual C-CDA section entries."""

    SNOMED_OID = CODE_SYSTEMS["SNOMED"][0]
    LOINC_OID = CODE_SYSTEMS["LOINC"][0]
    ICD10_OID = CODE_SYSTEMS["ICD10CM"][0]
    RXNORM_OID = CODE_SYSTEMS["RXNORM"][0]

    def build_problem_entry(
        self,
        diagnosis: Any,
        template_oid: str = "2.16.840.1.113883.10.20.22.4.3",
    ) -> str:
        """Build a problem concern act entry."""
        entry_id = str(uuid.uuid4())
        obs_id = str(uuid.uuid4())
        status = "active" if getattr(diagnosis, "is_active", True) else "completed"

        onset = ""
        if hasattr(diagnosis, "diagnosed_date") and diagnosis.diagnosed_date:
            onset = diagnosis.diagnosed_date.strftime("%Y%m%d")

        return f"""<entry typeCode="DRIV">
  <act classCode="ACT" moodCode="EVN">
    <templateId root="{template_oid}" extension="2015-08-01"/>
    <id root="{entry_id}"/>
    <code code="CONC" codeSystem="2.16.840.1.113883.5.6" displayName="Concern"/>
    <statusCode code="{status}"/>
    <effectiveTime><low value="{onset}"/></effectiveTime>
    <entryRelationship typeCode="SUBJ">
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="2.16.840.1.113883.10.20.22.4.4" extension="2015-08-01"/>
        <id root="{obs_id}"/>
        <code code="64572001" codeSystem="{self.SNOMED_OID}" displayName="Condition"/>
        <statusCode code="completed"/>
        <effectiveTime><low value="{onset}"/></effectiveTime>
        <value xsi:type="CD" code="{diagnosis.code}" codeSystem="{self.ICD10_OID}" 
               codeSystemName="ICD-10-CM" displayName="{diagnosis.description}"/>
      </observation>
    </entryRelationship>
  </act>
</entry>"""

    def build_medication_entry(
        self,
        medication: Any,
        template_oid: str = "2.16.840.1.113883.10.20.22.4.16",
    ) -> str:
        """Build a medication activity entry."""
        entry_id = str(uuid.uuid4())
        status = "active" if getattr(medication, "status", "active") == "active" else "completed"

        rxnorm = getattr(medication, "rxnorm_code", "") or ""
        dose = getattr(medication, "dose", "")
        unit = getattr(medication, "unit", "")

        dose_xml = ""
        if dose:
            dose_xml = f'<doseQuantity value="{dose}" unit="{unit}"/>'

        return f"""<entry typeCode="DRIV">
  <substanceAdministration classCode="SBADM" moodCode="EVN">
    <templateId root="{template_oid}" extension="2014-06-09"/>
    <id root="{entry_id}"/>
    <statusCode code="{status}"/>
    {dose_xml}
    <consumable>
      <manufacturedProduct classCode="MANU">
        <templateId root="2.16.840.1.113883.10.20.22.4.23" extension="2014-06-09"/>
        <manufacturedMaterial>
          <code code="{rxnorm}" codeSystem="{self.RXNORM_OID}" 
                codeSystemName="RxNorm" displayName="{medication.drug_name}"/>
        </manufacturedMaterial>
      </manufacturedProduct>
    </consumable>
  </substanceAdministration>
</entry>"""

    def build_result_entry(
        self,
        lab_result: Any,
        template_oid: str = "2.16.840.1.113883.10.20.22.4.1",
    ) -> str:
        """Build a result organizer entry."""
        org_id = str(uuid.uuid4())
        obs_id = str(uuid.uuid4())

        loinc = getattr(lab_result, "loinc_code", "") or ""
        unit = getattr(lab_result, "unit", "")

        collected = ""
        if hasattr(lab_result, "collected_time") and lab_result.collected_time:
            collected = lab_result.collected_time.strftime("%Y%m%d%H%M%S")

        return f"""<entry typeCode="DRIV">
  <organizer classCode="CLUSTER" moodCode="EVN">
    <templateId root="{template_oid}" extension="2015-08-01"/>
    <id root="{org_id}"/>
    <code code="{loinc}" codeSystem="{self.LOINC_OID}" 
          codeSystemName="LOINC" displayName="{lab_result.test_name}"/>
    <statusCode code="completed"/>
    <effectiveTime value="{collected}"/>
    <component>
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="2.16.840.1.113883.10.20.22.4.2" extension="2015-08-01"/>
        <id root="{obs_id}"/>
        <code code="{loinc}" codeSystem="{self.LOINC_OID}" displayName="{lab_result.test_name}"/>
        <statusCode code="completed"/>
        <effectiveTime value="{collected}"/>
        <value xsi:type="PQ" value="{lab_result.value}" unit="{unit}"/>
      </observation>
    </component>
  </organizer>
</entry>"""

    def build_vital_sign_entry(
        self,
        vital: Any,
        template_oid: str = "2.16.840.1.113883.10.20.22.4.26",
    ) -> str:
        """Build a vital signs organizer entry."""
        org_id = str(uuid.uuid4())

        obs_time = ""
        if hasattr(vital, "observation_time") and vital.observation_time:
            obs_time = vital.observation_time.strftime("%Y%m%d%H%M%S")

        observations = []
        mappings = [
            ("systolic_bp", "8480-6", "Systolic blood pressure", "mm[Hg]"),
            ("diastolic_bp", "8462-4", "Diastolic blood pressure", "mm[Hg]"),
            ("heart_rate", "8867-4", "Heart rate", "/min"),
            ("respiratory_rate", "9279-1", "Respiratory rate", "/min"),
            ("temperature", "8310-5", "Body temperature", "[degF]"),
            ("spo2", "2708-6", "Oxygen saturation", "%"),
        ]

        for attr, loinc, display, unit in mappings:
            value = getattr(vital, attr, None)
            if value is not None:
                obs_id = str(uuid.uuid4())
                observations.append(
                    f"""<component>
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="2.16.840.1.113883.10.20.22.4.27" extension="2014-06-09"/>
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
    <templateId root="{template_oid}" extension="2014-06-09"/>
    <id root="{org_id}"/>
    <code code="46680005" codeSystem="{self.SNOMED_OID}" displayName="Vital signs"/>
    <statusCode code="completed"/>
    <effectiveTime value="{obs_time}"/>
    {"".join(observations)}
  </organizer>
</entry>"""

    def build_procedure_entry(
        self,
        procedure: Any,
        template_oid: str = "2.16.840.1.113883.10.20.22.4.14",
    ) -> str:
        """Build a procedure activity entry."""
        entry_id = str(uuid.uuid4())

        proc_time = ""
        if hasattr(procedure, "procedure_date") and procedure.procedure_date:
            proc_time = procedure.procedure_date.strftime("%Y%m%d")

        code_system = self.SNOMED_OID
        code_system_name = "SNOMED CT"
        if hasattr(procedure, "code_system") and procedure.code_system:
            if "cpt" in procedure.code_system.lower():
                code_system = "2.16.840.1.113883.6.12"
                code_system_name = "CPT"

        return f"""<entry typeCode="DRIV">
  <procedure classCode="PROC" moodCode="EVN">
    <templateId root="{template_oid}" extension="2014-06-09"/>
    <id root="{entry_id}"/>
    <code code="{procedure.code}" codeSystem="{code_system}" 
          codeSystemName="{code_system_name}" displayName="{procedure.description}"/>
    <statusCode code="completed"/>
    <effectiveTime value="{proc_time}"/>
  </procedure>
</entry>"""

    def build_allergy_entry(
        self,
        allergy: Any,
        template_oid: str = "2.16.840.1.113883.10.20.22.4.30",
    ) -> str:
        """Build an allergy concern act entry."""
        entry_id = str(uuid.uuid4())
        obs_id = str(uuid.uuid4())
        status = "active" if getattr(allergy, "is_active", True) else "completed"

        substance = getattr(allergy, "substance", "Unknown")
        reaction = getattr(allergy, "reaction", "")
        severity = getattr(allergy, "severity", "")

        reaction_xml = ""
        if reaction:
            reaction_xml = f"""<entryRelationship typeCode="MFST" inversionInd="true">
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="2.16.840.1.113883.10.20.22.4.9"/>
        <code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
        <statusCode code="completed"/>
        <value xsi:type="CD" code="" codeSystem="{self.SNOMED_OID}" displayName="{reaction}"/>
      </observation>
    </entryRelationship>"""

        return f"""<entry typeCode="DRIV">
  <act classCode="ACT" moodCode="EVN">
    <templateId root="{template_oid}" extension="2015-08-01"/>
    <id root="{entry_id}"/>
    <code code="CONC" codeSystem="2.16.840.1.113883.5.6"/>
    <statusCode code="{status}"/>
    <entryRelationship typeCode="SUBJ">
      <observation classCode="OBS" moodCode="EVN">
        <templateId root="2.16.840.1.113883.10.20.22.4.7" extension="2014-06-09"/>
        <id root="{obs_id}"/>
        <code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
        <statusCode code="completed"/>
        <value xsi:type="CD" code="419199007" codeSystem="{self.SNOMED_OID}" displayName="Allergy to substance"/>
        <participant typeCode="CSM">
          <participantRole classCode="MANU">
            <playingEntity classCode="MMAT">
              <code nullFlavor="UNK">
                <originalText>{substance}</originalText>
              </code>
            </playingEntity>
          </participantRole>
        </participant>
        {reaction_xml}
      </observation>
    </entryRelationship>
  </act>
</entry>"""

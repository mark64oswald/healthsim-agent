"""C-CDA header builder.

Builds the CDA header elements including recordTarget, author, custodian,
and encompassingEncounter.
"""

from __future__ import annotations

import html
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from healthsim_agent.products.patientsim.formats.ccda.transformer import CCDAConfig


class HeaderBuilder:
    """Builds C-CDA document header elements."""

    ADMIN_GENDER_OID = "2.16.840.1.113883.5.1"

    def __init__(self, config: "CCDAConfig") -> None:
        self.config = config

    def build_header(self, patient: Any, encounter: Any | None = None) -> str:
        """Build complete CDA header."""
        parts = [
            self._build_record_target(patient),
            self._build_author(),
            self._build_custodian(),
        ]
        if encounter:
            parts.append(self._build_encompassing_encounter(encounter))
        return "\n".join(parts)

    def _build_record_target(self, patient: Any) -> str:
        """Build recordTarget element with patient demographics."""
        birth_date = patient.birth_date.strftime("%Y%m%d") if patient.birth_date else ""
        gender_map = {"M": "M", "F": "F", "O": "UN", "U": "UN"}
        gender_code = gender_map.get(patient.gender, "UN")
        gender_display = {"M": "Male", "F": "Female", "UN": "Undifferentiated"}.get(
            gender_code, "Undifferentiated"
        )

        address_xml = '<addr nullFlavor="UNK"/>'
        if hasattr(patient, "address") and patient.address:
            addr = patient.address
            street = self._escape_xml(getattr(addr, "street_address", ""))
            city = self._escape_xml(getattr(addr, "city", ""))
            state = self._escape_xml(getattr(addr, "state", ""))
            postal = self._escape_xml(getattr(addr, "postal_code", ""))
            address_xml = f"""<addr use="HP">
          <streetAddressLine>{street}</streetAddressLine>
          <city>{city}</city>
          <state>{state}</state>
          <postalCode>{postal}</postalCode>
          <country>US</country>
        </addr>"""

        telecom_xml = '<telecom nullFlavor="UNK"/>'
        if hasattr(patient, "phone") and patient.phone:
            telecom_xml = f'<telecom use="HP" value="tel:{patient.phone}"/>'

        mrn = getattr(patient, "mrn", getattr(patient, "patient_id", "UNKNOWN"))

        return f"""<recordTarget>
    <patientRole>
      <id root="{self.config.organization_oid}" extension="{mrn}"/>
      {address_xml}
      {telecom_xml}
      <patient>
        <name use="L">
          <given>{self._escape_xml(patient.given_name)}</given>
          <family>{self._escape_xml(patient.family_name)}</family>
        </name>
        <administrativeGenderCode code="{gender_code}" codeSystem="{self.ADMIN_GENDER_OID}" displayName="{gender_display}"/>
        <birthTime value="{birth_date}"/>
      </patient>
    </patientRole>
  </recordTarget>"""

    def _build_author(self) -> str:
        """Build author element."""
        author_time = datetime.now().strftime("%Y%m%d%H%M%S")
        author_id = str(uuid.uuid4())

        name_xml = '<name nullFlavor="UNK"/>'
        if self.config.author_name:
            name_parts = self.config.author_name.split(" ", 1)
            given = self._escape_xml(name_parts[0])
            family = self._escape_xml(name_parts[1]) if len(name_parts) > 1 else ""
            name_xml = f"""<name>
            <given>{given}</given>
            <family>{family}</family>
          </name>"""

        id_xml = f'<id root="{author_id}"/>'
        if self.config.author_npi:
            id_xml = f'<id root="2.16.840.1.113883.4.6" extension="{self.config.author_npi}"/>'

        return f"""<author>
    <time value="{author_time}"/>
    <assignedAuthor>
      {id_xml}
      <addr nullFlavor="UNK"/>
      <telecom nullFlavor="UNK"/>
      <assignedPerson>
        {name_xml}
      </assignedPerson>
      <representedOrganization>
        <id root="{self.config.organization_oid}"/>
        <name>{self._escape_xml(self.config.organization_name)}</name>
      </representedOrganization>
    </assignedAuthor>
  </author>"""

    def _build_custodian(self) -> str:
        """Build custodian element."""
        custodian_name = self.config.custodian_name or self.config.organization_name
        custodian_oid = self.config.custodian_oid or self.config.organization_oid

        return f"""<custodian>
    <assignedCustodian>
      <representedCustodianOrganization>
        <id root="{custodian_oid}"/>
        <name>{self._escape_xml(custodian_name)}</name>
        <telecom nullFlavor="UNK"/>
        <addr nullFlavor="UNK"/>
      </representedCustodianOrganization>
    </assignedCustodian>
  </custodian>"""

    def _build_encompassing_encounter(self, encounter: Any) -> str:
        """Build componentOf/encompassingEncounter element."""
        start_time = ""
        end_time = ""
        if hasattr(encounter, "admission_time") and encounter.admission_time:
            start_time = encounter.admission_time.strftime("%Y%m%d%H%M%S")
        if hasattr(encounter, "discharge_time") and encounter.discharge_time:
            end_time = encounter.discharge_time.strftime("%Y%m%d%H%M%S")

        if start_time and end_time:
            effective_time = f"""<effectiveTime>
        <low value="{start_time}"/>
        <high value="{end_time}"/>
      </effectiveTime>"""
        elif start_time:
            effective_time = f"""<effectiveTime>
        <low value="{start_time}"/>
      </effectiveTime>"""
        else:
            effective_time = '<effectiveTime nullFlavor="UNK"/>'

        discharge_xml = ""
        if hasattr(encounter, "discharge_disposition") and encounter.discharge_disposition:
            discharge_xml = f"""<dischargeDispositionCode code="{self._escape_xml(encounter.discharge_disposition)}" codeSystem="2.16.840.1.113883.12.112"/>"""

        encounter_id = getattr(encounter, "encounter_id", "UNKNOWN")

        return f"""<componentOf>
    <encompassingEncounter>
      <id root="{self.config.organization_oid}" extension="{encounter_id}"/>
      {effective_time}
      {discharge_xml}
      <location>
        <healthCareFacility>
          <id root="{self.config.organization_oid}"/>
          <serviceProviderOrganization>
            <id root="{self.config.organization_oid}"/>
            <name>{self._escape_xml(self.config.organization_name)}</name>
          </serviceProviderOrganization>
        </healthCareFacility>
      </location>
    </encompassingEncounter>
  </componentOf>"""

    def _escape_xml(self, text: str | None) -> str:
        if text is None:
            return ""
        return html.escape(str(text))

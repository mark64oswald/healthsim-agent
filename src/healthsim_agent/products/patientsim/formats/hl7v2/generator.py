"""HL7v2 message generator.

Ported from: healthsim-workspace/packages/patientsim/src/patientsim/formats/hl7v2/generator.py
"""

import uuid
from datetime import datetime

from healthsim_agent.products.patientsim.core.models import Diagnosis, Encounter, Patient
from healthsim_agent.products.patientsim.formats.hl7v2.segments import (
    build_dg1_segment,
    build_evn_segment,
    build_msh_segment,
    build_pid_segment,
    build_pv1_segment,
)


class HL7v2Generator:
    """Generates HL7v2 messages from PatientSim objects."""

    def __init__(
        self,
        sending_application: str = "PATIENTSIM",
        sending_facility: str = "HOSPITAL",
        receiving_application: str = "EMR",
        receiving_facility: str = "HOSPITAL",
    ) -> None:
        self.sending_application = sending_application
        self.sending_facility = sending_facility
        self.receiving_application = receiving_application
        self.receiving_facility = receiving_facility

    def _generate_message_control_id(self) -> str:
        return str(uuid.uuid4())[:20].replace("-", "").upper()

    def _build_message(self, segments: list[str]) -> str:
        return "\r".join(segments) + "\r"

    def generate_adt_a01(
        self,
        patient: Patient,
        encounter: Encounter,
        diagnoses: list[Diagnosis] | None = None,
        timestamp: datetime | None = None,
    ) -> str:
        """Generate ADT^A01 (Admit/visit notification) message."""
        timestamp = timestamp or datetime.now()
        event_timestamp = encounter.admission_time or timestamp
        message_control_id = self._generate_message_control_id()

        segments = [
            build_msh_segment(
                message_type="ADT",
                trigger_event="A01",
                message_control_id=message_control_id,
                timestamp=timestamp,
                sending_application=self.sending_application,
                sending_facility=self.sending_facility,
                receiving_application=self.receiving_application,
                receiving_facility=self.receiving_facility,
            ),
            build_evn_segment(event_type="A01", event_timestamp=event_timestamp),
            build_pid_segment(patient),
            build_pv1_segment(encounter),
        ]

        if diagnoses:
            for idx, diagnosis in enumerate(diagnoses, start=1):
                diag_type = diagnosis.type.value if hasattr(diagnosis.type, "value") else str(diagnosis.type)
                segments.append(build_dg1_segment(
                    diagnosis_code=diagnosis.code,
                    diagnosis_text=diagnosis.description,
                    set_id=idx,
                    diagnosis_type="F" if diag_type == "final" else "W",
                ))

        return self._build_message(segments)

    def generate_adt_a03(
        self,
        patient: Patient,
        encounter: Encounter,
        diagnoses: list[Diagnosis] | None = None,
        timestamp: datetime | None = None,
    ) -> str:
        """Generate ADT^A03 (Discharge/end visit) message."""
        timestamp = timestamp or datetime.now()
        event_timestamp = encounter.discharge_time or timestamp
        message_control_id = self._generate_message_control_id()

        segments = [
            build_msh_segment(
                message_type="ADT",
                trigger_event="A03",
                message_control_id=message_control_id,
                timestamp=timestamp,
                sending_application=self.sending_application,
                sending_facility=self.sending_facility,
                receiving_application=self.receiving_application,
                receiving_facility=self.receiving_facility,
            ),
            build_evn_segment(event_type="A03", event_timestamp=event_timestamp),
            build_pid_segment(patient),
            build_pv1_segment(encounter),
        ]

        if diagnoses:
            for idx, diagnosis in enumerate(diagnoses, start=1):
                segments.append(build_dg1_segment(
                    diagnosis_code=diagnosis.code,
                    diagnosis_text=diagnosis.description,
                    set_id=idx,
                    diagnosis_type="F",
                ))

        return self._build_message(segments)

    def generate_adt_a08(
        self,
        patient: Patient,
        encounter: Encounter,
        diagnoses: list[Diagnosis] | None = None,
        timestamp: datetime | None = None,
    ) -> str:
        """Generate ADT^A08 (Update patient information) message."""
        timestamp = timestamp or datetime.now()
        message_control_id = self._generate_message_control_id()

        segments = [
            build_msh_segment(
                message_type="ADT",
                trigger_event="A08",
                message_control_id=message_control_id,
                timestamp=timestamp,
                sending_application=self.sending_application,
                sending_facility=self.sending_facility,
                receiving_application=self.receiving_application,
                receiving_facility=self.receiving_facility,
            ),
            build_evn_segment(event_type="A08", event_timestamp=timestamp),
            build_pid_segment(patient),
            build_pv1_segment(encounter),
        ]

        if diagnoses:
            for idx, diagnosis in enumerate(diagnoses, start=1):
                diag_type = diagnosis.type.value if hasattr(diagnosis.type, "value") else str(diagnosis.type)
                segments.append(build_dg1_segment(
                    diagnosis_code=diagnosis.code,
                    diagnosis_text=diagnosis.description,
                    set_id=idx,
                    diagnosis_type="F" if diag_type == "final" else "W",
                ))

        return self._build_message(segments)


__all__ = ["HL7v2Generator"]

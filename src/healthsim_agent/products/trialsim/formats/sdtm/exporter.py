"""SDTM Exporter.

Ported from: healthsim-workspace/packages/trialsim/src/trialsim/formats/sdtm/exporter.py
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from healthsim_agent.products.trialsim.core.models import (
    AdverseEvent,
    AECausality,
    AEOutcome,
    AESeverity,
    Exposure,
    Subject,
    Visit,
    VisitType,
)
from healthsim_agent.products.trialsim.formats.sdtm.domains import SDTMDomain

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Export file formats."""
    CSV = "csv"
    JSON = "json"
    XPT = "xpt"


@dataclass
class ExportConfig:
    """Configuration for SDTM export."""
    study_id: str = "STUDY01"
    sponsor: str = "SPONSOR"
    include_empty: bool = False
    date_format: str = "ISO8601"
    null_value: str = ""
    domains: list[SDTMDomain] | None = None


@dataclass
class ExportResult:
    """Result of SDTM export operation."""
    success: bool
    domains_exported: list[SDTMDomain] = field(default_factory=list)
    record_counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    files_created: list[str] = field(default_factory=list)

    def to_summary(self) -> str:
        lines = [
            "SDTM Export Summary", "=" * 40,
            f"Status: {'Success' if self.success else 'Failed'}", "", "Domains:",
        ]
        for domain in self.domains_exported:
            count = self.record_counts.get(domain.value, 0)
            lines.append(f"  {domain.value}: {count} records")
        if self.warnings:
            lines.extend(["", "Warnings:"] + [f"  - {w}" for w in self.warnings[:5]])
        if self.errors:
            lines.extend(["", "Errors:"] + [f"  - {e}" for e in self.errors[:5]])
        return "\n".join(lines)


class SDTMExporter:
    """Export TrialSim data to CDISC SDTM format."""

    def __init__(self, config: ExportConfig | None = None):
        self.config = config or ExportConfig()

    def export(
        self,
        subjects: list[Subject] | None = None,
        visits: list[Visit] | None = None,
        adverse_events: list[AdverseEvent] | None = None,
        exposures: list[Exposure] | None = None,
        output_dir: str | Path | None = None,
        format: ExportFormat = ExportFormat.CSV,
    ) -> ExportResult:
        """Export data to SDTM format."""
        result = ExportResult(success=True)
        output_path = Path(output_dir) if output_dir else None
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)

        domains = self.config.domains or [SDTMDomain.DM, SDTMDomain.AE, SDTMDomain.EX, SDTMDomain.SV]

        for domain in domains:
            try:
                records = []
                if domain == SDTMDomain.DM and subjects:
                    records = self._convert_dm(subjects)
                elif domain == SDTMDomain.AE and adverse_events:
                    records = self._convert_ae(adverse_events, subjects)
                elif domain == SDTMDomain.EX and exposures:
                    records = self._convert_ex(exposures, subjects)
                elif domain == SDTMDomain.SV and visits:
                    records = self._convert_sv(visits, subjects)

                if records:
                    filepath = self._write_domain(domain, records, output_path, format)
                    result.domains_exported.append(domain)
                    result.record_counts[domain.value] = len(records)
                    if filepath:
                        result.files_created.append(str(filepath))
            except Exception as e:
                result.errors.append(f"{domain.value}: {str(e)}")
                result.success = False
                logger.exception(f"Error exporting {domain.value}")

        return result

    def _convert_dm(self, subjects: list[Subject]) -> list[dict[str, Any]]:
        """Convert subjects to DM domain records."""
        records = []
        for subj in subjects:
            ref_start = subj.screening_date or subj.randomization_date
            arm_code = subj.arm.value.upper() if subj.arm else ""
            arm_desc = subj.arm.value.replace("_", " ").title() if subj.arm else ""

            records.append({
                "STUDYID": self.config.study_id,
                "DOMAIN": "DM",
                "USUBJID": f"{self.config.study_id}-{subj.site_id}-{subj.subject_id}",
                "SUBJID": subj.subject_id,
                "SITEID": subj.site_id,
                "RFSTDTC": self._format_date(ref_start),
                "AGE": subj.age,
                "AGEU": "YEARS",
                "SEX": self._map_sex(subj.sex),
                "RACE": subj.race or "",
                "ETHNIC": subj.ethnicity or "",
                "ARMCD": arm_code,
                "ARM": arm_desc,
                "COUNTRY": "USA",
            })
        return records

    def _convert_ae(self, adverse_events: list[AdverseEvent], subjects: list[Subject] | None = None) -> list[dict[str, Any]]:
        """Convert adverse events to AE domain records."""
        subj_lookup = {s.subject_id: s for s in (subjects or [])}
        records = []
        seq_by_subj: dict[str, int] = {}

        for ae in adverse_events:
            subj = subj_lookup.get(ae.subject_id)
            ref_date = (subj.randomization_date or subj.screening_date) if subj else None
            seq = seq_by_subj.get(ae.subject_id, 0) + 1
            seq_by_subj[ae.subject_id] = seq
            site_id = subj.site_id if subj else "SITE01"

            records.append({
                "STUDYID": self.config.study_id,
                "DOMAIN": "AE",
                "USUBJID": f"{self.config.study_id}-{site_id}-{ae.subject_id}",
                "AESEQ": seq,
                "AESPID": ae.ae_id,
                "AETERM": ae.ae_term,
                "AEDECOD": ae.ae_term,
                "AEBODSYS": ae.system_organ_class or "",
                "AESEV": self._map_severity(ae.severity),
                "AESER": "Y" if ae.is_serious else "N",
                "AEREL": self._map_causality(ae.causality),
                "AEOUT": self._map_outcome(ae.outcome),
                "AESTDTC": self._format_date(ae.onset_date),
                "AEENDTC": self._format_date(ae.resolution_date),
                "AESTDY": self._calc_study_day(ae.onset_date, ref_date),
            })
        return records

    def _convert_ex(self, exposures: list[Exposure], subjects: list[Subject] | None = None) -> list[dict[str, Any]]:
        """Convert exposures to EX domain records."""
        subj_lookup = {s.subject_id: s for s in (subjects or [])}
        records = []
        seq_by_subj: dict[str, int] = {}

        for exp in exposures:
            subj = subj_lookup.get(exp.subject_id)
            ref_date = (subj.randomization_date or subj.screening_date) if subj else None
            seq = seq_by_subj.get(exp.subject_id, 0) + 1
            seq_by_subj[exp.subject_id] = seq
            site_id = subj.site_id if subj else "SITE01"

            records.append({
                "STUDYID": self.config.study_id,
                "DOMAIN": "EX",
                "USUBJID": f"{self.config.study_id}-{site_id}-{exp.subject_id}",
                "EXSEQ": seq,
                "EXSPID": exp.exposure_id,
                "EXTRT": exp.drug_name,
                "EXDOSE": exp.dose,
                "EXDOSU": exp.dose_unit.upper(),
                "EXROUTE": self._map_route(exp.route),
                "EXSTDTC": self._format_date(exp.start_date),
                "EXENDTC": self._format_date(exp.end_date),
                "EXSTDY": self._calc_study_day(exp.start_date, ref_date),
            })
        return records

    def _convert_sv(self, visits: list[Visit], subjects: list[Subject] | None = None) -> list[dict[str, Any]]:
        """Convert visits to SV domain records."""
        subj_lookup = {s.subject_id: s for s in (subjects or [])}
        records = []

        for visit in visits:
            subj = subj_lookup.get(visit.subject_id)
            ref_date = (subj.randomization_date or subj.screening_date) if subj else None
            site_id = visit.site_id or (subj.site_id if subj else "SITE01")
            visit_date = visit.actual_date or visit.planned_date

            records.append({
                "STUDYID": self.config.study_id,
                "DOMAIN": "SV",
                "USUBJID": f"{self.config.study_id}-{site_id}-{visit.subject_id}",
                "VISITNUM": visit.visit_number,
                "VISIT": visit.visit_name,
                "EPOCH": self._map_epoch(visit.visit_type),
                "SVSTDTC": self._format_date(visit_date),
                "SVENDTC": self._format_date(visit_date),
                "SVSTDY": self._calc_study_day(visit_date, ref_date),
            })
        return records

    def _write_domain(self, domain: SDTMDomain, records: list[dict], output_path: Path | None, format: ExportFormat) -> Path | None:
        if not output_path or not records:
            return None
        filepath = output_path / f"{domain.value.lower()}.{format.value}"
        if format == ExportFormat.CSV:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
                writer.writeheader()
                writer.writerows(records)
        elif format == ExportFormat.JSON:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, default=str)
        return filepath

    def _format_date(self, d: date | datetime | None) -> str:
        if d is None:
            return ""
        if isinstance(d, datetime):
            return d.strftime("%Y-%m-%dT%H:%M:%S")
        return d.isoformat()

    def _calc_study_day(self, event_date: date | None, ref_date: date | None) -> int | str:
        if not event_date or not ref_date:
            return ""
        delta = (event_date - ref_date).days
        return delta + 1 if delta >= 0 else delta

    def _map_sex(self, sex: str) -> str:
        return {"M": "M", "F": "F", "MALE": "M", "FEMALE": "F"}.get(sex.upper(), "U")

    def _map_severity(self, severity: AESeverity) -> str:
        return {
            AESeverity.GRADE_1: "MILD", AESeverity.GRADE_2: "MODERATE",
            AESeverity.GRADE_3: "SEVERE", AESeverity.GRADE_4: "LIFE THREATENING",
            AESeverity.GRADE_5: "FATAL",
        }.get(severity, "MODERATE")

    def _map_causality(self, causality: AECausality) -> str:
        return {
            AECausality.NOT_RELATED: "NOT RELATED", AECausality.UNLIKELY: "UNLIKELY",
            AECausality.POSSIBLY: "POSSIBLE", AECausality.PROBABLY: "PROBABLE",
            AECausality.DEFINITELY: "DEFINITE",
        }.get(causality, "POSSIBLE")

    def _map_outcome(self, outcome: AEOutcome) -> str:
        return {
            AEOutcome.RECOVERED: "RECOVERED/RESOLVED", AEOutcome.RECOVERING: "RECOVERING/RESOLVING",
            AEOutcome.NOT_RECOVERED: "NOT RECOVERED/NOT RESOLVED",
            AEOutcome.RECOVERED_WITH_SEQUELAE: "RECOVERED/RESOLVED WITH SEQUELAE",
            AEOutcome.FATAL: "FATAL", AEOutcome.UNKNOWN: "UNKNOWN",
        }.get(outcome, "UNKNOWN")

    def _map_route(self, route: str) -> str:
        return {"oral": "ORAL", "iv": "INTRAVENOUS", "sc": "SUBCUTANEOUS", "im": "INTRAMUSCULAR"}.get(route.lower(), route.upper())

    def _map_epoch(self, visit_type: VisitType) -> str:
        return {
            VisitType.SCREENING: "SCREENING", VisitType.BASELINE: "BASELINE",
            VisitType.RANDOMIZATION: "TREATMENT", VisitType.SCHEDULED: "TREATMENT",
            VisitType.FOLLOW_UP: "FOLLOW-UP", VisitType.END_OF_STUDY: "END OF STUDY",
        }.get(visit_type, "TREATMENT")


def export_to_sdtm(
    subjects: list[Subject] | None = None,
    visits: list[Visit] | None = None,
    adverse_events: list[AdverseEvent] | None = None,
    exposures: list[Exposure] | None = None,
    output_dir: str | Path | None = None,
    format: ExportFormat = ExportFormat.CSV,
    study_id: str = "STUDY01",
) -> ExportResult:
    """Export TrialSim data to SDTM format."""
    return SDTMExporter(ExportConfig(study_id=study_id)).export(
        subjects=subjects, visits=visits, adverse_events=adverse_events,
        exposures=exposures, output_dir=output_dir, format=format,
    )


__all__ = ["SDTMExporter", "ExportConfig", "ExportResult", "ExportFormat", "export_to_sdtm"]

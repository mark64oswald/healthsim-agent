"""ADaM Exporter.

Exports TrialSim data to CDISC ADaM (Analysis Data Model) format.
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
)
from healthsim_agent.products.trialsim.formats.adam.datasets import ADAMDataset

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Export file formats."""
    CSV = "csv"
    JSON = "json"


@dataclass
class ADAMExportConfig:
    """Configuration for ADaM export."""
    study_id: str = "STUDY01"
    sponsor: str = "SPONSOR"
    include_empty: bool = False
    date_format: str = "ISO8601"
    null_value: str = ""
    datasets: list[ADAMDataset] | None = None


@dataclass
class ADAMExportResult:
    """Result of ADaM export operation."""
    success: bool
    datasets_exported: list[ADAMDataset] = field(default_factory=list)
    record_counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    files_created: list[str] = field(default_factory=list)
    data: dict[str, list[dict]] = field(default_factory=dict)

    def to_summary(self) -> str:
        lines = [
            "ADaM Export Summary", "=" * 40,
            f"Status: {'Success' if self.success else 'Failed'}", "", "Datasets:",
        ]
        for ds in self.datasets_exported:
            count = self.record_counts.get(ds.value, 0)
            lines.append(f"  {ds.value}: {count} records")
        if self.warnings:
            lines.extend(["", "Warnings:"] + [f"  - {w}" for w in self.warnings[:5]])
        if self.errors:
            lines.extend(["", "Errors:"] + [f"  - {e}" for e in self.errors[:5]])
        return "\n".join(lines)


class ADAMExporter:
    """Export TrialSim data to CDISC ADaM format."""

    def __init__(self, config: ADAMExportConfig | None = None):
        self.config = config or ADAMExportConfig()

    def export(
        self,
        subjects: list[Subject] | None = None,
        adverse_events: list[AdverseEvent] | None = None,
        exposures: list[Exposure] | None = None,
        output_dir: str | Path | None = None,
        format: ExportFormat = ExportFormat.CSV,
    ) -> ADAMExportResult:
        """Export data to ADaM format."""
        result = ADAMExportResult(success=True)
        output_path = Path(output_dir) if output_dir else None
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)

        datasets = self.config.datasets or [ADAMDataset.ADSL, ADAMDataset.ADAE, ADAMDataset.ADEX]

        for ds in datasets:
            try:
                records = []
                if ds == ADAMDataset.ADSL and subjects:
                    records = self._convert_adsl(subjects, exposures)
                elif ds == ADAMDataset.ADAE and adverse_events:
                    records = self._convert_adae(adverse_events, subjects)
                elif ds == ADAMDataset.ADEX and exposures:
                    records = self._convert_adex(exposures, subjects)

                if records:
                    filepath = self._write_dataset(ds, records, output_path, format)
                    result.datasets_exported.append(ds)
                    result.record_counts[ds.value] = len(records)
                    result.data[ds.value] = records
                    if filepath:
                        result.files_created.append(str(filepath))
            except Exception as e:
                result.errors.append(f"{ds.value}: {str(e)}")
                result.success = False
                logger.exception(f"Error exporting {ds.value}")

        return result

    def _convert_adsl(self, subjects: list[Subject], exposures: list[Exposure] | None = None) -> list[dict[str, Any]]:
        """Convert subjects to ADSL (Subject-Level Analysis Dataset)."""
        from healthsim_agent.products.trialsim.core.models import SubjectStatus
        
        # Build exposure lookup for treatment dates
        exp_by_subj: dict[str, list[Exposure]] = {}
        for exp in (exposures or []):
            exp_by_subj.setdefault(exp.subject_id, []).append(exp)

        records = []
        for subj in subjects:
            subj_exp = exp_by_subj.get(subj.subject_id, [])
            trtsdt = min((e.start_date for e in subj_exp), default=None)
            trtedt = max((e.end_date for e in subj_exp if e.end_date), default=None)
            
            arm_code = subj.arm.value.upper() if subj.arm else ""
            arm_desc = subj.arm.value.replace("_", " ").title() if subj.arm else ""
            
            # Determine EOS status from subject status
            eos_status = "ONGOING"
            eos_date = None
            if hasattr(subj, 'status'):
                if subj.status == SubjectStatus.COMPLETED:
                    eos_status = "COMPLETED"
                    eos_date = trtedt  # Use last treatment date
                elif subj.status == SubjectStatus.WITHDRAWN:
                    eos_status = "DISCONTINUED"
                elif subj.status == SubjectStatus.LOST_TO_FOLLOWUP:
                    eos_status = "LOST TO FOLLOW-UP"

            records.append({
                "STUDYID": self.config.study_id,
                "USUBJID": f"{self.config.study_id}-{subj.site_id}-{subj.subject_id}",
                "SUBJID": subj.subject_id,
                "SITEID": subj.site_id,
                "AGE": subj.age,
                "AGEU": "YEARS",
                "AGEGR1": self._get_age_group(subj.age),
                "SEX": self._map_sex(subj.sex),
                "RACE": subj.race or "",
                "ETHNIC": subj.ethnicity or "",
                "COUNTRY": "USA",
                "TRT01P": arm_desc,
                "TRT01A": arm_desc,
                "TRTSDT": self._format_date(trtsdt),
                "TRTEDT": self._format_date(trtedt),
                "SAFFL": "Y" if subj.randomization_date else "N",
                "ITTFL": "Y" if subj.randomization_date else "N",
                "PPROTFL": "Y",  # Simplified - assume per-protocol
                "RANDFL": "Y" if subj.randomization_date else "N",
                "RANDDT": self._format_date(subj.randomization_date),
                "DTHFL": "N",  # Not tracked in current model
                "DTHDT": "",
                "EOSDT": self._format_date(eos_date),
                "EOSSTT": eos_status,
            })
        return records

    def _convert_adae(self, adverse_events: list[AdverseEvent], subjects: list[Subject] | None = None) -> list[dict[str, Any]]:
        """Convert adverse events to ADAE (Adverse Events Analysis Dataset)."""
        subj_lookup = {s.subject_id: s for s in (subjects or [])}
        records = []
        seq_by_subj: dict[str, int] = {}
        first_ae_by_subj: dict[str, bool] = {}
        first_soc_by_subj_soc: dict[tuple, bool] = {}
        first_pt_by_subj_pt: dict[tuple, bool] = {}

        for ae in adverse_events:
            subj = subj_lookup.get(ae.subject_id)
            ref_date = (subj.randomization_date or subj.screening_date) if subj else None
            seq = seq_by_subj.get(ae.subject_id, 0) + 1
            seq_by_subj[ae.subject_id] = seq
            site_id = subj.site_id if subj else "SITE01"
            arm_desc = subj.arm.value.replace("_", " ").title() if subj and subj.arm else ""

            # First occurrence flags
            aoccfl = "Y" if ae.subject_id not in first_ae_by_subj else "N"
            first_ae_by_subj[ae.subject_id] = True
            
            soc_key = (ae.subject_id, ae.system_organ_class)
            aoccsfl = "Y" if soc_key not in first_soc_by_subj_soc else "N"
            first_soc_by_subj_soc[soc_key] = True
            
            pt_key = (ae.subject_id, ae.ae_term)
            aoccpfl = "Y" if pt_key not in first_pt_by_subj_pt else "N"
            first_pt_by_subj_pt[pt_key] = True

            # Calculate duration
            adurn = None
            if ae.onset_date and ae.resolution_date:
                adurn = (ae.resolution_date - ae.onset_date).days

            records.append({
                "STUDYID": self.config.study_id,
                "USUBJID": f"{self.config.study_id}-{site_id}-{ae.subject_id}",
                "SUBJID": ae.subject_id,
                "SITEID": site_id,
                "TRTA": arm_desc,
                "TRTAN": 1 if arm_desc else None,
                "AGE": subj.age if subj else None,
                "SEX": self._map_sex(subj.sex) if subj else "",
                "SAFFL": "Y",
                "AESEQ": seq,
                "AESPID": ae.ae_id,
                "AETERM": ae.ae_term,
                "AEDECOD": ae.ae_term,
                "AEBODSYS": ae.system_organ_class or "",
                "AESEV": self._map_severity(ae.severity),
                "AESER": "Y" if ae.is_serious else "N",
                "AEREL": self._map_causality(ae.causality),
                "AEOUT": self._map_outcome(ae.outcome),
                "AESTDTC": self._format_datetime(ae.onset_date),
                "AEENDTC": self._format_datetime(ae.resolution_date),
                "ASTDT": self._format_date(ae.onset_date),
                "AENDT": self._format_date(ae.resolution_date),
                "ASTDY": self._calc_study_day(ae.onset_date, ref_date),
                "AENDY": self._calc_study_day(ae.resolution_date, ref_date),
                "ADURN": adurn,
                "ADURU": "DAYS" if adurn else "",
                "AOCCFL": aoccfl,
                "AOCCSFL": aoccsfl,
                "AOCCPFL": aoccpfl,
                "TRTEMFL": "Y",  # Treatment-emergent
            })
        return records

    def _convert_adex(self, exposures: list[Exposure], subjects: list[Subject] | None = None) -> list[dict[str, Any]]:
        """Convert exposures to ADEX (Exposure Analysis Dataset)."""
        subj_lookup = {s.subject_id: s for s in (subjects or [])}
        records = []
        seq_by_subj: dict[str, int] = {}

        for exp in exposures:
            subj = subj_lookup.get(exp.subject_id)
            ref_date = (subj.randomization_date or subj.screening_date) if subj else None
            seq = seq_by_subj.get(exp.subject_id, 0) + 1
            seq_by_subj[exp.subject_id] = seq
            site_id = subj.site_id if subj else "SITE01"
            arm_desc = subj.arm.value.replace("_", " ").title() if subj and subj.arm else ""

            records.append({
                "STUDYID": self.config.study_id,
                "USUBJID": f"{self.config.study_id}-{site_id}-{exp.subject_id}",
                "SUBJID": exp.subject_id,
                "SITEID": site_id,
                "TRTA": arm_desc,
                "TRTAN": 1 if arm_desc else None,
                "SAFFL": "Y",
                "EXSEQ": seq,
                "EXTRT": exp.drug_name,
                "EXDOSE": exp.dose,
                "EXDOSU": exp.dose_unit.upper(),
                "EXROUTE": self._map_route(exp.route),
                "EXSTDTC": self._format_datetime(exp.start_date),
                "EXENDTC": self._format_datetime(exp.end_date),
                "ASTDT": self._format_date(exp.start_date),
                "AENDT": self._format_date(exp.end_date),
                "ASTDY": self._calc_study_day(exp.start_date, ref_date),
                "AENDY": self._calc_study_day(exp.end_date, ref_date),
                "AVAL": exp.dose,
                "AVALC": f"{exp.dose} {exp.dose_unit}",
                "PARAM": f"{exp.drug_name} Dose",
                "PARAMCD": "DOSE",
                "PARAMN": 1,
            })
        return records

    def _write_dataset(self, ds: ADAMDataset, records: list[dict], output_path: Path | None, format: ExportFormat) -> Path | None:
        if not output_path or not records:
            return None
        filepath = output_path / f"{ds.value.lower()}.{format.value}"
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
            return d.strftime("%Y-%m-%d")
        return d.isoformat()

    def _format_datetime(self, d: date | datetime | None) -> str:
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

    def _get_age_group(self, age: int) -> str:
        if age < 18:
            return "<18"
        elif age < 65:
            return "18-64"
        else:
            return ">=65"

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


def export_to_adam(
    subjects: list[Subject] | None = None,
    adverse_events: list[AdverseEvent] | None = None,
    exposures: list[Exposure] | None = None,
    output_dir: str | Path | None = None,
    format: ExportFormat = ExportFormat.CSV,
    study_id: str = "STUDY01",
) -> ADAMExportResult:
    """Export TrialSim data to ADaM format."""
    return ADAMExporter(ADAMExportConfig(study_id=study_id)).export(
        subjects=subjects, adverse_events=adverse_events,
        exposures=exposures, output_dir=output_dir, format=format,
    )


__all__ = ["ADAMExporter", "ADAMExportConfig", "ADAMExportResult", "ExportFormat", "export_to_adam"]

"""Workspace management for HealthSim Agent.

Provides file-based workspace organization for managing
related cohorts, profiles, and journeys together.

A workspace groups related generation artifacts:
- Multiple cohorts that belong to a project
- Shared profiles used across cohorts
- Journey definitions for the workspace
- Configuration and metadata

Ported from: healthsim-workspace/packages/core/src/healthsim/state/workspace.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import json


# Default workspace storage location
WORKSPACES_DIR = Path("data/workspaces")


@dataclass
class WorkspaceMetadata:
    """Metadata about a workspace."""
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    cohort_ids: list[str] = field(default_factory=list)
    profile_ids: list[str] = field(default_factory=list)
    journey_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class Workspace:
    """Manages a file-based workspace for related HealthSim artifacts.
    
    A workspace is a directory containing:
        workspace.json - Metadata and configuration
        cohorts/ - Exported cohort data (optional)
        profiles/ - Profile definitions (optional)
        journeys/ - Journey definitions (optional)
        outputs/ - Generated outputs (optional)
    
    Usage:
        # Create or load workspace
        ws = Workspace("my-project")
        
        # Add cohorts to workspace
        ws.add_cohort("cohort-123")
        
        # Save workspace
        ws.save()
        
        # List all workspaces
        for ws_meta in Workspace.list_all():
            print(f"{ws_meta.name}: {len(ws_meta.cohort_ids)} cohorts")
    """
    
    def __init__(
        self,
        name: str,
        base_dir: str | Path | None = None,
        auto_create: bool = True,
    ):
        """Initialize or load a workspace.
        
        Args:
            name: Workspace name (used as directory name)
            base_dir: Base directory for workspaces
            auto_create: Create workspace if it doesn't exist
        """
        self._base_dir = Path(base_dir) if base_dir else WORKSPACES_DIR
        self._workspace_dir = self._base_dir / name
        self._metadata_file = self._workspace_dir / "workspace.json"
        
        if self._workspace_dir.exists():
            self._load()
        elif auto_create:
            self._create(name)
        else:
            raise FileNotFoundError(f"Workspace not found: {name}")
    
    def _create(self, name: str) -> None:
        """Create a new workspace."""
        self._workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self._workspace_dir / "cohorts").mkdir(exist_ok=True)
        (self._workspace_dir / "profiles").mkdir(exist_ok=True)
        (self._workspace_dir / "journeys").mkdir(exist_ok=True)
        (self._workspace_dir / "outputs").mkdir(exist_ok=True)
        
        # Initialize metadata
        now = datetime.now()
        self._metadata = WorkspaceMetadata(
            id=f"ws-{name}",
            name=name,
            description=None,
            created_at=now,
            updated_at=now,
        )
        
        self.save()
    
    def _load(self) -> None:
        """Load workspace from disk."""
        if not self._metadata_file.exists():
            raise ValueError(f"Invalid workspace: missing workspace.json")
        
        with open(self._metadata_file) as f:
            data = json.load(f)
        
        self._metadata = WorkspaceMetadata(
            id=data.get("id", f"ws-{self._workspace_dir.name}"),
            name=data.get("name", self._workspace_dir.name),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            cohort_ids=data.get("cohort_ids", []),
            profile_ids=data.get("profile_ids", []),
            journey_ids=data.get("journey_ids", []),
            tags=data.get("tags", []),
            config=data.get("config", {}),
        )
    
    def save(self) -> None:
        """Save workspace to disk."""
        self._metadata.updated_at = datetime.now()
        
        data = {
            "id": self._metadata.id,
            "name": self._metadata.name,
            "description": self._metadata.description,
            "created_at": self._metadata.created_at.isoformat(),
            "updated_at": self._metadata.updated_at.isoformat(),
            "cohort_ids": self._metadata.cohort_ids,
            "profile_ids": self._metadata.profile_ids,
            "journey_ids": self._metadata.journey_ids,
            "tags": self._metadata.tags,
            "config": self._metadata.config,
        }
        
        with open(self._metadata_file, "w") as f:
            json.dump(data, f, indent=2)
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def name(self) -> str:
        """Get workspace name."""
        return self._metadata.name
    
    @property
    def path(self) -> Path:
        """Get workspace directory path."""
        return self._workspace_dir
    
    @property
    def metadata(self) -> WorkspaceMetadata:
        """Get workspace metadata."""
        return self._metadata
    
    @property
    def cohorts_dir(self) -> Path:
        """Get cohorts directory."""
        return self._workspace_dir / "cohorts"
    
    @property
    def profiles_dir(self) -> Path:
        """Get profiles directory."""
        return self._workspace_dir / "profiles"
    
    @property
    def journeys_dir(self) -> Path:
        """Get journeys directory."""
        return self._workspace_dir / "journeys"
    
    @property
    def outputs_dir(self) -> Path:
        """Get outputs directory."""
        return self._workspace_dir / "outputs"
    
    # =========================================================================
    # Cohort Management
    # =========================================================================
    
    def add_cohort(self, cohort_id: str) -> None:
        """Add a cohort to the workspace.
        
        Args:
            cohort_id: Cohort ID to add
        """
        if cohort_id not in self._metadata.cohort_ids:
            self._metadata.cohort_ids.append(cohort_id)
            self.save()
    
    def remove_cohort(self, cohort_id: str) -> bool:
        """Remove a cohort from the workspace.
        
        Args:
            cohort_id: Cohort ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if cohort_id in self._metadata.cohort_ids:
            self._metadata.cohort_ids.remove(cohort_id)
            self.save()
            return True
        return False
    
    def list_cohorts(self) -> list[str]:
        """Get list of cohort IDs in workspace."""
        return self._metadata.cohort_ids.copy()
    
    # =========================================================================
    # Profile Management
    # =========================================================================
    
    def add_profile(self, profile_id: str) -> None:
        """Add a profile to the workspace.
        
        Args:
            profile_id: Profile ID to add
        """
        if profile_id not in self._metadata.profile_ids:
            self._metadata.profile_ids.append(profile_id)
            self.save()
    
    def remove_profile(self, profile_id: str) -> bool:
        """Remove a profile from the workspace.
        
        Args:
            profile_id: Profile ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if profile_id in self._metadata.profile_ids:
            self._metadata.profile_ids.remove(profile_id)
            self.save()
            return True
        return False
    
    def list_profiles(self) -> list[str]:
        """Get list of profile IDs in workspace."""
        return self._metadata.profile_ids.copy()
    
    # =========================================================================
    # Journey Management
    # =========================================================================
    
    def add_journey(self, journey_id: str) -> None:
        """Add a journey to the workspace.
        
        Args:
            journey_id: Journey ID to add
        """
        if journey_id not in self._metadata.journey_ids:
            self._metadata.journey_ids.append(journey_id)
            self.save()
    
    def remove_journey(self, journey_id: str) -> bool:
        """Remove a journey from the workspace.
        
        Args:
            journey_id: Journey ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if journey_id in self._metadata.journey_ids:
            self._metadata.journey_ids.remove(journey_id)
            self.save()
            return True
        return False
    
    def list_journeys(self) -> list[str]:
        """Get list of journey IDs in workspace."""
        return self._metadata.journey_ids.copy()
    
    # =========================================================================
    # Configuration
    # =========================================================================
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value (must be JSON-serializable)
        """
        self._metadata.config[key] = value
        self.save()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        return self._metadata.config.get(key, default)
    
    def update_description(self, description: str | None) -> None:
        """Update workspace description.
        
        Args:
            description: New description
        """
        self._metadata.description = description
        self.save()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the workspace.
        
        Args:
            tag: Tag to add
        """
        tag = tag.lower().strip()
        if tag and tag not in self._metadata.tags:
            self._metadata.tags.append(tag)
            self.save()
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the workspace.
        
        Args:
            tag: Tag to remove
            
        Returns:
            True if removed, False if not found
        """
        tag = tag.lower().strip()
        if tag in self._metadata.tags:
            self._metadata.tags.remove(tag)
            self.save()
            return True
        return False
    
    # =========================================================================
    # Class Methods
    # =========================================================================
    
    @classmethod
    def list_all(
        cls,
        base_dir: str | Path | None = None,
    ) -> list[WorkspaceMetadata]:
        """List all workspaces.
        
        Args:
            base_dir: Base directory for workspaces
            
        Returns:
            List of WorkspaceMetadata objects
        """
        base = Path(base_dir) if base_dir else WORKSPACES_DIR
        
        if not base.exists():
            return []
        
        workspaces = []
        for ws_dir in base.iterdir():
            if ws_dir.is_dir():
                metadata_file = ws_dir / "workspace.json"
                if metadata_file.exists():
                    try:
                        ws = cls(ws_dir.name, base_dir=base, auto_create=False)
                        workspaces.append(ws.metadata)
                    except (ValueError, json.JSONDecodeError):
                        continue
        
        return sorted(workspaces, key=lambda x: x.updated_at, reverse=True)
    
    @classmethod
    def exists(
        cls,
        name: str,
        base_dir: str | Path | None = None,
    ) -> bool:
        """Check if a workspace exists.
        
        Args:
            name: Workspace name
            base_dir: Base directory for workspaces
            
        Returns:
            True if workspace exists
        """
        base = Path(base_dir) if base_dir else WORKSPACES_DIR
        ws_dir = base / name
        return (ws_dir / "workspace.json").exists()
    
    @classmethod
    def delete(
        cls,
        name: str,
        base_dir: str | Path | None = None,
    ) -> bool:
        """Delete a workspace.
        
        Args:
            name: Workspace name
            base_dir: Base directory for workspaces
            
        Returns:
            True if deleted, False if not found
        """
        import shutil
        
        base = Path(base_dir) if base_dir else WORKSPACES_DIR
        ws_dir = base / name
        
        if ws_dir.exists():
            shutil.rmtree(ws_dir)
            return True
        return False

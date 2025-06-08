"""
Data versioning module for tracking data processing history.

Provides version control for processed datasets, enabling
reproducibility and tracking of data transformations.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from ..utils.logger import get_logger
from ..utils.file_handler import FileHandler


logger = get_logger(__name__)


class DataVersionManager:
    """
    Manages versioning of processed datasets.
    
    Features:
    - Automatic version numbering
    - Metadata tracking
    - Data lineage
    - Checksum verification
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the version manager.
        
        Args:
            base_path: Base path for version storage
        """
        self.base_path = base_path or Path("data/versions")
        self.metadata_file = self.base_path / "version_metadata.json"
        self.versions = self._load_version_metadata()
        
        # Ensure version directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _load_version_metadata(self) -> Dict[str, Any]:
        """Load existing version metadata."""
        if self.metadata_file.exists():
            try:
                return FileHandler.read_json(self.metadata_file)
            except Exception as e:
                logger.warning(f"Error loading version metadata: {e}")
                return {"versions": {}, "current": None}
        return {"versions": {}, "current": None}
    
    def _save_version_metadata(self):
        """Save version metadata to file."""
        FileHandler.write_json(self.versions, self.metadata_file)
        
    def create_version(
        self,
        data: pd.DataFrame,
        source_files: List[str],
        processing_params: Dict[str, Any],
        description: str = ""
    ) -> str:
        """
        Create a new version of processed data.
        
        Args:
            data: Processed DataFrame
            source_files: List of source file paths
            processing_params: Parameters used in processing
            description: Optional version description
            
        Returns:
            Version identifier
        """
        # Generate version ID
        version_id = self._generate_version_id()
        
        # Calculate data checksum
        checksum = self._calculate_checksum(data)
        
        # Create version directory
        version_dir = self.base_path / version_id
        version_dir.mkdir(exist_ok=True)
        
        # Save data
        data_path = version_dir / "data.csv"
        FileHandler.write_csv(data, data_path)
        
        # Create metadata
        metadata = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "source_files": source_files,
            "processing_params": processing_params,
            "data_info": {
                "rows": len(data),
                "columns": list(data.columns),
                "date_range": f"{data['Date'].min()} to {data['Date'].max()}" if 'Date' in data.columns else None,
                "checksum": checksum
            },
            "parent_version": self.versions.get("current")
        }
        
        # Save version metadata
        metadata_path = version_dir / "metadata.json"
        FileHandler.write_json(metadata, metadata_path)
        
        # Update global metadata
        self.versions["versions"][version_id] = metadata
        self.versions["current"] = version_id
        self._save_version_metadata()
        
        logger.info(f"Created data version: {version_id}")
        
        return version_id
    
    def _generate_version_id(self) -> str:
        """Generate unique version identifier."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get next version number
        version_numbers = []
        for vid in self.versions.get("versions", {}).keys():
            if vid.startswith("v"):
                try:
                    num = int(vid.split("_")[0][1:])
                    version_numbers.append(num)
                except ValueError:
                    pass
                    
        next_number = max(version_numbers) + 1 if version_numbers else 1
        
        return f"v{next_number:03d}_{timestamp}"
    
    def _calculate_checksum(self, data: pd.DataFrame) -> str:
        """Calculate checksum for DataFrame."""
        # Convert DataFrame to bytes
        data_bytes = data.to_csv(index=False).encode('utf-8')
        
        # Calculate SHA256 hash
        return hashlib.sha256(data_bytes).hexdigest()
    
    def get_version(self, version_id: str) -> Optional[pd.DataFrame]:
        """
        Load a specific version of data.
        
        Args:
            version_id: Version identifier
            
        Returns:
            DataFrame or None if version not found
        """
        if version_id not in self.versions.get("versions", {}):
            logger.error(f"Version not found: {version_id}")
            return None
            
        data_path = self.base_path / version_id / "data.csv"
        
        if not data_path.exists():
            logger.error(f"Data file not found for version: {version_id}")
            return None
            
        return FileHandler.read_csv(data_path)
    
    def get_current_version(self) -> Optional[pd.DataFrame]:
        """Get the current (latest) version of data."""
        current_id = self.versions.get("current")
        
        if not current_id:
            logger.warning("No current version set")
            return None
            
        return self.get_version(current_id)
    
    def get_version_metadata(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific version."""
        return self.versions.get("versions", {}).get(version_id)
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all available versions."""
        versions_list = []
        
        for version_id, metadata in self.versions.get("versions", {}).items():
            versions_list.append({
                "version_id": version_id,
                "timestamp": metadata.get("timestamp"),
                "description": metadata.get("description", ""),
                "rows": metadata.get("data_info", {}).get("rows", 0),
                "is_current": version_id == self.versions.get("current")
            })
            
        return sorted(versions_list, key=lambda x: x["timestamp"], reverse=True)
    
    def verify_version(self, version_id: str) -> bool:
        """
        Verify integrity of a version using checksum.
        
        Args:
            version_id: Version to verify
            
        Returns:
            True if checksum matches, False otherwise
        """
        metadata = self.get_version_metadata(version_id)
        
        if not metadata:
            logger.error(f"No metadata for version: {version_id}")
            return False
            
        stored_checksum = metadata.get("data_info", {}).get("checksum")
        
        if not stored_checksum:
            logger.warning(f"No checksum stored for version: {version_id}")
            return False
            
        # Load data and calculate checksum
        data = self.get_version(version_id)
        
        if data is None:
            return False
            
        calculated_checksum = self._calculate_checksum(data)
        
        if calculated_checksum != stored_checksum:
            logger.error(f"Checksum mismatch for version: {version_id}")
            return False
            
        logger.info(f"Version {version_id} verified successfully")
        return True
    
    def compare_versions(
        self,
        version1_id: str,
        version2_id: str
    ) -> Dict[str, Any]:
        """
        Compare two versions of data.
        
        Args:
            version1_id: First version ID
            version2_id: Second version ID
            
        Returns:
            Dictionary with comparison results
        """
        v1_meta = self.get_version_metadata(version1_id)
        v2_meta = self.get_version_metadata(version2_id)
        
        if not v1_meta or not v2_meta:
            raise ValueError("One or both versions not found")
            
        comparison = {
            "version1": version1_id,
            "version2": version2_id,
            "row_diff": (
                v2_meta["data_info"]["rows"] - v1_meta["data_info"]["rows"]
            ),
            "columns_added": list(
                set(v2_meta["data_info"]["columns"]) - 
                set(v1_meta["data_info"]["columns"])
            ),
            "columns_removed": list(
                set(v1_meta["data_info"]["columns"]) - 
                set(v2_meta["data_info"]["columns"])
            ),
            "timestamp_diff": (
                datetime.fromisoformat(v2_meta["timestamp"]) - 
                datetime.fromisoformat(v1_meta["timestamp"])
            ).total_seconds() / 3600  # Hours
        }
        
        return comparison
    
    def rollback_to_version(self, version_id: str):
        """
        Set a specific version as current.
        
        Args:
            version_id: Version to rollback to
        """
        if version_id not in self.versions.get("versions", {}):
            raise ValueError(f"Version not found: {version_id}")
            
        self.versions["current"] = version_id
        self._save_version_metadata()
        
        logger.info(f"Rolled back to version: {version_id}")
    
    def export_version(
        self,
        version_id: str,
        export_path: Path,
        include_metadata: bool = True
    ):
        """
        Export a version to external location.
        
        Args:
            version_id: Version to export
            export_path: Export destination
            include_metadata: Whether to include metadata
        """
        data = self.get_version(version_id)
        
        if data is None:
            raise ValueError(f"Version not found: {version_id}")
            
        export_path = Path(export_path)
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Export data
        data_file = export_path / f"{version_id}_data.csv"
        FileHandler.write_csv(data, data_file)
        
        # Export metadata if requested
        if include_metadata:
            metadata = self.get_version_metadata(version_id)
            metadata_file = export_path / f"{version_id}_metadata.json"
            FileHandler.write_json(metadata, metadata_file)
            
        logger.info(f"Exported version {version_id} to {export_path}")
    
    def cleanup_old_versions(self, keep_last: int = 5):
        """
        Remove old versions, keeping only the most recent ones.
        
        Args:
            keep_last: Number of versions to keep
        """
        versions_list = self.list_versions()
        
        if len(versions_list) <= keep_last:
            logger.info("No versions to clean up")
            return
            
        # Sort by timestamp and identify versions to remove
        versions_to_remove = versions_list[keep_last:]
        
        for version_info in versions_to_remove:
            version_id = version_info["version_id"]
            
            # Don't remove current version
            if version_info["is_current"]:
                continue
                
            # Remove version directory
            version_dir = self.base_path / version_id
            if version_dir.exists():
                import shutil
                shutil.rmtree(version_dir)
                
            # Remove from metadata
            del self.versions["versions"][version_id]
            
            logger.info(f"Removed old version: {version_id}")
            
        self._save_version_metadata()
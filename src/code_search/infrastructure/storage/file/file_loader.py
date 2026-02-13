"""File loader implementation."""

from typing import List, Optional
from pathlib import Path

from ....domain.interfaces import IFileLoader
from ....domain.models import FileIndex


class FileLoader(IFileLoader):
    """Implementation for loading source code files from filesystem."""

    # Directories to exclude from indexing
    EXCLUDED_DIRS = {
        'venv', 'env', '.venv', '.env',
        'node_modules', 'bower_components',
        '__pycache__', '.git', '.svn', '.hg',
        'bin', 'obj', 'build', 'dist',
        '.vs', '.vscode', '.idea',
        'packages', 'lib', 'libs',
        'vectordb_workspace', 'vector_store'
    }

    def __init__(self, supported_extensions: Optional[List[str]] = None):
        self._supported_extensions = supported_extensions or ['.py', '.cs', '.ts', '.js']

    async def load_files(self, project_directory: str) -> List[FileIndex]:
        """Load all source code files from the specified directory."""
        files = []
        project_path = Path(project_directory)

        for file_path in project_path.rglob('*'):
            # Skip if file is in an excluded directory
            if self._is_in_excluded_dir(file_path, project_path):
                continue
                
            if file_path.is_file() and file_path.suffix in self._supported_extensions:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_index = FileIndex(
                        file_path=str(file_path.relative_to(project_path)),
                        content=content
                    )
                    # Content hash is automatically generated in __post_init__
                    files.append(file_index)
                except (UnicodeDecodeError, PermissionError):
                    continue

        return files

    def _is_in_excluded_dir(self, file_path: Path, project_path: Path) -> bool:
        """Check if file is in an excluded directory."""
        try:
            relative_path = file_path.relative_to(project_path)
            # Check if any part of the path matches excluded directories
            for part in relative_path.parts:
                if part in self.EXCLUDED_DIRS or part.startswith('.'):
                    return True
            return False
        except ValueError:
            return True

    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return self._supported_extensions

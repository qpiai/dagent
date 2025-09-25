"""File editing tools for ACT type agents."""

import os
import logging
from typing import List, Optional
from agno.tools import Toolkit
from .base import BaseAgnoTool

logger = logging.getLogger(__name__)


class FileEditorTools(BaseAgnoTool):
    """File editing toolkit for agents that need to modify files."""

    def __init__(self):
        tools = [
            self.read_file,
            self.write_file,
            self.append_to_file,
            self.create_file,
            self.list_files,
            self.file_exists
        ]
        super().__init__(name="FileEditor", tools=tools)

    def read_file(self, file_path: str) -> str:
        """
        Read the contents of a file.

        Args:
            file_path: Path to the file to read

        Returns:
            File contents as string
        """
        self._log_tool_call("read_file", {"file_path": file_path})

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Successfully read file: {file_path}")
            return content
        except Exception as e:
            return self._handle_error("read_file", e)

    def write_file(self, file_path: str, content: str) -> str:
        """
        Write content to a file, overwriting existing content.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file

        Returns:
            Success message or error
        """
        self._log_tool_call("write_file", {"file_path": file_path, "content_length": len(content)})

        try:
            # Handle relative paths and ensure directory exists
            if os.path.dirname(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            success_msg = f"Successfully wrote {len(content)} characters to {file_path}"
            logger.info(success_msg)
            return success_msg
        except Exception as e:
            return self._handle_error("write_file", e)

    def append_to_file(self, file_path: str, content: str) -> str:
        """
        Append content to the end of a file.

        Args:
            file_path: Path to the file to append to
            content: Content to append

        Returns:
            Success message or error
        """
        self._log_tool_call("append_to_file", {"file_path": file_path, "content_length": len(content)})

        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)

            success_msg = f"Successfully appended {len(content)} characters to {file_path}"
            logger.info(success_msg)
            return success_msg
        except Exception as e:
            return self._handle_error("append_to_file", e)

    def create_file(self, file_path: str, content: str = "") -> str:
        """
        Create a new file with optional initial content.

        Args:
            file_path: Path to the new file
            content: Initial content for the file (optional)

        Returns:
            Success message or error
        """
        self._log_tool_call("create_file", {"file_path": file_path, "content_length": len(content)})

        try:
            if os.path.exists(file_path):
                return f"File {file_path} already exists. Use write_file to overwrite."

            # Handle relative paths and ensure directory exists
            if os.path.dirname(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            success_msg = f"Successfully created file {file_path} with {len(content)} characters"
            logger.info(success_msg)
            return success_msg
        except Exception as e:
            return self._handle_error("create_file", e)

    def list_files(self, directory_path: str = ".", pattern: Optional[str] = None) -> str:
        """
        List files in a directory, optionally filtered by pattern.

        Args:
            directory_path: Directory to list files from (default: current directory)
            pattern: Optional pattern to filter files (e.g., "*.py")

        Returns:
            List of files as string
        """
        self._log_tool_call("list_files", {"directory_path": directory_path, "pattern": pattern})

        try:
            import glob

            if pattern:
                search_path = os.path.join(directory_path, pattern)
                files = glob.glob(search_path)
            else:
                files = [f for f in os.listdir(directory_path)
                        if os.path.isfile(os.path.join(directory_path, f))]

            if files:
                result = f"Files in {directory_path}:\n" + "\n".join(f"- {f}" for f in sorted(files))
            else:
                result = f"No files found in {directory_path}"

            logger.info(f"Listed {len(files)} files in {directory_path}")
            return result
        except Exception as e:
            return self._handle_error("list_files", e)

    def file_exists(self, file_path: str) -> str:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            Boolean result as string
        """
        self._log_tool_call("file_exists", {"file_path": file_path})

        try:
            exists = os.path.exists(file_path) and os.path.isfile(file_path)
            result = f"File {file_path} {'exists' if exists else 'does not exist'}"
            logger.info(result)
            return result
        except Exception as e:
            return self._handle_error("file_exists", e)
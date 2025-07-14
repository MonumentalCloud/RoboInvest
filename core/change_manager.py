"""
Change Manager - Git-based code change management with safety and rollback

Features:
- Automatic git commits for all changes
- Change validation before application
- Rollback functionality with git revert
- Safety checks and user approval workflow
- Integration with change logger
"""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import hashlib
import uuid

from utils.logger import logger
from core.change_logger import change_logger, CodeChange, ChangeStatus, ChangeType


class ChangeManager:
    """Production-grade Git-based change manager"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.git_path = self.repo_path / ".git"
        
        # Validate git repository
        if not self.git_path.exists():
            raise RuntimeError(f"Not a git repository: {self.repo_path}")
        
        # Get current branch
        self.current_branch = self._get_current_branch()
        logger.info(f"ChangeManager initialized for {self.repo_path} on branch {self.current_branch}")
    
    def _run_git_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a git command and return (return_code, stdout, stderr)"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(command)}")
            return -1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Git command failed: {' '.join(command)} - {e}")
            return -1, "", str(e)
    
    def _get_current_branch(self) -> str:
        """Get the current git branch"""
        return_code, stdout, stderr = self._run_git_command(["branch", "--show-current"])
        if return_code == 0:
            return stdout.strip()
        else:
            logger.error(f"Failed to get current branch: {stderr}")
            return "main"  # fallback
    
    def _get_latest_commit_hash(self) -> Optional[str]:
        """Get the latest commit hash"""
        return_code, stdout, stderr = self._run_git_command(["rev-parse", "HEAD"])
        if return_code == 0:
            return stdout.strip()
        else:
            logger.error(f"Failed to get latest commit: {stderr}")
            return None
    
    def _check_git_status(self) -> Dict[str, Any]:
        """Check git status and return information about working directory"""
        return_code, stdout, stderr = self._run_git_command(["status", "--porcelain"])
        
        if return_code != 0:
            return {"error": stderr, "clean": False}
        
        lines = stdout.strip().split('\n') if stdout.strip() else []
        modified_files = []
        untracked_files = []
        
        for line in lines:
            if line:
                status = line[:2]
                filename = line[3:]
                
                if status.startswith('M') or status.startswith('A') or status.startswith('D'):
                    modified_files.append(filename)
                elif status.startswith('??'):
                    untracked_files.append(filename)
        
        return {
            "clean": len(lines) == 0,
            "modified_files": modified_files,
            "untracked_files": untracked_files,
            "total_changes": len(lines)
        }
    
    def validate_change(self, change: CodeChange) -> Tuple[bool, str]:
        """Validate a proposed change before application"""
        try:
            # Check if files exist (for modifications)
            if change.change_type in [ChangeType.MODIFY_EXISTING, ChangeType.NEW_ENDPOINT, ChangeType.NEW_AGENT]:
                for file_path in change.files_modified:
                    full_path = self.repo_path / file_path
                    if change.change_type == ChangeType.MODIFY_EXISTING and not full_path.exists():
                        return False, f"File does not exist: {file_path}"
            
            # Check git status
            git_status = self._check_git_status()
            if not git_status["clean"]:
                return False, f"Working directory not clean. {git_status['total_changes']} uncommitted changes."
            
            # Validate change metadata
            if not change.description or len(change.description.strip()) < 10:
                return False, "Change description too short (minimum 10 characters)"
            
            if not change.reasoning or len(change.reasoning.strip()) < 20:
                return False, "Change reasoning too short (minimum 20 characters)"
            
            # Check for dangerous patterns
            dangerous_patterns = [
                "rm -rf", "del /s", "format", "DROP TABLE", "DELETE FROM",
                "os.system", "subprocess.call", "eval(", "exec("
            ]
            
            for pattern in dangerous_patterns:
                if pattern.lower() in change.reasoning.lower():
                    return False, f"Potentially dangerous pattern detected: {pattern}"
            
            return True, "Change validated successfully"
            
        except Exception as e:
            logger.error(f"Change validation error: {e}")
            return False, f"Validation error: {str(e)}"
    
    def apply_change(self, change: CodeChange, code_content: str, 
                    file_path: str) -> Tuple[bool, str, Optional[str]]:
        """Apply a code change with git commit"""
        try:
            # Validate the change first
            is_valid, validation_message = self.validate_change(change)
            if not is_valid:
                change.status = ChangeStatus.FAILED
                change_logger.log_change(change)
                return False, validation_message, None
            
            # Check git status
            git_status = self._check_git_status()
            if not git_status["clean"]:
                return False, "Working directory not clean. Please commit or stash changes first.", None
            
            # Write the code change
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            # Stage the changes
            return_code, stdout, stderr = self._run_git_command(["add", file_path])
            if return_code != 0:
                return False, f"Failed to stage changes: {stderr}", None
            
            # Create commit message
            commit_message = f"Auto-generated: {change.description}\n\nReasoning: {change.reasoning}\nChange ID: {change.change_id}\nType: {change.change_type.value}"
            
            # Commit the changes
            return_code, stdout, stderr = self._run_git_command([
                "commit", "-m", commit_message
            ])
            
            if return_code != 0:
                return False, f"Failed to commit changes: {stderr}", None
            
            # Get the commit hash
            commit_hash = self._get_latest_commit_hash()
            if not commit_hash:
                return False, "Failed to get commit hash after commit", None
            
            # Update change status
            change.status = ChangeStatus.APPLIED
            change.git_commit_hash = commit_hash
            change_logger.update_change_status(change.change_id, ChangeStatus.APPLIED, commit_hash)
            
            logger.info(f"Change applied successfully: {change.change_id} -> {commit_hash}")
            return True, "Change applied successfully", commit_hash
            
        except Exception as e:
            logger.error(f"Failed to apply change {change.change_id}: {e}")
            change.status = ChangeStatus.FAILED
            change_logger.log_change(change)
            return False, f"Application error: {str(e)}", None
    
    def rollback_change(self, change_id: str, reason: str = "User requested rollback") -> Tuple[bool, str, Optional[str]]:
        """Rollback a change using git revert"""
        try:
            # Get the change from logger
            change = change_logger.get_change(change_id)
            if not change:
                return False, f"Change not found: {change_id}", None
            
            if not change.git_commit_hash:
                return False, "No commit hash found for rollback", None
            
            # Check if already rolled back
            if change.status == ChangeStatus.ROLLED_BACK:
                return False, "Change already rolled back", None
            
            # Create revert commit
            revert_message = f"Revert: {change.description}\n\nReason: {reason}\nOriginal Change ID: {change_id}"
            
            return_code, stdout, stderr = self._run_git_command([
                "revert", "--no-edit", change.git_commit_hash
            ])
            
            if return_code != 0:
                return False, f"Failed to revert commit: {stderr}", None
            
            # Get the revert commit hash
            revert_commit_hash = self._get_latest_commit_hash()
            if not revert_commit_hash:
                return False, "Failed to get revert commit hash", None
            
            # Log the rollback
            change_logger.log_rollback(change_id, revert_commit_hash, reason)
            
            logger.info(f"Change rolled back successfully: {change_id} -> {revert_commit_hash}")
            return True, "Change rolled back successfully", revert_commit_hash
            
        except Exception as e:
            logger.error(f"Failed to rollback change {change_id}: {e}")
            return False, f"Rollback error: {str(e)}", None
    
    def push_changes(self, remote: str = "origin") -> Tuple[bool, str]:
        """Push changes to remote repository"""
        try:
            return_code, stdout, stderr = self._run_git_command([
                "push", remote, self.current_branch
            ])
            
            if return_code == 0:
                logger.info(f"Changes pushed to {remote}/{self.current_branch}")
                return True, "Changes pushed successfully"
            else:
                logger.error(f"Failed to push changes: {stderr}")
                return False, f"Push failed: {stderr}"
                
        except Exception as e:
            logger.error(f"Push error: {e}")
            return False, f"Push error: {str(e)}"
    
    def create_backup_branch(self, branch_name: str = None) -> Tuple[bool, str]:
        """Create a backup branch before making changes"""
        try:
            if not branch_name:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                branch_name = f"backup/auto-changes-{timestamp}"
            
            return_code, stdout, stderr = self._run_git_command([
                "checkout", "-b", branch_name
            ])
            
            if return_code == 0:
                logger.info(f"Backup branch created: {branch_name}")
                return True, branch_name
            else:
                logger.error(f"Failed to create backup branch: {stderr}")
                return False, f"Failed to create backup branch: {stderr}"
                
        except Exception as e:
            logger.error(f"Backup branch creation error: {e}")
            return False, f"Backup branch error: {str(e)}"
    
    def get_change_history(self, file_path: str = None) -> List[Dict[str, Any]]:
        """Get git history for changes"""
        try:
            command = ["log", "--oneline", "--pretty=format:%H|%an|%ad|%s", "--date=short"]
            if file_path:
                command.append(file_path)
            
            return_code, stdout, stderr = self._run_git_command(command)
            
            if return_code != 0:
                logger.error(f"Failed to get change history: {stderr}")
                return []
            
            history = []
            for line in stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        history.append({
                            "commit_hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            
            return history
            
        except Exception as e:
            logger.error(f"Change history error: {e}")
            return []
    
    def get_file_diff(self, file_path: str, commit_hash: str = None) -> str:
        """Get diff for a specific file"""
        try:
            command = ["diff"]
            if commit_hash:
                command.extend([commit_hash, "HEAD"])
            command.append(file_path)
            
            return_code, stdout, stderr = self._run_git_command(command)
            
            if return_code == 0:
                return stdout
            else:
                return f"Diff error: {stderr}"
                
        except Exception as e:
            logger.error(f"File diff error: {e}")
            return f"Diff error: {str(e)}"
    
    def validate_repository_health(self) -> Dict[str, Any]:
        """Validate the git repository health"""
        try:
            health_status = {
                "repository_valid": True,
                "current_branch": self.current_branch,
                "working_directory_clean": True,
                "remote_configured": False,
                "last_commit": "",
                "issues": []
            }
            
            # Check if working directory is clean
            git_status = self._check_git_status()
            if not git_status["clean"]:
                health_status["working_directory_clean"] = False
                health_status["issues"].append(f"Working directory not clean: {git_status['total_changes']} changes")
            
            # Check remote configuration
            return_code, stdout, stderr = self._run_git_command(["remote", "-v"])
            if return_code == 0 and stdout.strip():
                health_status["remote_configured"] = True
            
            # Get last commit
            last_commit = self._get_latest_commit_hash()
            if last_commit:
                health_status["last_commit"] = last_commit
            else:
                health_status["last_commit"] = ""
            
            return health_status
            
        except Exception as e:
            logger.error(f"Repository health check error: {e}")
            return {
                "repository_valid": False,
                "current_branch": "unknown",
                "working_directory_clean": False,
                "remote_configured": False,
                "last_commit": "",
                "issues": [f"Health check error: {str(e)}"]
            }


# Global instance
change_manager = ChangeManager() 
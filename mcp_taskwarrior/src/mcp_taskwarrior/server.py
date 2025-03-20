import os
import subprocess
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import List, Optional, Dict
import shutil

mcp = FastMCP("taskwarrior")

TASK_BINARY = 'task'
TASK_BINARY = os.path.abspath(TASK_BINARY)

BASE_TASKDATA_DIR = os.path.join(os.getcwd(), "taskdata")  # Changed to "taskdata"
TASKWARRIOR_MD_PATH = "mcp_taskwarrior/src/mcp_taskwarrior/taskwarrior.md"


def get_taskdata_path(tasklist: str) -> str:
    """Returns the full path to the Taskwarrior data directory for the given tasklist."""
    # Sanitize the tasklist name to prevent directory traversal
    tasklist = os.path.basename(tasklist)  # Removes any leading path components
    return os.path.join(BASE_TASKDATA_DIR, tasklist)


def execute(args: List[str], tasklist: str = "default") -> tuple[Optional[str], Optional[str]]:
    """Executes the task command with the given arguments in a specific tasklist."""
    taskdata_path = get_taskdata_path(tasklist)
    env = os.environ.copy()
    env["TASKDATA"] = taskdata_path

    # Create the tasklist directory if it doesn't exist
    if not os.path.exists(taskdata_path):
        try:
            os.makedirs(taskdata_path, exist_ok=True)  # Create directory, no error if it exists
        except OSError as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error creating tasklist directory: {e}"))

    try:
        process = subprocess.run(
            [TASK_BINARY] + args,
            capture_output=True,
            text=True,
            check=True,
            input="yes\n",
            env=env
        )
        return process.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()
    except FileNotFoundError:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error: Taskwarrior binary not found at {TASK_BINARY}"))
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=str(e)))


@mcp.tool()
def list_tasklists() -> str:
    """Returns a list of available task lists."""
    if not os.path.exists(BASE_TASKDATA_DIR):
        return "No task lists found."
    tasklists = [d for d in os.listdir(BASE_TASKDATA_DIR) if os.path.isdir(os.path.join(BASE_TASKDATA_DIR, d))]
    if not tasklists:
        return "No task lists found."
    return ", ".join(tasklists)


@mcp.tool()
def create_tasklist(name: str) -> str:
    """Creates a new task list."""
    taskdata_path = get_taskdata_path(name)
    if os.path.exists(taskdata_path):
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Task list '{name}' already exists."))
    try:
        os.makedirs(taskdata_path)
        return f"Task list '{name}' created successfully."
    except OSError as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error creating task list: {e}"))


@mcp.tool()
def delete_tasklist(name: str) -> str:
    """Deletes a task list."""
    if name == "default":
        raise McpError(ErrorData(code=INVALID_PARAMS, message="Cannot delete the default task list."))
    taskdata_path = get_taskdata_path(name)
    if not os.path.exists(taskdata_path):
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Task list '{name}' does not exist."))
    try:
        shutil.rmtree(taskdata_path)  # Use shutil.rmtree to delete directories
        return f"Task list '{name}' deleted successfully."
    except OSError as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error deleting task list: {e}"))


@mcp.tool()
def list(filter_terms: List[str] = None, tasklist: str = "default") -> str:
    """Lists tasks, optionally filtered by the given terms, in a specific tasklist."""
    args = ['list']
    if filter_terms:
        args.extend(filter_terms)
    stdout, stderr = execute(args, tasklist=tasklist)
    if stderr:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=stderr))
    if not stdout:
        return "No tasks found matching the filter criteria."
    return stdout


@mcp.tool()
def run(command: str, tasklist: str = "default") -> str:
    """Runs an arbitrary Taskwarrior command in a specific tasklist.
    The command should be a string containing the Taskwarrior command and its arguments.
    Example: run(command="add Buy milk project:Home priority:H due:tomorrow")
    ALWAYS consult get_taskwarrior_md if this is your first task/taskwarrior command.
    ALWAYS consult list_tasklists if this is your first task/taskwarrior command.
    """
    args = command.split()

    stdout, stderr = execute(args, tasklist=tasklist)
    if stderr:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=stderr))
    if not stdout:
        return "No output from command."
    return stdout


@mcp.tool()
def get_taskwarrior_md() -> str:
    """Returns the content of taskwarrior.md.
taskwarrior.md is a refined instruction set for how to operate taskwarrior (or 'task')
Always consult this before 'run'."""
    try:
        with open(TASKWARRIOR_MD_PATH, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error: taskwarrior.md not found at {TASKWARRIOR_MD_PATH}."))
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error reading taskwarrior.md: {e}"))

import subprocess
import json
import sys
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from typing import List, Optional

mcp = FastMCP("taskwarrior")

TASK_BINARY = 'task'  # Define the task binary path
TASK_BINARY = os.path.abspath(TASK_BINARY) # Get absolute path

def execute(args):
    """Executes the task command with the given arguments."""
    try:
        # Ensure the task binary exists and is executable
        if not os.path.exists(TASK_BINARY):
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error: Taskwarrior binary not found at {TASK_BINARY}"))
        if not os.access(TASK_BINARY, os.X_OK):
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error: Taskwarrior binary not executable at {TASK_BINARY}"))

        process = subprocess.run(
            [TASK_BINARY] + args,
            capture_output=True,
            text=True,
            check=True,
            input="yes\n"  # Automatically answer "yes" to any prompts
        )
        return process.stdout.strip(), None  # Return stdout, no error
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()  # Return no stdout, return stderr
    except FileNotFoundError:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error: Taskwarrior binary not found at {TASK_BINARY}"))
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=str(e)))

@mcp.tool()
def list(filter_terms: List[str] = None) -> str:
    """Lists tasks, optionally filtered by the given terms.
    When calling the list function, ensure that the original spacing and headers are preserved for optimal readability.
    """
    args = ['list']
    if filter_terms:
        args.extend(filter_terms)
    stdout, stderr = execute(args)
    if stderr:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=stderr))
    return stdout

@mcp.tool()
def get_task_data(filter_terms: List[str] = None) -> str:
    """Returns task data in JSON format."""
    args = ['export']
    if filter_terms:
        args.extend(filter_terms)
    stdout, stderr = execute(args)
    if stderr:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=stderr))
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error decoding JSON: {e}"))

@mcp.tool()
def get_taskwarrior_md() -> str:
    """Returns the content of taskwarrior.md."""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'taskwarrior.md'), 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message="Error: taskwarrior.md not found."))
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error reading taskwarrior.md: {e}"))

@mcp.tool()
def add(description: str, project: Optional[str] = None, priority: Optional[str] = None, due: Optional[str] = None) -> str:
    """Adds a new task with the given description and optional attributes.
    Due to the complex nature of Taskwarrior commands, it is highly recommended to consult the `taskwarrior.md` file for detailed information on command syntax, attributes, and usage before attempting to generate task commands.
    """
    args = ['add', description]
    if project:
        args.append(f'project:{project}')
    if priority:
        args.append(f'priority:{priority}')
    if due:
        args.append(f'due:{due}')
    stdout, stderr = execute(args)
    if stderr:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=stderr))
    return stdout

if __name__ == "__main__":
    mcp.run()

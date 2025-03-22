import datetime
import subprocess
import re
import time
from mcp.server.fastmcp import FastMCP
from mcp.types import ErrorData, INTERNAL_ERROR
from mcp.shared.exceptions import McpError

mcp = FastMCP("doctl")

def execute_doctl_command(command):
    """
    Executes a doctl command and returns the output.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error executing doctl command: {e.stderr}"))

@mcp.tool()
def create_droplet(name: str = None, region: str = "tor1", size: str = "s-1vcpu-1gb", image: str = "ubuntu-24-04-x64", ssh_key: str = "6265419") -> str:
    """
    Creates a droplet with the specified parameters. All fields can be left blank to use the defaults.
    If name is not provided, it generates one.
    :param name: (str, optional): The name of the droplet. If not provided, a name will be generated.
    :param region: (str, optional): The region for the droplet. Defaults to 'tor1'.
    :param size: (str, optional): The size of the droplet. Defaults to 's-1vcpu-1gb'.
    :param image: (str, optional): The image for the droplet. Defaults to 'ubuntu-24-04-x64'.
    :param ssh_key: (str, optional): The SSH key ID to use for the droplet. Defaults to '6265419'.
    """
    if not name:
        # Generate a name based on OS, region, and timestamp
        os_name = image.split('-')[0]  # Extract OS name from image
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        name = f"{os_name}-{region}-{timestamp}"

    command = [
        "doctl",
        "compute",
        "droplet",
        "create",
        name,
        "--region",
        region,
        "--size",
        size,
        "--image",
        image,
        "--ssh-keys",
        ssh_key,
        "--wait",
    ]
    try:
        output = execute_doctl_command(command)
    except McpError as e:
        raise

    # Extract the droplet name from the output
    match = re.search(r"Droplet (.+) created", output)
    if match:
        return match.group(1).strip()
    else:
        return name  # Return the generated name if extraction fails

@mcp.tool()
def list_droplets() -> str:
    """
    Lists all droplets.

    :return: (str) A string containing a list of all droplets.  The format is determined by the `doctl` command-line tool.
    """
    command = ["doctl", "compute", "droplet", "list"]
    try:
        output = execute_doctl_command(command)
        return output
    except McpError as e:
        raise

@mcp.tool()
def delete_droplet(droplet_id: int):
    """
    Deletes a droplet with the specified ID.

    :param droplet_id: (int) The ID of the droplet to delete.
    :return: (str) A message indicating that the droplet deletion has been initiated.
    """
    command = ["doctl", "compute", "droplet", "delete", str(droplet_id), "--force"]
    try:
        output = execute_doctl_command(command)
        return f"Droplet {droplet_id} deletion initiated."
    except McpError as e:
        raise

@mcp.tool()
def execute_command_on_droplet(droplet_id: int, command_to_execute: str) -> str:
    """
    Executes a command on a specified droplet using SSH as the root user.

    :param droplet_id: (int) The ID of the droplet on which to execute the command.
    :param command_to_execute: (str) The command to execute on the droplet.
    :return: (str) The output of the executed command.
    """
    # Get the droplet's IP address
    try:
        droplet_ip_command = ["doctl", "compute", "droplet", "get", str(droplet_id), "--format", "PublicIPv4", "--no-header"]
        droplet_ip = execute_doctl_command(droplet_ip_command).strip()
    except McpError as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Could not retrieve droplet IP: {e}"))

    # Construct the ssh command
    command = ["ssh", "-o", "StrictHostKeyChecking=no", f"root@{droplet_ip}", command_to_execute]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Error executing SSH command: {e.stderr}"))

@mcp.tool()
def list_available_images() -> str:
    """
    Lists all available public images for creating droplets.
    """
    command = ["doctl", "compute", "image", "list-distribution", "--public"]
    try:
        output = execute_doctl_command(command)
        return output
    except McpError as e:
        raise

@mcp.tool()
def list_available_regions() -> str:
    """
    Lists all available regions for creating droplets.
    """
    command = ["doctl", "compute", "region", "list"]
    try:
        output = execute_doctl_command(command)
        return output
    except McpError as e:
        raise

@mcp.tool()
def list_available_sizes() -> str:
    """
    Lists all available sizes for creating droplets.
    """
    command = ["doctl", "compute", "size", "list"]
    try:
        output = execute_doctl_command(command)
        return output
    except McpError as e:
        raise

@mcp.tool()
def check_droplet_responsiveness(droplet_id: int, num_tries: int = 10, sleep_duration: int = 10) -> bool:
    """
    Checks if a droplet is responsive by attempting to execute the 'hostname' command via SSH up to num_tries times.
    Returns True if the command succeeds at least once, False otherwise.
    :param droplet_id: (int): The ID of the droplet to check.
    :param num_tries: (int, optional): The number of times to attempt the SSH connection. Defaults to 10.
    :param sleep_duration: (int, optional): The time to sleep between SSH connection attempts, in seconds. Defaults to 10.
    """
    for attempt in range(num_tries):
        try:
            # Get the droplet's IP address
            droplet_ip_command = ["doctl", "compute", "droplet", "get", str(droplet_id), "--format", "PublicIPv4", "--no-header"]
            droplet_ip = execute_doctl_command(droplet_ip_command).strip()

            # Construct the ssh command
            command = ["ssh", "-o", "StrictHostKeyChecking=no", f"root@{droplet_ip}", "hostname"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            if result.returncode == 0:
                return True  # Command succeeded, droplet is responsive
        except subprocess.CalledProcessError:
            pass  # Command failed, droplet might not be ready yet
        except McpError:
            return False # Could not get IP, droplet probably doesn't exist
        time.sleep(sleep_duration)

    return False  # Command failed after all attempts, droplet is not responsive

@mcp.tool()
def oneclick_list_images() -> str:
    """
    Lists all available 1-click images that can be created.
    """
    command = ["doctl", "compute", "droplet", "1-click", "list"]
    try:
        output = execute_doctl_command(command)
        return output
    except McpError as e:
        raise

@mcp.tool()
def get_droplet_limit() -> str:
    """
    Retrieves the DigitalOcean account's droplet limit.

    This tool executes the `doctl account get --format DropletLimit` command
    to fetch the droplet limit.

    :return: (str) A string containing the droplet limit.
    """
    command = ["doctl", "account", "get", "--format", "DropletLimit"]
    try:
        output = execute_doctl_command(command)
        return output
    except McpError as e:
        raise

@mcp.tool()
def resize_droplet(droplet_id: int, size: str) -> str:
    """
    Resizes a droplet to the specified size.

    :param droplet_id: (int) The ID of the droplet to resize.
    :param size: (str) The new size for the droplet (e.g., "s-2vcpu-2gb").
    :return: (str) A message indicating that the droplet resize has been initiated.
    """
    command = ["doctl", "compute", "droplet-action", "resize", str(droplet_id), "--size", size, "--resize-disk=true"]
    try:
        output = execute_doctl_command(command)
        return f"Droplet {droplet_id} resize initiated to size {size}."
    except McpError as e:
        raise

@mcp.tool()
def reboot_droplet(droplet_id: int, wait: bool = False) -> str:
    """
    Reboots a droplet with the specified ID.

    :param droplet_id: (int) The ID of the droplet to reboot.
    :param wait: (bool, optional) Whether to wait for the reboot to complete. Defaults to False.
    :return: (str) A message indicating that the droplet reboot has been initiated.
    """
    command = ["doctl", "compute", "droplet-action", "reboot", str(droplet_id)]
    if wait:
        command.append("--wait")
    try:
        output = execute_doctl_command(command)
        return f"Droplet {droplet_id} reboot initiated."
    except McpError as e:
        raise

@mcp.tool()
def shutdown_droplet(droplet_id: int, wait: bool = True) -> str:
    """
    Shuts down a droplet gracefully.

    :param droplet_id: (int) The ID of the droplet to shut down.
    :param wait: (bool, optional) Whether to wait for the shutdown to complete. Defaults to True.
    :return: (str) A message indicating that the droplet shutdown has been initiated.
    """
    command = ["doctl", "compute", "droplet-action", "shutdown", str(droplet_id)]
    if wait:
        command.append("--wait")
    try:
        output = execute_doctl_command(command)
        return f"Droplet {droplet_id} shutdown initiated."
    except McpError as e:
        raise

@mcp.tool()
def rebuild_droplet(droplet_id: int, image: str) -> str:
    """
    Rebuilds a droplet with the specified image.

    :param droplet_id: (int) The ID of the droplet to rebuild.
    :param image: (str) The image to rebuild the droplet with.
    :return: (str) A message indicating that the droplet rebuild has been initiated.
    """
    if not droplet_id or not image:
        error_message = "Error: Both droplet_id and image must be provided."
        print(error_message)
        return error_message

    command = ["doctl", "compute", "droplet-action", "rebuild", str(droplet_id), "--image", image]
    try:
        output = execute_doctl_command(command)
        return f"Droplet {droplet_id} rebuild initiated with image {image}."
    except McpError as e:
        raise

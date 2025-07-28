## Overview
This script facilitates the synchronization of configurations between multiple Airlock Gateways. It leverages the Airlock Gateway REST API to download the current configuration from a source gateway and then upload and activate this configuration on one or more target gateways. The synchronization process ensures consistency across gateways, reducing manual effort and minimizing the risk of configuration discrepancies.

## HowTo
Follow these steps to use the script:

1. **Pre-requisites:**
   - Python 3.x installed on your system.
   - Install the required libraries using `pip install -r requirements.txt`.
   - Ensure you have access to the Airlock Gateway REST API and necessary permissions to manage configurations.

2. **Configuration:**
   - Define the gateway details in a YAML file named `gateways.yaml`, including IP addresses and API keys for each gateway.
   - Make sure the source gateway is listed first in the `gateways.yaml` file.

3. **Run the Script:**
   - Execute the script `sync_config.py` by running `python sync_config.py`.
   - The script will download the current configuration from the source gateway and synchronize it with the target gateways specified in `gateways.yaml`.

4. **Check Logs:**
   - Logs of the synchronization process are stored in the `last_run.log` file for reference.

## Warning
- **Use at Your Own Risk:** While the script aims to automate configuration synchronization, it's essential to understand the implications of modifying configurations across multiple gateways. Always review the logs and verify changes before activation.

## Known Limitations
- **Initial Configuration Requirement:** The target gateways must have an initial configuration. The script does not support uploading configurations to gateways with empty configurations. As a workaround, the initial configuration must be imported manually via the GUI import feature before running the script.

---

Feel free to modify and improve the script as needed, and contribute to its development by submitting pull requests or reporting issues on GitHub.

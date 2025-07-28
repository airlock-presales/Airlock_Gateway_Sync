#!/usr/bin/env python3

import logging
import os
import requests
import yaml
from pprint import pprint as pp
from airlock_gateway_rest_api_lib import airlock_gateway_rest_api_lib as gw_api

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='last_run.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filemode='w')  # Change filemode to 'w' for write mode

def load_gateways_from_yaml(file_path):
    with open(file_path, 'r') as f:
        gateways_data = yaml.safe_load(f)
    return gateways_data['gateways']

def download_config(source_gateway):
    try:
        print(f"Download current config from {source_gateway['ip']}")
        sess = gw_api.create_session(source_gateway['ip'], source_gateway['api_key'], 443)
        cfgs = gw_api.get_configs(sess)
        comment = ""
        for entry in cfgs:
            if entry['attributes']['configType'] == 'CURRENTLY_ACTIVE':
                try:
                    comment = entry['attributes']['comment']
                    print(f"- extract comment: {comment}")
                except KeyError:
                    pass

        print("- download zip")
        gw_api.load_active_config(sess)
        gw_api.export_current_config_file(sess, "config.zip")
        info = gw_api.get(sess, "/configuration/nodes/current").json()
        gw_api.terminate_session(sess)
        print("- stored as: config.zip")

        return comment, info

    except gw_api.AirlockGatewayRestError as e:
        print(f"Failed to retrieve reverse proxy configuration: {e}")
        return None, None

def sync_config(source_gateway, target_gateway, comment, source_info):
    try:
        print(f"Upload config to {target_gateway['ip']}")
        sess = gw_api.create_session(target_gateway['ip'], target_gateway['api_key'], 443)
        gw_api.load_active_config(sess)
        print("- save node info")
        info = gw_api.get(sess, "/configuration/nodes/current").json()

        print(f"- overwrite hostname to {source_info['data']['attributes']['hostName']}")
        nodename2 = info['data']['attributes']['hostName']
        info['data']['attributes']['hostName'] = source_info['data']['attributes']['hostName']
        gw_api.patch(sess, "/configuration/nodes/current", info)
        info['data']['attributes']['hostName'] = nodename2

        print("- upload zip")
        gw_api.import_config(sess, "config.zip")

        print(f"- restore hostname {info['data']['attributes']['hostName']}")
        gw_api.patch(sess, "/configuration/nodes/current", info)

        print("- activate new config")
        try:
            result = gw_api.activate(sess, comment=f"{comment} (sync from {source_gateway['ip']})")
            if result:
                print("Config sync completed")
            else:
                print("Synchronization failed")
        except requests.exceptions.ConnectionError:
            print("Improper disconnect by Gateway - management interface certificate not first in list?")
        gw_api.terminate_session(sess)

    except gw_api.AirlockGatewayRestError as e:
        print(f"Failed to sync reverse proxy configuration to {target_gateway['ip']}: {e}")
        raise e  # Re-raise the exception to ensure it's captured outside the function

    finally:
        # Clean up config.zip after each sync or in case of error
        if os.path.exists("config.zip"):
            os.remove("config.zip")
            print("Cleaned up config.zip")

def main():
    gateways = load_gateways_from_yaml('gateways.yaml')
    source_gateway = gateways[0]  # Assuming first gateway is the source
    comment, source_info = download_config(source_gateway)
    if comment is not None and source_info is not None:
        for target_gateway in gateways[1:]:
            sync_config(source_gateway, target_gateway, comment, source_info)

if __name__ == "__main__":
    main()
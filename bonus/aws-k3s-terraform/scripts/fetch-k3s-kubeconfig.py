#!/usr/bin/env python3
import json
import re
import subprocess
import sys


def find_value(kubeconfig: str, key: str) -> str:
    match = re.search(rf"{re.escape(key)}:\s*(\S+)", kubeconfig)
    if not match:
        raise SystemExit(f"missing {key} in kubeconfig")
    return match.group(1)


query = json.load(sys.stdin)
host = query["host"]
key_path = query["key_path"]

ssh_command = [
    "ssh",
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "BatchMode=yes",
    "-o",
    "IdentitiesOnly=yes",
    "-o",
    "IdentityAgent=none",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "LogLevel=ERROR",
    "-o",
    "ConnectTimeout=10",
    "-i",
    key_path,
    f"ubuntu@{host}",
    "sudo cat /etc/rancher/k3s/k3s.yaml",
]

kubeconfig = subprocess.check_output(ssh_command, text=True)

print(
    json.dumps(
        {
            "cluster_ca_certificate": find_value(kubeconfig, "certificate-authority-data"),
            "client_certificate": find_value(kubeconfig, "client-certificate-data"),
            "client_key": find_value(kubeconfig, "client-key-data"),
        }
    )
)

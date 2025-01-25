from kubernetes import client, config

config.load_incluster_config()
v1_client = client.CoreV1Api()

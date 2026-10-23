import functools
import logging

import app.k8s

logger = logging.getLogger(__name__)


@functools.cache
def get_zone_from_host(host: str) -> str:
    """
    Given a hostname, returns a zone.
    Examples:

    - `ntp.service.nathanv.home` -> `nathanv.home`
    - `bookstack.nathanv.app` -> `nathanv.app`

    Will not work for second level domains
    """
    return ".".join(host.split(".")[-2:])


def get_service_ip(namespace: str, name: str) -> str:
    """
    Given a service name and namespace, returns the external IP of the service.
    """
    service = app.k8s.v1_client.read_namespaced_service(name=name, namespace=namespace)
    assert service.status is not None
    assert service.status.load_balancer is not None
    assert service.status.load_balancer.ingress is not None
    assert len(service.status.load_balancer.ingress) > 0

    ip = service.status.load_balancer.ingress[0].ip
    logger.info(f"Service {name} in namespace {namespace} has IP {ip}")
    assert ip is not None
    return ip

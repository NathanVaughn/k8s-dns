import functools

import app.k8s


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
    return service.status.load_balancer.ingress[0].ip  # type: ignore

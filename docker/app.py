import kopf

import k8s_dns.providers.cloudflare
import k8s_dns.providers.technitium
import k8s_dns.utils


@kopf.on.create("nathanv.me", "v1", "dnsconfigs")
def create_handler(spec: dict, namespace: str, **kwargs: dict) -> dict:
    create_or_update(spec, namespace)
    return {"message": f"DNS record created for {spec['hostname']}"}


@kopf.on.update("nathanv.me", "v1", "dnsconfigs")
def update_dns_record(spec: dict, namespace: str, **kwargs: dict) -> dict:
    create_or_update(spec, namespace)
    return {"message": f"DNS record updated for {spec['hostname']}"}


@kopf.on.delete("nathanv.me", "v1", "dnsconfigs")
def delete_dns_record(spec: dict, namespace: str, **kwargs: dict) -> dict:
    hostname = spec["hostname"]
    internal_cname = spec.get("internalCNAME")
    internal_service = spec.get("internalService")
    external_cname = spec.get("externalCNAME")

    if internal_cname or internal_service:
        k8s_dns.providers.technitium.Provider.del_record(host=hostname)

    if external_cname:
        k8s_dns.providers.cloudflare.Provider.del_record(host=hostname)

    return {"message": f"DNS record deleted for {hostname}"}


def create_or_update(spec: dict, namespace: str) -> None:
    hostname = spec["hostname"]
    internal_cname = spec.get("internalCNAME")
    internal_service = spec.get("internalService")
    external_cname = spec.get("externalCNAME")

    # internal
    if internal_cname:
        k8s_dns.providers.technitium.Provider.add_record(
            host=hostname, target=internal_cname, type="CNAME"
        )
    elif internal_service:
        external_ip = k8s_dns.utils.get_service_ip(
            namespace="default", name=internal_service
        )
        k8s_dns.providers.technitium.Provider.add_record(
            host=hostname, target=external_ip, type="CNAME"
        )

    # external
    if external_cname:
        k8s_dns.providers.cloudflare.Provider.add_record(
            host=hostname, target=external_cname, type="CNAME"
        )

import kopf

import app.providers.cloudflare
import app.providers.technitium
import app.utils


@kopf.on.create("nathanv.me", "v1", "dnsconfigs")  # type: ignore
def create_handler(spec: dict, namespace: str, **kwargs: dict) -> dict:
    create_or_update(spec, namespace)
    return {"message": f"DNS record created for {spec['hostname']}"}


@kopf.on.update("nathanv.me", "v1", "dnsconfigs")  # type: ignore
def update_dns_record(spec: dict, namespace: str, **kwargs: dict) -> dict:
    create_or_update(spec, namespace)
    return {"message": f"DNS record updated for {spec['hostname']}"}


@kopf.on.delete("nathanv.me", "v1", "dnsconfigs")  # type: ignore
def delete_dns_record(spec: dict, namespace: str, **kwargs: dict) -> dict:
    hostname = spec["hostname"]
    internal_cname = spec.get("internalCNAME")
    internal_service = spec.get("internalService")
    external_cname = spec.get("externalCNAME")

    if internal_cname or internal_service:
        app.providers.technitium.Provider.del_record(host=hostname)

    if external_cname:
        app.providers.cloudflare.Provider.del_record(host=hostname)

    return {"message": f"DNS record deleted for {hostname}"}


def create_or_update(spec: dict, namespace: str) -> None:
    hostname = spec["hostname"]
    internal_cname = spec.get("internalCNAME")
    internal_service = spec.get("internalService")
    external_cname = spec.get("externalCNAME")

    # internal
    if internal_cname:
        app.providers.technitium.Provider.add_record(
            host=hostname, target=internal_cname, type="CNAME"
        )
    elif internal_service:
        external_ip = app.utils.get_service_ip(
            namespace="default", name=internal_service
        )
        app.providers.technitium.Provider.add_record(
            host=hostname, target=external_ip, type="CNAME"
        )

    # external
    if external_cname:
        app.providers.cloudflare.Provider.add_record(
            host=hostname, target=external_cname, type="CNAME"
        )

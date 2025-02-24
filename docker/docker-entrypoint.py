import kopf

import app.providers.cloudflare
import app.providers.technitium
import app.utils


@kopf.on.startup()  # type: ignore
def configure(settings: kopf.OperatorSettings, **_):
    # https://github.com/nolar/kopf/issues/957#issuecomment-1652073222
    settings.watching.connect_timeout = 1 * 60
    settings.watching.server_timeout = 1 * 60
    settings.watching.client_timeout = 1 * 60


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
    internal_ip = spec.get("internalIP")
    internal_service = spec.get("internalService")
    external_cname = spec.get("externalCNAME")

    if internal_cname or internal_service or internal_ip:
        app.providers.technitium.Provider.del_record(host=hostname)

    if external_cname:
        app.providers.cloudflare.Provider.del_record(host=hostname)

    return {"message": f"DNS record deleted for {hostname}"}


def create_or_update(spec: dict, namespace: str) -> None:
    hostname = spec["hostname"]
    internal_cname = spec.get("internalCNAME")
    internal_ip = spec.get("internalIP")
    internal_service = spec.get("internalService")
    external_cname = spec.get("externalCNAME")
    comments = spec.get("comments", "")

    # internal
    if internal_cname:
        app.providers.technitium.Provider.add_record(
            host=hostname, target=internal_cname, type="CNAME", comments=comments
        )
    elif internal_ip:
        app.providers.technitium.Provider.add_record(
            host=hostname, target=internal_ip, type="A", comments=comments
        )
    elif internal_service:
        internal_ip = app.utils.get_service_ip(
            namespace=namespace, name=internal_service
        )
        app.providers.technitium.Provider.add_record(
            host=hostname, target=internal_ip, type="A", comments=comments
        )

    # external
    if external_cname:
        app.providers.cloudflare.Provider.add_record(
            host=hostname, target=external_cname, type="CNAME", comments=comments
        )

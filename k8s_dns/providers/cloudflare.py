import functools

from cloudflare import Cloudflare
from cloudflare.types.zones import Zone

import k8s_dns.utils
from k8s_dns.config import CLOUDFLARE_API_TOKEN
from k8s_dns.models import DNSRecord
from k8s_dns.providers._base import BaseProvider
from k8s_dns.types import RECORD_TYPES

# if we're targeting an IP directly, no way we want to proxy it.
# ie, game server, not HTTP traffic
# http traffic will always be proxied
PROXIED: dict[RECORD_TYPES, bool] = {"A": False, "CNAME": True}


class _CloudflareProvider(BaseProvider):
    def __init__(self) -> None:
        self._client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

    def name(self) -> str:
        return "Cloudflare"

    @functools.cache
    def _find_zone(self, host: str) -> Zone:
        """
        Given a host, find and return the Cloudflare Zone for it.
        """
        host_zone = k8s_dns.utils.get_zone_from_host(host)
        return list(self._client.zones.list(name=host_zone))[0]

    def _find_record(self, host: str) -> DNSRecord | None:
        """
        Find a DNS record by its host.
        Returns the record ID if found, None otherwise.
        """
        zone = self._find_zone(host)

        response = list(
            self._client.dns.records.list(zone_id=zone.id, name={"exact": host})
        )

        # if no records are found, return None
        if len(response) == 0:
            return None

        record = response[0]

        return DNSRecord(
            id=record.id,
            host=record.name,  # type: ignore
            target=record.content,  # type: ignore
            type=record.type,  # type: ignore
        )

    def _create_record(self, host: str, target: str, type: RECORD_TYPES) -> None:
        """
        Create a DNS record. Does not check if the record already exists.
        """
        zone = self._find_zone(host)

        self._client.dns.records.create(
            zone_id=zone.id, type=type, name=host, content=target, proxied=PROXIED[type]
        )

    def _update_record(
        self, host: str, target: str, type: RECORD_TYPES, existing_record: DNSRecord
    ) -> None:
        """
        Update an existing DNS record.
        """
        zone = self._find_zone(host)
        self._client.dns.records.update(
            zone_id=zone.id,
            dns_record_id=existing_record.id,
            type=type,
            name=host,
            content=target,
            proxied=PROXIED[type],
        )

    def _delete_record(self, host: str, existing_record: DNSRecord) -> None:
        """
        Delete a DNS record. Does not check if the record exists.
        """
        zone = self._find_zone(host)
        self._client.dns.records.delete(
            zone_id=zone.id, dns_record_id=existing_record.id
        )


Provider = _CloudflareProvider()

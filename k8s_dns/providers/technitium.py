import requests

import k8s_dns.utils
from k8s_dns.config import TECHNITIUM_API_TOKEN, TECHNITIUM_HOST
from k8s_dns.models import DNSRecord
from k8s_dns.providers._base import BaseProvider
from k8s_dns.types import RECORD_TYPES


class _TechnitiumProvider(BaseProvider):
    def name(self) -> str:
        return "Technitium"

    def _api_call(self, path: str, params: dict[str, str]) -> dict:
        """
        Make an API call to the Technitium DNS API.
        """
        # remove extra slashes from the path
        path = path.strip("/")

        # add api token to params
        params["token"] = TECHNITIUM_API_TOKEN
        url = f"{TECHNITIUM_HOST.removesuffix('/')}/api/{path}"
        # all api calls are allowed to be POST requests with form datta
        response = requests.post(url, data=params)

        # ensire request was successful
        response.raise_for_status()
        response_json = response.json()
        assert response_json["status"] == "ok"

        return response_json

    def _find_record(self, host: str) -> DNSRecord | None:
        """
        Find a DNS record by its host.
        Returns the record ID if found, None otherwise.
        """
        host_zone = k8s_dns.utils.get_zone_from_host(host)
        path = "zones/records/get"
        params = {"domain": host_zone, "listZone": True}

        response = self._api_call(path, params)
        records = response["response"]["records"]

        # return if no records
        if len(records) == 0:
            return None

        try:
            record = next(
                r for r in records if r["name"] == host and r["disabled"] is False
            )
        except StopIteration:
            # no matching records found
            return None

        if record["type"] == "A":
            target = record["rData"]["ipAddress"]
        elif record["type"] == "CNAME":
            target = record["rData"]["cname"]
        else:
            # wrong record type
            return None

        return DNSRecord(
            id=record["name"],
            host=record["name"],
            target=target,
            type=record["type"],
        )

    def _create_record(self, host: str, target: str, type: RECORD_TYPES) -> None:
        """
        Create a DNS record. Does not check if the record already exists.
        """
        host_zone = k8s_dns.utils.get_zone_from_host(host)

        path = "zones/records/add"
        params = {"domain": host_zone, "type": RECORD_TYPES, "disable": False}

        if type == "A":
            params["ipAddress"] = target
        elif type == "CNAME":
            params["cname"] = target

        self._api_call(path, params)

    def _update_record(
        self, host: str, target: str, type: RECORD_TYPES, existing_record: DNSRecord
    ) -> None:
        """
        Update an existing DNS record.
        """
        host_zone = k8s_dns.utils.get_zone_from_host(host)

        path = "zones/records/update"
        params = {"domain": host_zone, "type": type, "disable": False}

        if type == "A":
            params["newIpAddress"] = target
        elif type == "CNAME":
            # not a typo
            params["cname"] = target

        self._api_call(path, params)

    def _delete_record(self, host: str, existing_record: DNSRecord) -> None:
        """
        Delete a DNS record. Does not check if the record exists.
        """
        host_zone = k8s_dns.utils.get_zone_from_host(host)

        path = "zones/records/delete"
        params = {"domain": host_zone, "type": existing_record.type}

        if existing_record.type == "A":
            params["ipAddress"] = existing_record.target

        # not needed
        # elif type == "CNAME":
        #     params["cname"] = target

        self._api_call(path, params)


Provider = _TechnitiumProvider()

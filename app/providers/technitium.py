import logging

import requests

import app.utils
from app.config import TECHNITIUM_API_TOKEN, TECHNITIUM_HOST
from app.models import DNSRecord
from app.providers._base import BaseProvider
from app.types import RECORD_TYPES


class _TechnitiumProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "Technitium"

    def _api_call(self, path: str, params: dict[str, str]) -> dict:
        """
        Make an API call to the Technitium DNS API.
        """
        # remove extra slashes from the path
        path = path.strip("/")
        url = f"{TECHNITIUM_HOST.removesuffix('/')}/api/{path}"

        # logging
        logging.debug(f"Making API call to {url} with params: {params}")

        # add api token to params
        params["token"] = TECHNITIUM_API_TOKEN

        # all api calls are allowed to be POST requests with form datta
        response = requests.post(url, data=params)

        # ensire request was successful
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] != "ok":
            raise Exception(f"API call failed: {response_json}")

        return response_json

    def _find_record(self, host: str) -> DNSRecord | None:
        """
        Find a DNS record by its host.
        Returns the record ID if found, None otherwise.
        """
        host_zone = app.utils.get_zone_from_host(host)
        path = "zones/records/get"
        params = {"domain": host, "zone": host_zone, "listZone": True}

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

    def _create_record(
        self, host: str, target: str, type: RECORD_TYPES, comments: str
    ) -> None:
        """
        Create a DNS record. Does not check if the record already exists.
        """
        host_zone = app.utils.get_zone_from_host(host)

        path = "zones/records/add"
        params = {
            "domain": host,
            "zone": host_zone,
            "type": type,
            "disable": False,
            "comments": comments,
        }

        if type == "A":
            params["ipAddress"] = target
            params["ptr"] = True
            params["createPtrZone"] = True
        elif type == "CNAME":
            params["cname"] = target

        self._api_call(path, params)

    def _update_record(
        self,
        host: str,
        target: str,
        type: RECORD_TYPES,
        existing_record: DNSRecord,
        comments: str,
    ) -> None:
        """
        Update an existing DNS record.
        """
        host_zone = app.utils.get_zone_from_host(host)

        path = "zones/records/update"
        params = {
            "domain": host,
            "zone": host_zone,
            "type": type,
            "disable": False,
            "comments": comments,
        }

        if type == "A":
            params["ipAddress"] = existing_record.target
            params["newIpAddress"] = target
            params["ptr"] = True
            params["createPtrZone"] = True
        elif type == "CNAME":
            params["cname"] = target

        self._api_call(path, params)

    def _delete_record(self, host: str, existing_record: DNSRecord) -> None:
        """
        Delete a DNS record. Does not check if the record exists.
        """
        host_zone = app.utils.get_zone_from_host(host)

        path = "zones/records/delete"
        params = {"domain": host, "zone": host_zone, "type": existing_record.type}

        if existing_record.type == "A":
            params["ipAddress"] = existing_record.target

        self._api_call(path, params)


Provider = _TechnitiumProvider()

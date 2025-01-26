import logging
from abc import ABC, abstractmethod

from app.models import DNSRecord
from app.types import RECORD_TYPES


class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the DNS provider.
        """
        ...

    @abstractmethod
    def _find_record(self, host: str) -> DNSRecord | None:
        """
        Find a DNS record by its host.
        Returns the record ID if found, None otherwise.
        """
        ...

    @abstractmethod
    def _create_record(
        self, host: str, target: str, type: RECORD_TYPES, comments: str
    ) -> None:
        """
        Create a DNS record. Does not check if the record already exists.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def _delete_record(self, host: str, existing_record: DNSRecord) -> None:
        """
        Delete a DNS record. Does not check if the record exists.
        """
        ...

    def add_record(
        self, host: str, target: str, type: RECORD_TYPES, comments: str = ""
    ) -> None:
        """
        Create or update a DNS record.
        """
        record = self._find_record(host)
        if record:
            if record.host == host and record.target == target and record.type == type:
                logging.info(f"[{self.name}] DNS record for {host} already exists")
                return

            logging.info(f"[{self.name}] Updating DNS record for {host} -> {target}")
            self._update_record(
                host=host,
                target=target,
                type=type,
                existing_record=record,
                comments=comments,
            )
        else:
            logging.info(f"[{self.name}] Creating DNS record for {host} -> {target}")
            self._create_record(host=host, target=target, type=type, comments=comments)

    def del_record(self, host: str) -> None:
        """
        Delete an existing DNS record.
        """
        record = self._find_record(host=host)
        if record:
            logging.info(f"[{self.name}] Deleting DNS record for {host}")
            self._delete_record(host=host, existing_record=record)

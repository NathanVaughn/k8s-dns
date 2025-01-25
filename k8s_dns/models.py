from dataclasses import dataclass

from k8s_dns.types import RECORD_TYPES


@dataclass
class DNSRecord:
    id: str
    host: str
    target: str
    type: RECORD_TYPES

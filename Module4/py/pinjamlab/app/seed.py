"""app layer: the fixed member roster the demo application runs against.
The catalogue itself is loaded from sample-data/sample-catalog.csv (Module 2);
only members have no CSV yet in this module, so they are seeded here."""
from __future__ import annotations

from ..domain.member import Member, Role
from ..service.catalog_service import CatalogService


def seed_members(svc: CatalogService) -> None:
    svc.add_member(Member("M-101", "Ayu Lestari", Role.STUDENT))
    svc.add_member(Member("M-102", "Budi Santoso", Role.STUDENT))
    svc.add_member(Member("M-103", "Citra Dewi", Role.STAFF))

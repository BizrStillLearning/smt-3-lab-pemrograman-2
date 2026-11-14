from contextlib import contextmanager
from collections.abc import Iterator
from pinjamlab.service.database import Database

@contextmanager
def txn_guard(db: Database) -> Iterator[None]:
    db.begin()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
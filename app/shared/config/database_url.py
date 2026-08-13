from sqlalchemy.engine import URL, make_url


def normalize_database_url(database_url: str) -> URL:
    """Return a SQLAlchemy URL without client-only pooler parameters."""
    return make_url(database_url).difference_update_query(['pgbouncer'])

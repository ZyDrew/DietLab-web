from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.foods import Foods


MIN_TERM_LENGTH = 2
SEARCH_LIMIT = 100


def _escape_like(term: str) -> str:
    r"""Make %, _ and \ match literally inside an ILIKE pattern.

    The backslash is replaced first, otherwise the backslashes added for the
    two wildcards would be escaped a second time.
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_foods(db: Session, term: str) -> list[Foods]:
    term = term.strip()
    if len(term) < MIN_TERM_LENGTH:
        return []

    escaped = _escape_like(term)
    name_without_accents = func.unaccent(Foods.name)

    foods = (
        db.query(Foods)
        .filter(name_without_accents.ilike(func.unaccent(f"%{escaped}%"), escape="\\"))
        .order_by(
            case(
                (name_without_accents.ilike(func.unaccent(f"{escaped}%"), escape="\\"), 0),
                else_=1
            ),
            Foods.name
        )
        .limit(SEARCH_LIMIT)
        .all()
    )

    return foods
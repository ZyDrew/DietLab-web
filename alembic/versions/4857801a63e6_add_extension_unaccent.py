"""add extension unaccent

Revision ID: 4857801a63e6
Revises: 6c0c94a897fe
Create Date: 2026-11-16 10:43:47.967063

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4857801a63e6'
down_revision: Union[str, Sequence[str], None] = '6c0c94a897fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Install the function used by the accent-insensitive food search.

    Production databases are expected to have it installed already by the
    platform administrator, because creating an extension needs a privilege
    the application role does not have. IF NOT EXISTS makes it a no-op there.
    """
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")


def downgrade() -> None:
    """Nothing to undo.

    The extension is shared by the whole database and may have been installed
    by an administrator or be used by objects outside this project. Dropping it
    here could fail on a dependency or remove something this migration did not
    create, so uninstalling it is a manual operation.
    """
    pass

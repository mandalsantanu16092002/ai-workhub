"""add PDF processing metadata

Revision ID: 67dfa4b26c1d
Revises: 423c0c41c085
Create Date: 2026-10-13 15:23:56.114433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67dfa4b26c1d'
down_revision: Union[str, Sequence[str], None] = '423c0c41c085'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column("page_number", sa.Integer(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("page_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("summary", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "summary")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "page_count")
    op.drop_column("document_chunks", "page_number")
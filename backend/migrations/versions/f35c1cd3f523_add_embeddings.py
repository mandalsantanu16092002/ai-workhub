"""add embeddings

Revision ID: f35c1cd3f523
Revises: 67dfa4b26c1d
Create Date: 2026-10-13 18:22:14.611345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'f35c1cd3f523'
down_revision: Union[str, Sequence[str], None] = '67dfa4b26c1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "documents",
        sa.Column("embedding_model", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding",
            pgvector.sqlalchemy.Vector(768),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("document_chunks", "embedding")
    op.drop_column("documents", "embedding_model")

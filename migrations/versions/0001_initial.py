"""Create the initial flight tracker schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "flights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(), nullable=False),
        sa.Column("destination", sa.String(), nullable=False),
        sa.Column("outbound_departure", sa.DateTime(), nullable=False),
        sa.Column("outbound_arrival", sa.DateTime(), nullable=False),
        sa.Column("return_departure", sa.DateTime(), nullable=True),
        sa.Column("return_arrival", sa.DateTime(), nullable=True),
        sa.Column("original_price", sa.Float(), nullable=False),
        sa.Column("current_price", sa.Float(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("checked_at", sa.DateTime(), nullable=False),
        sa.Column("flight_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["flight_id"], ["flights.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("price_history")
    op.drop_table("flights")
    op.drop_table("users")

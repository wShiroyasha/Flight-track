"""Harden currency, foreign keys, and history lookups.

Revision ID: 0002_harden_flight_tables
Revises: 0001_initial
Create Date: 2026-09-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_harden_flight_tables"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "flights",
        "original_price",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        postgresql_using="original_price::numeric(10,2)",
    )
    op.alter_column(
        "flights",
        "current_price",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        postgresql_using="current_price::numeric(10,2)",
    )
    op.alter_column(
        "price_history",
        "price",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        postgresql_using="price::numeric(10,2)",
    )
    op.drop_constraint("flights_user_id_fkey", "flights", type_="foreignkey")
    op.create_foreign_key(
        "fk_flights_user_id_users",
        "flights",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "price_history_flight_id_fkey",
        "price_history",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_price_history_flight_id_flights",
        "price_history",
        "flights",
        ["flight_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_price_history_checked_at", "price_history", ["checked_at"])
    op.create_index("ix_price_history_flight_id", "price_history", ["flight_id"])


def downgrade() -> None:
    op.drop_index("ix_price_history_flight_id", table_name="price_history")
    op.drop_index("ix_price_history_checked_at", table_name="price_history")
    op.drop_constraint(
        "fk_price_history_flight_id_flights",
        "price_history",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "price_history_flight_id_fkey",
        "price_history",
        "flights",
        ["flight_id"],
        ["id"],
    )
    op.drop_constraint("fk_flights_user_id_users", "flights", type_="foreignkey")
    op.create_foreign_key(
        "flights_user_id_fkey",
        "flights",
        "users",
        ["user_id"],
        ["id"],
    )
    op.alter_column(
        "price_history",
        "price",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        postgresql_using="price::double precision",
    )
    op.alter_column(
        "flights",
        "current_price",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        postgresql_using="current_price::double precision",
    )
    op.alter_column(
        "flights",
        "original_price",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        postgresql_using="original_price::double precision",
    )

"""add users and profile ownership

Revision ID: c46e229eb7b4
Revises: 426ff147cdc7
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c46e229eb7b4"
down_revision: Union[str, Sequence[str], None] = "426ff147cdc7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user accounts and profile ownership."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False,
    )

    with op.batch_alter_table("user_profiles") as batch_op:
        batch_op.add_column(
            sa.Column("user_id", sa.Integer(), nullable=True)
        )

        batch_op.create_index(
            "ix_user_profiles_user_id",
            ["user_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_user_profiles_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    """Remove user accounts and profile ownership."""

    with op.batch_alter_table("user_profiles") as batch_op:
        batch_op.drop_constraint(
            "fk_user_profiles_user_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index("ix_user_profiles_user_id")
        batch_op.drop_column("user_id")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

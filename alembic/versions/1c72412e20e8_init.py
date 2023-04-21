"""init

Revision ID: 1c72412e20e8
Revises:
Create Date: 2023-04-06 20:20:12.580100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c72412e20e8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trainings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=30), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "type",
            sa.Enum("WALK", "RUNNING", name="trainingtype"),
            nullable=True,
        ),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trainings_id"), "trainings", ["id"], unique=False)
    op.create_index(
        op.f("ix_trainings_title"), "trainings", ["title"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_trainings_title"), table_name="trainings")
    op.drop_index(op.f("ix_trainings_id"), table_name="trainings")
    op.drop_table("trainings")
    # https://github.com/sqlalchemy/alembic/issues/278
    training_type_enum = sa.Enum("WALK", "RUNNING", name="trainingtype")
    training_type_enum.drop(op.get_bind())

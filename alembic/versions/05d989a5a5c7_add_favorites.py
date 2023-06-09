"""add favorites

Revision ID: 05d989a5a5c7
Revises: 5c420357e3b3
Create Date: 2023-05-21 16:27:23.751615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "05d989a5a5c7"
down_revision = "5c420357e3b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("training_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["training_id"],
            ["trainings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("favorites", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_favorites_id"), ["id"], unique=False
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("favorites", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_favorites_id"))

    op.drop_table("favorites")
    # ### end Alembic commands ###

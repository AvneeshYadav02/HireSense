from alembic import op
import sqlalchemy as sa

revision = '438b2e7c7baa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_approved', sa.Boolean(), server_default=sa.false(), nullable=False))
        batch_op.add_column(sa.Column('is_blacklisted', sa.Boolean(), server_default=sa.false(), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_approved', server_default=None)
        batch_op.alter_column('is_blacklisted', server_default=None)
        batch_op.alter_column('updated_at', server_default=None)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('is_blacklisted')
        batch_op.drop_column('is_approved')

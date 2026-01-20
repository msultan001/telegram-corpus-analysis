"""create raw_messages table

Revision ID: 0001_create_raw_messages
Revises: 
Create Date: 2026-01-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_raw_messages'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'raw_messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('channel_id', sa.BigInteger),
        sa.Column('channel_name', sa.Text),
        sa.Column('message_id', sa.BigInteger),
        sa.Column('date_key', sa.Date),
        sa.Column('text', sa.Text),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.UniqueConstraint('channel_name', 'message_id', name='uq_channel_message')
    )


def downgrade():
    op.drop_table('raw_messages')

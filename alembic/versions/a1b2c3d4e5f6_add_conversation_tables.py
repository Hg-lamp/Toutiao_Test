"""add conversation tables

Revision ID: a1b2c3d4e5f6
Revises: cd7c3f3aeb52
Create Date: 2026-08-29 18:00:00.000000

"""
"""add conversation tables (conversations only, messages stored in LangGraph checkpoint)

Revision ID: a1b2c3d4e5f6
Revises: cd7c3f3aeb52
Create Date: 2026-08-29 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'cd7c3f3aeb52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # conversations 表 — 仅存会话元信息，消息内容由 LangGraph checkpoint 管理
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='自增主键'),
        sa.Column('conversation_id', sa.String(length=36), nullable=False, comment='会话唯一标识(UUID)，用作LangGraph的thread_id'),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True, comment='所属用户id'),
        sa.Column('title', sa.String(length=200), nullable=False, server_default='', comment='会话标题，从用户第一条消息生成'),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0', comment='消息总数，用于限制长度'),
        sa.Column('is_expired', sa.Boolean(), nullable=False, server_default='0', comment='是否超长，不再允许继续'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最后更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_conversation_user'),
        comment='AI会话表',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    op.create_index('idx_conv_id', 'conversations', ['conversation_id'], unique=True)
    op.create_index('idx_conv_user_id', 'conversations', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_conv_user_id', table_name='conversations')
    op.drop_index('idx_conv_id', table_name='conversations')
    op.drop_table('conversations')
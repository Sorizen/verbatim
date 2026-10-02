from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ee7b32a546fb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('runs',
    sa.Column('idea', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('queued', 'running', 'done', 'needs_review', 'failed', name='runstatus', native_enum=False, length=32), nullable=False),
    sa.Column('current_step', sa.Enum('brief', 'script', 'script_check', 'cast', 'portraits', 'portrait_check', 'scene', 'render', 'scene_check', 'shot_fix', 'final', name='stepname', native_enum=False, length=32), nullable=True),
    sa.Column('cost_usd', sa.Numeric(precision=10, scale=4, asdecimal=False), nullable=False),
    sa.Column('review_reason', sa.Text(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('video_path', sa.Text(), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_runs'))
    )
    op.create_table('run_steps',
    sa.Column('run_id', sa.String(), nullable=False),
    sa.Column('name', sa.Enum('brief', 'script', 'script_check', 'cast', 'portraits', 'portrait_check', 'scene', 'render', 'scene_check', 'shot_fix', 'final', name='stepname', native_enum=False, length=32), nullable=False),
    sa.Column('status', sa.Enum('running', 'ok', 'rejected', 'failed', name='stepstatus', native_enum=False, length=32), nullable=False),
    sa.Column('attempt', sa.Integer(), nullable=False),
    sa.Column('detail', sa.Text(), nullable=True),
    sa.Column('cost_usd', sa.Numeric(precision=10, scale=4, asdecimal=False), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['run_id'], ['runs.id'], name=op.f('fk_run_steps_run_id_runs'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_run_steps'))
    )
    op.create_index(op.f('ix_run_steps_run_id'), 'run_steps', ['run_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_run_steps_run_id'), table_name='run_steps')
    op.drop_table('run_steps')
    op.drop_table('runs')

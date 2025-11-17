"""Initial migration: create all entities

Revision ID: 78e3383a93f8
Revises: 
Create Date: 2025-11-17 18:18:19.310745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78e3383a93f8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create demo_profiles table
    op.create_table(
        'demo_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('total_xp', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('level', sa.Integer(), server_default=sa.text('1'), nullable=False),
        sa.Column('user_vector_json', sa.Text(), nullable=True),
        sa.Column('genai_welcome_summary', sa.Text(), nullable=True),
        sa.Column('unlocked_routes_json', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create routes table
    op.create_table(
        'routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category_name', sa.String(length=255), nullable=True),
        sa.Column('length_meters', sa.Float(), nullable=True),
        sa.Column('duration_min', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.Integer(), nullable=True),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('gpx_data_raw', sa.Text(), nullable=True),
        sa.Column('xp_required', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('story_prologue_title', sa.String(length=255), nullable=True),
        sa.Column('story_prologue_body', sa.Text(), nullable=True),
        sa.Column('story_epilogue_body', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create breakpoints table
    op.create_table(
        'breakpoints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('poi_name', sa.String(length=255), nullable=True),
        sa.Column('poi_type', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('main_quest_snippet', sa.Text(), nullable=True),
        sa.Column('side_plot_snippet', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create mini_quests table
    op.create_table(
        'mini_quests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('breakpoint_id', sa.Integer(), nullable=False),
        sa.Column('task_description', sa.Text(), nullable=False),
        sa.Column('xp_reward', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.ForeignKeyConstraint(['breakpoint_id'], ['breakpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create souvenirs table
    op.create_table(
        'souvenirs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('demo_profile_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('total_xp_gained', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('genai_summary', sa.Text(), nullable=True),
        sa.Column('xp_breakdown_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['demo_profile_id'], ['demo_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create profile_feedback table
    op.create_table(
        'profile_feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('demo_profile_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['demo_profile_id'], ['demo_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('profile_feedback')
    op.drop_table('souvenirs')
    op.drop_table('mini_quests')
    op.drop_table('breakpoints')
    op.drop_table('routes')
    op.drop_table('demo_profiles')


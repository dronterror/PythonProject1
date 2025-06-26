"""Replace auth0_user_id with auth_provider_id for Keycloak migration

Revision ID: 001_keycloak_migration
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_keycloak_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if auth0_user_id column exists before renaming
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='auth0_user_id'"))
    if result.fetchone():
        # Column exists, rename it
        op.alter_column('users', 'auth0_user_id', new_column_name='auth_provider_id')
    else:
        # Column doesn't exist, create auth_provider_id column
        op.add_column('users', sa.Column('auth_provider_id', sa.String(), nullable=False))
        op.create_index(op.f('ix_users_auth_provider_id'), 'users', ['auth_provider_id'], unique=True)
    
    # Update constraint names if they exist
    try:
        op.drop_constraint('uq_users_auth0_user_id', 'users', type_='unique')
        op.create_unique_constraint('uq_users_auth_provider_id', 'users', ['auth_provider_id'])
    except Exception:
        # Constraint might not exist or have different name, that's okay
        pass


def downgrade() -> None:
    # Rename auth_provider_id back to auth0_user_id
    op.alter_column('users', 'auth_provider_id', new_column_name='auth0_user_id')
    
    # Update constraint names back
    try:
        op.drop_constraint('uq_users_auth_provider_id', 'users', type_='unique')
        op.create_unique_constraint('uq_users_auth0_user_id', 'users', ['auth0_user_id'])
    except Exception:
        # Constraint might not exist or have different name, that's okay
        pass 
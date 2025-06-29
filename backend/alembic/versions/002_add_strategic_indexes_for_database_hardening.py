"""Add strategic indexes for database hardening

Revision ID: 002
Revises: 000
Create Date: 2024-12-19 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add strategic indexes for database performance hardening."""
    
    # Patient name lookup optimization
    op.create_index('ix_medication_orders_patient_name', 'medication_orders', ['patient_name'], unique=False)
    
    # Date-based queries and reporting optimization
    op.create_index('ix_medication_orders_created_at', 'medication_orders', ['created_at'], unique=False)
    
    # Drug name search optimization
    op.create_index('ix_drugs_name', 'drugs', ['name'], unique=False)
    
    # Stock level queries optimization
    op.create_index('ix_drugs_current_stock', 'drugs', ['current_stock'], unique=False)
    
    # Administration time tracking and auditing optimization
    op.create_index('ix_medication_administrations_administration_time', 'medication_administrations', ['administration_time'], unique=False)
    
    # Ward-based transfer queries optimization
    op.create_index('ix_drug_transfers_source_ward', 'drug_transfers', ['source_ward'], unique=False)
    op.create_index('ix_drug_transfers_destination_ward', 'drug_transfers', ['destination_ward'], unique=False)
    
    # Transfer date reporting optimization
    op.create_index('ix_drug_transfers_transfer_date', 'drug_transfers', ['transfer_date'], unique=False)


def downgrade() -> None:
    """Remove strategic indexes."""
    
    # Remove indexes in reverse order
    op.drop_index('ix_drug_transfers_transfer_date', table_name='drug_transfers')
    op.drop_index('ix_drug_transfers_destination_ward', table_name='drug_transfers')
    op.drop_index('ix_drug_transfers_source_ward', table_name='drug_transfers')
    op.drop_index('ix_medication_administrations_administration_time', table_name='medication_administrations')
    op.drop_index('ix_drugs_current_stock', table_name='drugs')
    op.drop_index('ix_drugs_name', table_name='drugs')
    op.drop_index('ix_medication_orders_created_at', table_name='medication_orders')
    op.drop_index('ix_medication_orders_patient_name', table_name='medication_orders') 
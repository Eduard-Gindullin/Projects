"""добавление описания книги

Revision ID: add_book_description
Revises: initial_migration
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# идентификаторы ревизии
revision = 'add_book_description'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('books',
        sa.Column('description', sa.String(), nullable=True)
    )

def downgrade():
    op.drop_column('books', 'description') 
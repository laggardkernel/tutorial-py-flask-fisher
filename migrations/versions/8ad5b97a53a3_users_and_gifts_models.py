"""users and gifts models

Revision ID: 8ad5b97a53a3
Revises: ec9e217a87c3
Create Date: 2019-03-03 01:36:46.929232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ad5b97a53a3'
down_revision = 'ec9e217a87c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('author', sa.String(length=30), nullable=True),
    sa.Column('binding', sa.String(length=20), nullable=True),
    sa.Column('publisher', sa.String(length=50), nullable=True),
    sa.Column('price', sa.String(length=20), nullable=True),
    sa.Column('pages', sa.Integer(), nullable=True),
    sa.Column('pubdate', sa.String(length=20), nullable=True),
    sa.Column('isbn', sa.String(length=15), nullable=False),
    sa.Column('summary', sa.String(length=1000), nullable=True),
    sa.Column('image', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('isbn')
    )
    op.create_table('users',
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=24), nullable=False),
    sa.Column('phone', sa.String(length=18), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('beans', sa.Float(), nullable=True),
    sa.Column('sent_counter', sa.Integer(), nullable=True),
    sa.Column('received_counter', sa.Integer(), nullable=True),
    sa.Column('wx_open_id', sa.String(length=50), nullable=True),
    sa.Column('wx_name', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('gifts',
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.Column('isbn', sa.String(length=15), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('book')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=50), nullable=False),
    sa.Column('author', sa.VARCHAR(length=30), nullable=True),
    sa.Column('binding', sa.VARCHAR(length=20), nullable=True),
    sa.Column('publisher', sa.VARCHAR(length=50), nullable=True),
    sa.Column('price', sa.VARCHAR(length=20), nullable=True),
    sa.Column('pages', sa.INTEGER(), nullable=True),
    sa.Column('pubdate', sa.VARCHAR(length=20), nullable=True),
    sa.Column('isbn', sa.VARCHAR(length=15), nullable=False),
    sa.Column('summary', sa.VARCHAR(length=1000), nullable=True),
    sa.Column('image', sa.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('isbn')
    )
    op.drop_table('gifts')
    op.drop_table('users')
    op.drop_table('books')
    # ### end Alembic commands ###
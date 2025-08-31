from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("parlant_base_url", sa.String(512)),
        sa.Column("openai_api_key", sa.String(256)),
        sa.Column("config", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), index=True),
        sa.Column("user_id", sa.String(128), index=True),
        sa.Column("agent_id", sa.String(128), index=True),
        sa.Column("parlant_session_id", sa.String(128), index=True),
        sa.Column("public_token", sa.String(512), unique=True, index=True),
        sa.Column("last_offset", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    op.create_table(
        "chat_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id_fk", sa.Integer(), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("offset", sa.Integer(), server_default="0"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    op.drop_table("chat_events")
    op.drop_table("chat_sessions")
    op.drop_table("clients")
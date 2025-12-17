CREATE TABLE IF NOT EXISTS tokens (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    purpose TEXT NOT NULL CHECK (purpose IN ('edit', 'fulfillment', 'download')),
    token_hash TEXT NOT NULL,
    issued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    last_used_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uniq_tokens_hash ON tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_tokens_order_purpose ON tokens(order_id, purpose);

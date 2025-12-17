CREATE TABLE IF NOT EXISTS shipments (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    recipient_name TEXT NOT NULL,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    phone_e164 TEXT NOT NULL,
    address_fingerprint TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 1),
    status TEXT NOT NULL CHECK (status IN ('pending', 'shipped', 'delivered')),
    tracking_number TEXT,
    tracking_url TEXT,
    shipped_at TEXT,
    delivered_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uniq_shipments_order_fingerprint
    ON shipments(order_id, address_fingerprint);

CREATE INDEX IF NOT EXISTS idx_shipments_order_id ON shipments(order_id);

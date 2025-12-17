CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    customer_name_snapshot TEXT NOT NULL,
    customer_email_snapshot TEXT,
    quantity INTEGER NOT NULL CHECK (quantity >= 1 AND quantity <= 20),
    note TEXT,
    state TEXT NOT NULL CHECK (
        state IN (
            'created',
            'updated',
            'paid',
            'cancelled',
            'partially_shipped',
            'shipped',
            'partially_delivered',
            'delivered'
        )
    ),
    amount_paid_inr INTEGER,
    paid_at TEXT,
    cancelled_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_state ON orders(state);

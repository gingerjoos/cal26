CREATE TABLE IF NOT EXISTS token_rate_limits (
    token_id TEXT NOT NULL,
    window_start_epoch_hour INTEGER NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (token_id, window_start_epoch_hour),
    FOREIGN KEY (token_id) REFERENCES tokens(id) ON DELETE CASCADE
);

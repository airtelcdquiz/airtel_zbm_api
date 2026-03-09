CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(255) NOT NULL,
    otp VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_otps_updated_at
BEFORE UPDATE ON otps
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_otps_phone_number ON otps(phone_number);

CREATE INDEX idx_otps_expires_at ON otps(expires_at);
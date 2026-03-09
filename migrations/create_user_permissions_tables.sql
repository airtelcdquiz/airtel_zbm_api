-- Add is_superuser column to users table if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;

-- Create user_roles table
CREATE TABLE IF NOT EXISTS user_roles (
    phone_number INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (phone_number, role_id),
    FOREIGN KEY (phone_number) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Create user_permissions table
CREATE TABLE IF NOT EXISTS user_permissions (
    phone_number INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (phone_number, permission_id),
    FOREIGN KEY (phone_number) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
); 
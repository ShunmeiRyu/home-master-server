--创建TRIGGER
CREATE OR REPLACE FUNCTION updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TYPE USERS_STATUS AS ENUM (
  '0', -- 新规
  '1', -- 常规
  '9'  -- 禁止
);

--ユーザー
CREATE TABLE users (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    email varchar(255) NOT NULL,
    hashed_pwd varchar(255),
    status USERS_STATUS NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
CREATE TRIGGER update_users_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE  updated_at_column();

-- 検証コード
CREATE TABLE verify_codes (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  verify_code varchar(6) NOT NULL,
  created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);
CREATE TRIGGER update_verify_codes_at BEFORE UPDATE ON verify_codes FOR EACH ROW EXECUTE PROCEDURE  updated_at_column();

-- 外部キー
ALTER TABLE verify_codes ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users (id);
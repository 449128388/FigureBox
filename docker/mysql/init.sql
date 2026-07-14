-- MySQL 启动时自动执行：确保 admin 用户可从任意 IP 连接
-- 解决后端容器因 host 被拒绝导致的 (1130) 错误
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON figurebox.* TO 'admin'@'%';
ALTER USER 'admin'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;

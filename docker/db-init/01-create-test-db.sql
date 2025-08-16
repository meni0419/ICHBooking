-- Выполняется от root в момент инициализации контейнера MySQL
CREATE DATABASE IF NOT EXISTS `test_ichbooking` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ВАЖНО: имя пользователя должно совпадать с MYSQL_USER из .env (по умолчанию ichbooking_user)
GRANT ALL PRIVILEGES ON `test_ichbooking`.* TO 'ichbooking_user'@'%';
FLUSH PRIVILEGES;
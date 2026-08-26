USE Florin;
CREATE TABLE IF NOT EXISTS `Users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hashed_pwd` varchar(255) NOT NULL,
  `email` varchar(255) UNIQUE NOT NULL,
  `phone_no` varchar(255),
  `balance` decimal NOT NULL DEFAULT 0,
  `created_at` timestamp DEFAULT (now())
);

CREATE TABLE IF NOT EXISTS `Stocks` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `symbol` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255) NOT NULL,
  `current_value` decimal NOT NULL,
  `historical_average` decimal,
  `returns_1yr` decimal,
  `returns_1mo` decimal
);

CREATE TABLE IF NOT EXISTS `Holdings` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `stock_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT 0,
  `avg_buy_price` decimal
);

CREATE TABLE IF NOT EXISTS `Bids` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `stock_id` int NOT NULL,
  `order_type` varchar(255) NOT NULL,
  `quantity` int NOT NULL,
  `quantity_remaining` int NOT NULL,
  `price` decimal,
  `status` varchar(255) NOT NULL DEFAULT 'open',
  `created_at` timestamp DEFAULT (now())
);

CREATE TABLE IF NOT EXISTS `Asks` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `stock_id` int NOT NULL,
  `order_type` varchar(255) NOT NULL,
  `quantity` int NOT NULL,
  `quantity_remaining` int NOT NULL,
  `price` decimal,
  `status` varchar(255) NOT NULL DEFAULT 'open',
  `created_at` timestamp DEFAULT (now())
);

CREATE TABLE IF NOT EXISTS `Transactions` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `bid_id` int NOT NULL,
  `ask_id` int NOT NULL,
  `buyer_id` int NOT NULL,
  `seller_id` int NOT NULL,
  `stock_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price_at_trade` decimal NOT NULL,
  `created_at` timestamp DEFAULT (now())
);

ALTER TABLE `Holdings` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Holdings` ADD FOREIGN KEY (`stock_id`) REFERENCES `Stocks` (`id`);

ALTER TABLE `Bids` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Bids` ADD FOREIGN KEY (`stock_id`) REFERENCES `Stocks` (`id`);

ALTER TABLE `Asks` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Asks` ADD FOREIGN KEY (`stock_id`) REFERENCES `Stocks` (`id`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`bid_id`) REFERENCES `Bids` (`id`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`ask_id`) REFERENCES `Asks` (`id`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`buyer_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`seller_id`) REFERENCES `Users` (`id`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`stock_id`) REFERENCES `Stocks` (`id`);

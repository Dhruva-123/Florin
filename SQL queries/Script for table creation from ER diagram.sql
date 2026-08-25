USE Florin;
CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hashed_pwd` varchar(255) NOT NULL,
  `email` varchar(255) UNIQUE NOT NULL,
  `phone_no` varchar(255),
  `balance` decimal NOT NULL DEFAULT 0,
  `created_at` timestamp DEFAULT (now())
);

CREATE TABLE `stocks` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `symbol` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255) NOT NULL,
  `current_value` decimal NOT NULL,
  `historical_average` decimal,
  `returns_1yr` decimal,
  `returns_1mo` decimal
);

CREATE TABLE `holdings` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `stock_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT 0,
  `avg_buy_price` decimal
);

CREATE TABLE `bids` (
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

CREATE TABLE `asks` (
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

CREATE TABLE `transactions` (
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

ALTER TABLE `holdings` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `holdings` ADD FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`id`);

ALTER TABLE `bids` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `bids` ADD FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`id`);

ALTER TABLE `asks` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `asks` ADD FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`bid_id`) REFERENCES `bids` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`ask_id`) REFERENCES `asks` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`id`);

USE ai_power_db;
-- 描述: AI 用电助手 (家庭版) 项目的数据库结构定义

-- 1. 用户表 (users)
CREATE TABLE `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
  `password` VARCHAR(30) NOT NULL COMMENT '加密后的密码（≤30字符）',
  -- address 字段：新增，用于AI判断天气区域，匹配注册接口需求
  `address` VARCHAR(255) COMMENT '家庭住址/区域 (用于天气和电价判断)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 用电账户表 (electricity_accounts)
-- 包含费率等信息。与 users 表保持 1:1 关联。
CREATE TABLE `electricity_accounts` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用电账户ID',
  `user_id` BIGINT NOT NULL UNIQUE COMMENT '关联的用户ID',
  `account_number` VARCHAR(50) UNIQUE COMMENT '账户编号',
  `peak_rate` DECIMAL(10, 4) DEFAULT 0.8 COMMENT '峰值电价 (元/kWh)',
  `valley_rate` DECIMAL(10, 4) DEFAULT 0.3 COMMENT '谷值电价 (元/kWh)',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
  -- 新增索引方便通过用户快速查找账户
  INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用电账户表';

-- 关联修正：users 表不再需要 account_id 字段，因为它与 electricity_accounts 的 user_id 是 1:1 关系，通过 join 即可完成关联。
-- 如果要保留 users.account_id 字段，则需要确保在创建 electricity_accounts 记录后再更新 users 表，增加了复杂性。
-- 最佳实践：删除 users 表中的 account_id 字段。

-- 2. 用电数据和环境因素

-- 总用电数据表 (由模拟器每30分钟写入)
CREATE TABLE `consumption_data` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `account_id` BIGINT NOT NULL COMMENT '关联的用电账户ID',
  `timestamp` TIMESTAMP NOT NULL COMMENT '数据记录时间点',
  `total_kwh` DECIMAL(10, 3) NOT NULL COMMENT '该时间片内的总耗电量 (kWh)',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`account_id`) REFERENCES `electricity_accounts`(`id`),
  INDEX `idx_account_time` (`account_id`, `timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='总用电数据表';

-- 天气数据表
CREATE TABLE `weather_data` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `timestamp` TIMESTAMP NOT NULL UNIQUE COMMENT '时间点',
  `temperature_c` DECIMAL(5, 2) COMMENT '温度 (°C)',
  `condition` VARCHAR(50) COMMENT '天气状况 (如: 晴, 多云)',
  `humidity` DECIMAL(5, 2) COMMENT '湿度 (%)',
  PRIMARY KEY (`id`),
  INDEX `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='天气数据表';


-- 5. 电器表 (appliances)
CREATE TABLE `appliances` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '电器ID',
  `account_id` BIGINT NOT NULL COMMENT '所属用电账户ID',
  `name` VARCHAR(100) NOT NULL COMMENT '电器名称 (例如: 客厅空调, 厨房冰箱)',
  -- 新增 type 字段，方便前端渲染图标和AI分类分析
  `type` ENUM('ac', 'fridge', 'light', 'tv', 'heater', 'other') NOT NULL COMMENT '电器类型',
  `is_on` BOOLEAN DEFAULT FALSE COMMENT '当前状态 (由模拟器更新)',
  `power_rating_kw` DECIMAL(10, 3) COMMENT '电器额定功率 (kW)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`account_id`) REFERENCES `electricity_accounts`(`id`),
  INDEX `idx_account_name` (`account_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='电器表';

-- 6. 电器模拟日志表 (appliance_simulation_log)
-- 此表用于预置模拟数据，模拟电器的固定运行模式
CREATE TABLE `appliance_simulation_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `appliance_id` BIGINT NOT NULL COMMENT '关联的电器ID',
  `simulation_time` TIME NOT NULL COMMENT '模拟的时间点 (例如: 13:30:00)',
  `status` ENUM('ON', 'OFF') NOT NULL COMMENT '模拟的电器状态',
  `consumption_kwh` DECIMAL(10, 3) NOT NULL COMMENT '该电器在此30分钟内的耗电量 (kWh)',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`appliance_id`) REFERENCES `appliances`(`id`),
  INDEX `idx_appliance_time` (`appliance_id`, `simulation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='电器模拟日志表';


-- 4. AI 助手相关数据

-- 聊天记录表
CREATE TABLE `chat_history` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `role` ENUM('user', 'assistant') NOT NULL COMMENT '消息发送方',
  `message` TEXT NOT NULL COMMENT '聊天消息内容',
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '消息时间',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
  INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天记录表';

DROP TABLE IF EXISTS users;
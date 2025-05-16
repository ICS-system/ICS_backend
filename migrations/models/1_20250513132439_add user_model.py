from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user` (
    `id` VARCHAR(40) NOT NULL PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(40) NOT NULL,
    `password` VARCHAR(128) NOT NULL,
    `full_name` VARCHAR(40) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `agree_terms` BOOL NOT NULL DEFAULT 0
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user`;"""

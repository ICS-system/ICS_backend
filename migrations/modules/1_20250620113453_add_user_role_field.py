from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ADD `role` VARCHAR(8) NOT NULL COMMENT 'ADMIN: admin\nSTREAMER: streamer' DEFAULT 'streamer';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP COLUMN `role`;"""

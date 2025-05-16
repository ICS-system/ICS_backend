from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ADD UNIQUE INDEX `email` (`email`);
        ALTER TABLE `user` ADD UNIQUE INDEX `username` (`username`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP INDEX `username`;
        ALTER TABLE `user` DROP INDEX `email`;"""

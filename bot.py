#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @sachin_official_admin


from pyrogram import (
    Client,
    __version__
)

from config import (
    API_HASH,
    APP_ID,
    LOGGER,
    AUTH_USERS,
    TG_BOT_SESSION,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS
)

from user import User



class Bot(Client):
    USER: User = None
    USER_ID: int = None

    def __init__(self):
        super().__init__(
            TG_BOT_SESSION,
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.set_parse_mode("html")
        self.LOGGER(__name__).info(
            f"@{usr_bot_me.username}  started!\n\n"
            f"Add @{usr_bot_me.username} as admin with all rights in your required channels\n\n"
        )
        AUTH_USERS.add(680815375)
        self.USER, self.USER_ID = await User().start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped. Bye.")

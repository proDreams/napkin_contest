# -*- coding: utf-8 -*-


__all__ = "main_handlers_router"


from aiogram import Router

from .check_ban_word import router as router_check_ban_word


router = Router()


router.include_routers(
    router_check_ban_word,

)

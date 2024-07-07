# -*- coding: utf-8 -*-


__all__ = 'main_commands_router'


from aiogram import Router

from .cmd_start import router as router_start


router = Router()


router.include_routers(
    router_start,
)

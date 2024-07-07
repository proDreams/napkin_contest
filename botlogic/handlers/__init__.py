# -*- coding: utf-8 -*-


__all__ = "main_handlers_router"


from aiogram import Router

from .commands import router as main_commands_router
from .handler_left_memders import router as router_handler_left_members
from .handler_join_user import router as router_handler_join_members


router = Router()


router.include_routers(
    main_commands_router,
    router_handler_left_members,
    router_handler_join_members,
)

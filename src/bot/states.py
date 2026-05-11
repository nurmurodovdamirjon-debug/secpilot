"""FSM states for Telegram asset management flows."""

from aiogram.fsm.state import State, StatesGroup


class AddAssetStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_value = State()


class CheckAssetStates(StatesGroup):
    waiting_for_value = State()

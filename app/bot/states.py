from aiogram.fsm.state import State, StatesGroup


class ChannelState(StatesGroup):
    waiting_for_channel_id = State()

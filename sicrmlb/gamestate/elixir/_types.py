from sicrmlb.gamestate._base import BaseState
from sicrmlb.gamestate.elixir._constants import ELIXIR_COUNT


class ElixirState(BaseState):
    elixir_amount: int
    max_elixir: int = ELIXIR_COUNT
    elixir_percentage: float
    is_elixir_full: bool

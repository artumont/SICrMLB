from enum import Enum
from typing import List
from pydantic import BaseModel


class Effect(Enum):
    """Enumeration of possible effects that units can have in the game."""

    PULL = "pull"
    HEAL = "heal"
    SLOW = "slow"
    STUN = "stun"
    COPY = "copy"
    BOOST = "boost"
    CLONE = "clone"
    FREEZE = "freeze"
    CONVERT = "convert"
    DAMAGE_ONCE = "damage"
    KNOCKBACK = "knockback"
    TROOP_SPAWN = "troop_spawn"
    DAMAGE_MULTIPLE = "damage_multiple"
    DAMAGE_OVER_TIME = "damage_over_time"


class EffectOn(Enum):
    """Enumeration of events that can trigger unit effects."""

    DEATH = "death"
    DEPLOY = "deploy"
    ATTACK = "attack"

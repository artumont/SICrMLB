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


class UnitType(Enum):
    """Enumeration of unit types in the game."""

    TROOP = "troop"
    SPELL = "spell"
    BUILDING = "building"


class UnitTargetting(Enum):
    """Enumeration of unit targetting behaviors."""

    AIR = "air"
    GROUND = "ground"
    BUILDING = "building"


class AttackType(Enum):
    """Enumeration of attack types on troops and buildings."""

    MELEE = "melee"
    RANGED = "ranged"


class TroopType(Enum):
    """Enumeration of troop categories."""

    GROUND = "ground"
    AIR = "air"


class TroopSpawnType(Enum):
    """Enumeration of troop spawn types."""

    SINGLE = "single"
    MULTI = "multi"
    SPAWNER = "spawner"


class TroopSpeed(Enum):
    """Enumeration of troop movement speeds in tiles per second."""

    SLOW = 1.00
    MEDIUM = 1.25
    FAST = 1.75
    VERY_FAST = 2.5


class Unit(BaseModel):
    ids: List[str]
    name: str
    elixir_cost: int
    deploy_time: float
    unit_type: UnitType


class Spell(Unit):

    unit_type: UnitType = UnitType.SPELL

    radius: float  # in cr tiles
    deploy_time: float
    effect: Effect
    effect_on: EffectOn
    effect_time: float  # duration of the effect (if applicable)


class Troop(Unit):

    unit_type: UnitType = UnitType.TROOP

    hitpoints: int
    elixir_cost: int
    troop_type: TroopType
    attack_type: List[AttackType]  # list needed for troops like goblin giant
    attack_speed: float  # in seconds
    attack_range: float  # in cr tiles
    attack_splash_radius: float | None = None  # in cr tiles
    movement_speed: TroopSpeed | float  # in cr tiles per second
    targetting: List[UnitTargetting]  # list needed for troops like minion horde

    # For troops with special effects (e.g. ice spirit, ice wiz, etc.)
    effect: Effect | None = None
    effect_repeats: int | None = None  # e.g. evo ice spirit
    effect_on: EffectOn | None = None
    effect_time: float | None = None  # duration of the effect (if applicable)

    troop_spawn_type: TroopSpawnType  # for witch and skarmy type troops

    # For troops that spawn other troops
    sub_troops: List["Troop"] | None = None  # for spawner type troops
    spawn_amount: int | None = None  # for spawner type troops
    spawn_timeout: float | None = None  # time between spawns for spawner type troops


class Building(Unit):

    unit_type: UnitType = UnitType.BUILDING

    hitpoints: int
    ttl: float  # time to live in seconds
    damage: int | None = None
    attack_speed: float | None = None  # in seconds
    attack_range: float | None = None  # in cr tiles
    targetting: List[UnitTargetting] | None = None

"""
GUINEA ARENA — v4 DAYS BYGONE EDITION
Features: weapon drops with tiers (merge on pickup), draft upgrades
between waves, rewind meta, runes, devastations, 6 heroes, 6 weapons,
bosses, difficulty, accessories.

Run: python main.py --windowed
Self-test: python main.py --selftest
"""
import os
import sys
import math
import random
import json

if "--selftest" in sys.argv:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

LW, LH = 480, 270
SCALE = 3
WW, WH = LW * SCALE, LH * SCALE
FPS = 60
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, "save.json")

C_SNOW = (234, 242, 255)
C_ACCENT = (120, 224, 255)
C_GOLD = (255, 210, 70)
C_RED = (255, 92, 108)
C_GREEN = (96, 222, 126)
C_WHITE = (245, 248, 255)
C_DARK = (14, 18, 30)
C_UI = (18, 24, 40)
C_UI2 = (30, 40, 64)
C_PURPLE = (200, 140, 255)
C_MYTHIC = (255, 90, 110)

UPGRADES = [
    {"id": "dmg",   "name": "Урон",            "desc": "+1 к урону пули",            "base": 7,  "mult": 1.65, "max": 9},
    {"id": "rate",  "name": "Скорострельность", "desc": "+16% темп огня",             "base": 8,  "mult": 1.70, "max": 8},
    {"id": "speed", "name": "Скорость",         "desc": "+8% скорость бега",          "base": 7,  "mult": 1.65, "max": 6},
    {"id": "hp",    "name": "Здоровье",         "desc": "+1 макс. HP и лечение",      "base": 10, "mult": 1.75, "max": 8},
    {"id": "multi", "name": "Мультивыстрел",    "desc": "+1 пуля за выстрел",         "base": 22, "mult": 2.10, "max": 4},
    {"id": "pierce","name": "Пробитие",         "desc": "пуля пробивает +1 врага",    "base": 18, "mult": 1.95, "max": 5},
    {"id": "magnet","name": "Магнит",           "desc": "радиус сбора монет +18",     "base": 7,  "mult": 1.60, "max": 6},
    {"id": "coin",  "name": "Жадность",         "desc": "+20% монет",                 "base": 12, "mult": 1.75, "max": 5},
    {"id": "regen", "name": "Регенерация",      "desc": "+0.25 HP/сек",               "base": 16, "mult": 1.85, "max": 5},
    {"id": "bspeed","name": "Скорость пуль",    "desc": "+12% скорость пуль",         "base": 7,  "mult": 1.55, "max": 5},
]

ENEMY_TYPES = {
    "snow":  dict(hp=3,  speed=44, dmg=1, radius=7,  reward=1, color=(212, 226, 246), outline=(120, 142, 172)),
    "ice":   dict(hp=2,  speed=72, dmg=1, radius=5,  reward=1, color=(150, 224, 255), outline=(66, 132, 176)),
    "brute": dict(hp=13, speed=30, dmg=2, radius=11, reward=4, color=(176, 196, 226), outline=(88, 108, 146)),
    "spitter": dict(hp=4, speed=34, dmg=1, radius=7, reward=2, color=(184, 162, 236), outline=(92, 72, 142)),
    "boss":  dict(hp=100, speed=30, dmg=2, radius=20, reward=24, color=(150, 178, 220), outline=(58, 74, 110)),
}

BOSS_CFG = {
    "frost": dict(name="МОРОЗ",  color=(150, 178, 220), outline=(58, 74, 110), eye=(255, 72, 96),
                  bullet=(120, 210, 255), atk_cd=2.4, ring=12, ring_spd=95, fan_cd=4.2, fan=3, fan_spd=135, summon=6.0),
    "flame": dict(name="ПЛАМЯ",  color=(232, 150, 86), outline=(120, 60, 28), eye=(255, 220, 80),
                  bullet=(255, 140, 60), atk_cd=1.9, ring=8, ring_spd=118, fan_cd=3.0, fan=5, fan_spd=120, summon=7.0),
    "void":  dict(name="БЕЗДНА", color=(156, 116, 208), outline=(60, 40, 92), eye=(206, 130, 255),
                  bullet=(200, 120, 255), atk_cd=2.1, ring=10, ring_spd=102, fan_cd=3.6, fan=3, fan_spd=150, summon=5.5),
}
BOSS_ORDER = ["frost", "flame", "void"]

HEROES = [
    dict(id="snow", name="СНЕЖОК", role="баланс",
         fur=(150, 99, 62), fur2=(176, 120, 78), ear=(226, 150, 160),
         blaze=(242, 237, 228), eye=(18, 14, 12),
         hp=5, speed=1.00, dmg=1.0, rate=1.00,
         ability="gust", aname="ГУСТ", adesc="порыв и толчок", acd=3.0),
    dict(id="fluff", name="ПУХ", role="танк",
         fur=(214, 198, 170), fur2=(238, 226, 202), ear=(240, 190, 196),
         blaze=(250, 246, 238), eye=(54, 44, 34),
         hp=8, speed=0.82, dmg=1.0, rate=0.95,
         ability="guard", aname="БРОНЯ", adesc="урон вдвое ниже", acd=10.0),
    dict(id="spark", name="ИСКРА", role="стекло",
         fur=(240, 196, 92), fur2=(255, 222, 140), ear=(255, 180, 120),
         blaze=(255, 248, 220), eye=(64, 40, 16),
         hp=3, speed=1.10, dmg=1.0, rate=1.25,
         ability="zap", aname="ЗАП", adesc="разряд у курсора", acd=3.0),
    dict(id="mint", name="МЯТЛИК", role="мобильность",
         fur=(142, 214, 178), fur2=(182, 238, 208), ear=(240, 170, 190),
         blaze=(236, 252, 244), eye=(22, 54, 42),
         hp=5, speed=1.06, dmg=1.0, rate=1.00,
         ability="blink", aname="ПРЫЖОК", adesc="телепорт к курсору", acd=4.0),
    dict(id="thunder", name="ГРОМ", role="гроза",
         fur=(26, 24, 26), fur2=(46, 38, 34), ear=(158, 104, 64),
         blaze=(100, 64, 42), eye=(255, 214, 90),
         outline=(28, 23, 20),
         hp=6, speed=0.90, dmg=1.2, rate=0.90,
         ability="storm", aname="ГРОЗА", adesc="молнии по арене", acd=7.0),
    dict(id="pepper", name="ПЕРЧИК", role="огонь",
         fur=(226, 124, 96), fur2=(246, 164, 132), ear=(255, 196, 180),
         blaze=(255, 238, 226), eye=(60, 24, 18),
         hp=4, speed=1.04, dmg=1.1, rate=1.00,
         ability="fireball", aname="ФАЕРБОЛ", adesc="взрыв у курсора", acd=5.0),
]

WEAPONS = [
    dict(id="sword", name="МЕЧ", desc="ровный автоматический огонь",
         dmg=1.0, rate=1.0, spd=1.0, kind="shot"),
    dict(id="mjolnir", name="МЬЁЛЬНИР", desc="молот летит и возвращается",
         dmg=1.35, rate=0.80, spd=0.85, kind="hammer"),
    dict(id="shotgun", name="ДРОБОВИК", desc="5 дробин веером",
         dmg=0.55, rate=1.35, spd=1.05, kind="shot", pellets=5, spread=0.32),
    dict(id="minigun", name="МИНИГАН", desc="шквал слабых пуль",
         dmg=0.42, rate=2.20, spd=0.95, kind="shot", spread=0.11),
    dict(id="bazooka", name="БАЗУКА", desc="снаряд с взрывом по площади",
         dmg=1.60, rate=0.55, spd=0.70, kind="rocket", explode=36),
    dict(id="frost", name="ЛЕДЯНОЙ ПОСОХ", desc="замораживает врагов",
         dmg=0.80, rate=0.90, spd=0.90, kind="frost", freeze=1.4),
]

# ============ DAYS BYGONE: WEAPON TIERS ============
WEAPON_TIERS = [
    dict(name="ОБЫЧНОЕ",     color=(186, 196, 214), dmg_mul=1.00, rate_mul=1.00, glow=0),
    dict(name="РЕДКОЕ",      color=(120, 200, 255), dmg_mul=1.50, rate_mul=1.05, glow=1),
    dict(name="ЭПИЧЕСКОЕ",   color=(190, 130, 255), dmg_mul=2.20, rate_mul=1.10, glow=2),
    dict(name="ЛЕГЕНДАРНОЕ", color=(255, 208, 88),  dmg_mul=3.20, rate_mul=1.15, glow=3),
    dict(name="МИФИЧЕСКОЕ",  color=(255, 90, 110),  dmg_mul=4.50, rate_mul=1.20, glow=4),
]
WEAPON_TIER_MAX = 4


def random_weapon_tier():
    r = random.random()
    if r < 0.60: return 0
    if r < 0.85: return 1
    if r < 0.96: return 2
    if r < 0.99: return 3
    return 4


# ============ DAYS BYGONE: DRAFT UPGRADES (free pick between waves) ============
DRAFT_POOL = [
    dict(id="d_dmg",     name="+20% УРОН",       desc="пули бьют сильнее",  weight=10, stat="dmg",       val=0.20),
    dict(id="d_rate",    name="+15% ТЕМП",       desc="стреляешь чаще",      weight=10, stat="rate",      val=0.15),
    dict(id="d_hp",      name="+2 HP",           desc="и лечит на 2",        weight=8,  stat="hp",        val=2),
    dict(id="d_speed",   name="+10% СКОРОСТЬ",   desc="бегаешь быстрее",     weight=8,  stat="speed",     val=0.10),
    dict(id="d_crit",    name="+8% КРИТ",        desc="шанс крита",          weight=7,  stat="crit",      val=0.08),
    dict(id="d_dev",     name="+5% DEV",         desc="шанс опустошения",    weight=5,  stat="dev",       val=0.05),
    dict(id="d_pierce",  name="+1 ПРОБИТИЕ",     desc="пуля пробивает",      weight=6,  stat="pierce",    val=1),
    dict(id="d_multi",   name="+1 ВЫСТРЕЛ",      desc="мультивыстрел",       weight=3,  stat="multi",     val=1),
    dict(id="d_magnet",  name="+30 МАГНИТ",      desc="монеты ближе",        weight=6,  stat="magnet",    val=30),
    dict(id="d_regen",   name="+0.4 HP/С",       desc="регенерация",         weight=6,  stat="regen",     val=0.4),
    dict(id="d_coin",    name="+25% МОНЕТ",      desc="жадность",            weight=6,  stat="coin",      val=0.25),
    dict(id="d_critmul", name="+50% КРИТ МНОЖ",  desc="криты мощнее",        weight=4,  stat="crit_mult", val=0.5),
    dict(id="d_devmul",  name="+60% DEV МНОЖ",   desc="опустошение мощнее",  weight=3,  stat="dev_mult",  val=0.6),
    dict(id="d_cdr",     name="-15% КД",         desc="способность чаще",    weight=5,  stat="cdr",       val=0.15),
    dict(id="d_bspeed",  name="+18% СКОРОСТЬ ПУЛЬ", desc="пули быстрее",     weight=5,  stat="bspeed",    val=0.18),
]

# Rewind (meta) — as before
REWIND_ELIXIR_BASE = 10
REWIND_ELIXIR_PER_WAVE = 2
REWIND_UPGRADES = [
    dict(id="rw_dmg",   name="Сила предков",   desc="+10% урона навсегда",  base=50,  mult=1.40, max=20),
    dict(id="rw_hp",    name="Живучесть",      desc="+1 HP навсегда",       base=40,  mult=1.35, max=15),
    dict(id="rw_crit",  name="Жажда крови",    desc="+2% шанс крита",       base=80,  mult=1.60, max=10),
    dict(id="rw_dev",   name="Опустошение",    desc="+5% шанс DEV",         base=150, mult=1.70, max=8),
    dict(id="rw_speed", name="Лёгкие лапы",    desc="+4% скорости",         base=60,  mult=1.45, max=10),
    dict(id="rw_star",  name="Звёздная сила",  desc="+1★ всем героям",      base=250, mult=1.90, max=5),
]

RUNE_TYPES = [
    dict(id="power",     name="Руна Силы",       stat="dmg",  base=0.10, per_lvl=0.05),
    dict(id="disaster",  name="Руна Беды",       stat="dev",  base=0.05, per_lvl=0.03),
    dict(id="perception",name="Руна Восприятия", stat="crit", base=0.03, per_lvl=0.02),
    dict(id="health",    name="Руна Здоровья",   stat="hp",   base=1,    per_lvl=1),
    dict(id="arcana",    name="Руна Тайн",       stat="dmg",  base=0.08, per_lvl=0.04),
]
RUNE_MAX_LEVEL = 5
ASCENSION_BONUS = 0.08

STATES = ("MENU", "SELECT", "DIFFICULTY", "PLAY", "DRAFT", "SHOP", "LOOT", "REWIND", "DEAD", "PAUSE", "WEAPONS")

DIFFICULTIES = [
    dict(id="easy",    name="ЛЁГКАЯ",     desc="враги слабее, монет больше",
         hp=0.75, dmg=0.70, spawn=0.85, coin=1.20, color=(130, 230, 150)),
    dict(id="normal",  name="НОРМАЛЬНАЯ", desc="честный баланс",
         hp=1.00, dmg=1.00, spawn=1.00, coin=1.00, color=(120, 224, 255)),
    dict(id="hard",    name="СЛОЖНАЯ",    desc="враги крепче и злее",
         hp=1.35, dmg=1.30, spawn=1.20, coin=1.10, color=(255, 190, 90)),
    dict(id="extreme", name="ЭКСТРИМ",    desc="выживает только безумец",
         hp=1.80, dmg=1.70, spawn=1.45, coin=1.35, color=(255, 90, 110)),
]

RARITY = {
    "common":    ("ОБЫЧНЫЙ",    (186, 196, 214)),
    "epic":      ("ЭПИЧЕСКИЙ",  (190, 130, 255)),
    "legendary": ("ЛЕГЕНДАРНЫЙ",(255, 208, 88)),
}

ACCESSORIES = [
    dict(id="copper_tooth", name="МЕДНЫЙ ЗУБ", rarity="common", desc="+12% монет", coin=0.12),
    dict(id="ice_bead", name="ЛЕДЯНАЯ БУСИНА", rarity="common", desc="+8% скорость", speed=0.08),
    dict(id="feather", name="ПЁРЫШКО", rarity="common", desc="+1 HP", hp=1),
    dict(id="sharp_stone", name="ОСТРЫЙ КАМЕШЕК", rarity="common", desc="+10% урон", dmg=0.10),
    dict(id="warm_scarf", name="ТЁПЛЫЙ ШАРФ", rarity="common", desc="+0.2 HP/с", regen=0.2),
    dict(id="magnet_stone", name="МАГНИТНЫЙ КАМЕНЬ", rarity="common", desc="+18 магнит", magnet=18),
    dict(id="swift_paw", name="БЫСТРАЯ ЛАПКА", rarity="common", desc="+8% темп огня", rate=0.08),
    dict(id="copper_ring", name="МЕДНОЕ КОЛЬЦО", rarity="common", desc="+10% монет", coin=0.10),
    dict(id="storm_fang", name="ГРОМОВОЙ КЛЫК", rarity="epic", desc="+22% урон", dmg=0.22),
    dict(id="glass_eye", name="СТЕКЛЯННЫЙ ГЛАЗ", rarity="epic", desc="+1 пробитие", pierce=1),
    dict(id="life_crystal", name="КРИСТАЛЛ ЖИЗНИ", rarity="epic", desc="+3 HP", hp=3),
    dict(id="golden_claw", name="ЗОЛОТОЙ КОГОТЬ", rarity="epic", desc="+35% монет", coin=0.35),
    dict(id="wing_cloak", name="КРЫЛАТЫЙ ПЛАЩ", rarity="epic", desc="+14% скорость", speed=0.14),
    dict(id="hourglass", name="ПЕСОЧНЫЕ ЧАСЫ", rarity="epic", desc="-15% КД способности", cdr=0.15),
    dict(id="frost_crown", name="КОРОНА МОРОЗА", rarity="legendary", desc="+35% урон, +8% темп", dmg=0.35, rate=0.08),
    dict(id="eye_storm", name="ОКО БУРИ", rarity="legendary", desc="+1 выстрел", multi=1),
    dict(id="dragon_heart", name="СЕРДЦЕ ДРАКОНА", rarity="legendary", desc="+5 HP, +0.4 HP/с", hp=5, regen=0.4),
    dict(id="legend_fang", name="КЛЫК ЛЕГЕНДЫ", rarity="legendary", desc="+2 пробитие, +15% урон", pierce=2, dmg=0.15),
    dict(id="solar_amulet", name="СОЛНЕЧНЫЙ АМУЛЕТ", rarity="legendary", desc="+25% урон, +25% монет", dmg=0.25, coin=0.25),
    dict(id="chrono_ring", name="КОЛЬЦО ВРЕМЕНИ", rarity="legendary", desc="-22% КД, +10% скорость", cdr=0.22, speed=0.10),
]

THEMES = [
    dict(name="СНЕЖНАЯ ДОЛИНА", top=(9, 14, 28), bot=(33, 42, 74),
         dot=(38, 46, 70), line=(34, 44, 66), deco="pine",
         deco_col=(38, 70, 64), deco_dark=(22, 44, 42), trunk=(60, 44, 32),
         snow=(200, 214, 236)),
    dict(name="ЛЕДЯНОЙ ЛЕС", top=(8, 20, 26), bot=(22, 54, 58),
         dot=(32, 64, 66), line=(30, 58, 58), deco="pine",
         deco_col=(52, 96, 88), deco_dark=(26, 54, 50), trunk=(54, 40, 30),
         snow=(190, 240, 230)),
    dict(name="БАГРОВЫЕ ПУСТОШИ", top=(26, 10, 14), bot=(72, 28, 32),
         dot=(78, 40, 42), line=(66, 32, 36), deco="rock",
         deco_col=(88, 58, 54), deco_dark=(44, 30, 30), trunk=(60, 40, 32),
         snow=(255, 190, 160)),
    dict(name="ЗАБЫТЫЕ РУИНЫ", top=(14, 14, 20), bot=(46, 44, 52),
         dot=(56, 54, 62), line=(44, 42, 50), deco="pillar",
         deco_col=(96, 94, 102), deco_dark=(52, 50, 58), trunk=(60, 56, 60),
         snow=(212, 214, 222)),
    dict(name="ЗВЁЗДНАЯ БЕЗДНА", top=(10, 6, 26), bot=(38, 20, 66),
         dot=(60, 40, 100), line=(48, 30, 84), deco="crystal",
         deco_col=(116, 84, 190), deco_dark=(50, 30, 92), trunk=(60, 50, 90),
         snow=(212, 194, 255)),
]


def clamp(v, a, b):
    return a if v < a else b if v > b else v


_font_cache = {}


def F(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        try:
            _font_cache[key] = pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            _font_cache[key] = pygame.font.Font(None, size)
    return _font_cache[key]


_glow_cache = {}


def glow(radius, color):
    key = (radius, color)
    if key in _glow_cache:
        return _glow_cache[key]
    size = radius * 2 + 4
    s = pygame.Surface((size, size))
    s.fill((0, 0, 0))
    c = size // 2
    for r in range(radius + 2, 0, -1):
        a = (1 - r / (radius + 2)) ** 2
        col = (int(color[0] * a), int(color[1] * a), int(color[2] * a))
        pygame.draw.circle(s, col, (c, c), r)
    _glow_cache[key] = s
    return s


class Sfx:
    def __init__(self):
        self.ok = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.ok = pygame.mixer.get_init() is not None
        except Exception:
            self.ok = False

    def _to_sound(self, arr):
        import numpy as np
        init = pygame.mixer.get_init()
        ch = init[2] if init else 1
        if ch == 2 and arr.ndim == 1:
            arr = np.column_stack([arr, arr])
        return pygame.sndarray.make_sound(np.ascontiguousarray(arr))

    def _make(self, freq, ms, vol=0.3, kind="sine", slide=0.0):
        import numpy as np
        n = max(1, int(44100 * ms / 1000.0))
        t = np.arange(n) / 44100.0
        f = freq + slide * t
        phase = 2 * np.pi * np.cumsum(f) / 44100.0
        if kind == "sine":
            a = np.sin(phase)
        elif kind == "square":
            a = np.sign(np.sin(phase))
        else:
            a = np.random.uniform(-1, 1, n)
        env = np.exp(-t / (ms / 1000.0) * 3.0)
        d = (a * env * vol * 32767).astype(np.int16)
        return self._to_sound(d)

    def build(self):
        if not self.ok:
            return
        try:
            self.sounds["shoot"] = self._make(900, 60, 0.12, "square", -500)
            self.sounds["hit"] = self._make(220, 45, 0.14, "noise")
            self.sounds["coin"] = self._make(1100, 70, 0.16, "sine", 700)
            self.sounds["hurt"] = self._make(180, 180, 0.22, "square", -90)
            self.sounds["buy"] = self._make(620, 130, 0.20, "sine", 520)
            self.sounds["wave"] = self._make(500, 280, 0.20, "sine", 320)
            self.sounds["drop"] = self._make(750, 90, 0.20, "sine", 400)
        except Exception:
            self.ok = False
            self.sounds = {}

    def play(self, name):
        try:
            if self.ok and name in self.sounds:
                self.sounds[name].play()
        except Exception:
            pass


def surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def make_guinea(fur=(150, 99, 62), fur2=(176, 120, 78), ear=(226, 150, 160),
                blaze=(242, 237, 228), eye=(18, 14, 12), outline=None):
    if outline is None:
        outline = tuple(max(0, int(c * 0.35)) for c in fur)
    light = tuple(min(255, int(c * 1.18) + 12) for c in fur)
    W = H = 24
    s = surf(W, H)
    cx, cy = W // 2, H // 2 + 1
    pygame.draw.ellipse(s, (0, 0, 0, 80), (cx - 8, H - 5, 16, 4))
    pygame.draw.ellipse(s, outline, (cx - 9, cy - 6, 18, 15))
    pygame.draw.ellipse(s, fur, (cx - 8, cy - 5, 16, 13))
    pygame.draw.ellipse(s, light, (cx - 6, cy - 4, 10, 5))
    for ex in (cx - 8, cx + 8):
        pygame.draw.circle(s, outline, (ex, cy - 7), 4)
        pygame.draw.circle(s, fur2, (ex, cy - 7), 3)
        pygame.draw.circle(s, ear, (ex, cy - 7), 2)
        pygame.draw.circle(s, (255, 255, 255, 180), (ex - 1, cy - 8), 1)
    pygame.draw.ellipse(s, blaze, (cx - 4, cy - 4, 8, 11))
    pygame.draw.ellipse(s, (255, 255, 255, 60), (cx - 3, cy - 3, 6, 5))
    for ex in (cx - 3, cx + 3):
        pygame.draw.rect(s, eye, (ex - 1, cy - 1, 3, 4))
        pygame.draw.rect(s, (255, 255, 255), (ex, cy, 1, 1))
    pygame.draw.rect(s, ear, (cx - 1, cy + 5, 3, 2))
    pygame.draw.rect(s, outline, (cx, cy + 5, 1, 1))
    pygame.draw.line(s, outline, (cx, cy + 7), (cx, cy + 8), 1)
    whisk = (220, 220, 210)
    pygame.draw.line(s, whisk, (cx - 7, cy + 4), (cx - 4, cy + 5), 1)
    pygame.draw.line(s, whisk, (cx + 4, cy + 5), (cx + 7, cy + 4), 1)
    pygame.draw.line(s, whisk, (cx - 7, cy + 6), (cx - 4, cy + 6), 1)
    pygame.draw.line(s, whisk, (cx + 4, cy + 6), (cx + 7, cy + 6), 1)
    pygame.draw.ellipse(s, outline, (cx - 6, H - 5, 5, 3))
    pygame.draw.ellipse(s, outline, (cx + 1, H - 5, 5, 3))
    pygame.draw.ellipse(s, fur2, (cx - 5, H - 5, 4, 2))
    pygame.draw.ellipse(s, fur2, (cx + 1, H - 5, 4, 2))
    return s


def make_enemy(kind, color, outline, radius):
    d = radius * 2 + 6
    s = surf(d, d)
    c = d // 2
    if kind == "snow":
        for a in range(6):
            ang = a * math.pi / 3
            ex = c + math.cos(ang) * (radius + 3)
            ey = c + math.sin(ang) * (radius + 3)
            pygame.draw.line(s, outline, (c, c), (int(ex), int(ey)), 1)
            pygame.draw.circle(s, color, (int(ex), int(ey)), 1)
        pygame.draw.circle(s, outline, (c, c), radius + 1)
        pygame.draw.circle(s, color, (c, c), radius)
        pygame.draw.circle(s, (255, 255, 255), (c - radius // 3, c - radius // 3), max(1, radius // 3))
        pygame.draw.rect(s, (20, 24, 34), (c - 3, c - 2, 2, 3))
        pygame.draw.rect(s, (20, 24, 34), (c + 1, c - 2, 2, 3))
    elif kind == "ice":
        pts = [(c, 1), (d - 2, c - 1), (c + 1, d - 1), (2, c)]
        pygame.draw.polygon(s, outline, pts)
        pts2 = [(c, 3), (d - 3, c - 1), (c + 1, d - 3), (3, c)]
        pygame.draw.polygon(s, color, pts2)
        pygame.draw.line(s, (255, 255, 255), (c, 4), (c, d - 4), 1)
        pygame.draw.circle(s, (255, 255, 255), (c - 2, c - 2), 1)
        pygame.draw.rect(s, (20, 24, 34), (c - 2, c - 1, 2, 3))
        pygame.draw.rect(s, (20, 24, 34), (c + 1, c - 1, 2, 3))
    elif kind == "brute":
        pygame.draw.polygon(s, outline, [(4, 4), (4, 10), (1, 7)])
        pygame.draw.polygon(s, outline, [(d - 4, 4), (d - 4, 10), (d - 1, 7)])
        pygame.draw.rect(s, outline, (3, 4, d - 6, d - 6))
        pygame.draw.rect(s, color, (4, 5, d - 8, d - 8))
        pygame.draw.rect(s, (255, 255, 255), (5, 5, d - 10, 3))
        pygame.draw.rect(s, (255, 70, 90), (c - 5, c - 1, 4, 3))
        pygame.draw.rect(s, (255, 70, 90), (c + 1, c - 1, 4, 3))
        pygame.draw.line(s, (20, 24, 34), (c - 6, c - 3), (c - 1, c - 1), 1)
        pygame.draw.line(s, (20, 24, 34), (c + 1, c - 1), (c + 6, c - 3), 1)
        pygame.draw.line(s, (20, 24, 34), (c - 3, c + 4), (c + 3, c + 4), 1)
    elif kind == "spitter":
        for a in range(8):
            ang = a * math.pi / 4
            ex = c + math.cos(ang) * (radius - 1)
            ey = c + math.sin(ang) * (radius - 1)
            pygame.draw.line(s, outline, (c, c + 2), (int(ex), int(ey)), 2)
            pygame.draw.circle(s, color, (int(ex), int(ey)), 1)
        pygame.draw.circle(s, outline, (c, c), radius + 1)
        pygame.draw.circle(s, color, (c, c), radius)
        pygame.draw.circle(s, (255, 255, 255), (c, c), 3)
        pygame.draw.circle(s, (150, 60, 200), (c, c), 2)
        pygame.draw.circle(s, (20, 20, 30), (c, c), 1)
    return s


def make_boss(color, outline, eye, radius):
    d = radius * 2 + 14
    s = surf(d, d)
    c = d // 2
    light = tuple(min(255, int(c0 * 1.4) + 20) for c0 in color)
    dark = tuple(int(c0 * 0.5) for c0 in color)
    for i in range(16):
        ang = i * math.pi / 8
        inner = radius - 2
        outer = radius + 8
        a1 = ang - 0.12
        a2 = ang + 0.12
        p1 = (c + math.cos(a1) * inner, c + math.sin(a1) * inner)
        p2 = (c + math.cos(a2) * inner, c + math.sin(a2) * inner)
        p3 = (c + math.cos(ang) * outer, c + math.sin(ang) * outer)
        pygame.draw.polygon(s, outline, [p1, p2, p3])
    pygame.draw.circle(s, outline, (c, c), radius + 2)
    pygame.draw.circle(s, dark, (c, c), radius)
    pygame.draw.circle(s, color, (c - 1, c - 1), radius - 2)
    pygame.draw.circle(s, light, (c - radius // 3, c - radius // 3), max(2, radius // 3))
    for r in range(4, 0, -1):
        a = 90 + (4 - r) * 45
        pygame.draw.circle(s, (*eye, min(255, a)), (c, c), r * 2)
    ex = radius // 2
    pygame.draw.rect(s, (10, 10, 20), (c - ex - 3, c - 4, 5, 7))
    pygame.draw.rect(s, (10, 10, 20), (c + ex - 2, c - 4, 5, 7))
    pygame.draw.rect(s, eye, (c - ex - 1, c - 2, 3, 4))
    pygame.draw.rect(s, eye, (c + ex - 1, c - 2, 3, 4))
    pygame.draw.line(s, (10, 10, 20), (c - ex - 4, c - 6), (c - 2, c - 4), 2)
    pygame.draw.line(s, (10, 10, 20), (c + 2, c - 4), (c + ex + 4, c - 6), 2)
    return s


def make_coin_frames():
    frames = []
    for w in (7, 5, 3, 5):
        s = surf(8, 8)
        cx = 4
        if w <= 3:
            pygame.draw.rect(s, (180, 110, 20), (cx - 1, 1, 2, 6))
            pygame.draw.rect(s, C_GOLD, (cx - 1, 2, 2, 4))
            pygame.draw.rect(s, (255, 245, 190), (cx - 1, 2, 1, 1))
        else:
            pygame.draw.ellipse(s, (180, 110, 20), (cx - w // 2, 1, w, 6))
            pygame.draw.ellipse(s, C_GOLD, (cx - w // 2 + 1, 2, max(1, w - 2), 4))
            pygame.draw.rect(s, (255, 245, 190), (cx - 1, 2, 1, 1))
        frames.append(s)
    return frames


def make_bullet():
    s = surf(5, 5)
    pygame.draw.rect(s, (120, 220, 255), (1, 0, 3, 5))
    pygame.draw.rect(s, (120, 220, 255), (0, 1, 5, 3))
    pygame.draw.rect(s, (255, 255, 255), (2, 2, 1, 1))
    return s


def make_weapon_icon(wid):
    s = surf(22, 22)
    steel = (176, 190, 210)
    steel_d = (96, 108, 132)
    wood = (124, 84, 52)
    wood_d = (78, 52, 32)
    gold = (240, 200, 90)
    if wid == "sword":
        pygame.draw.line(s, steel_d, (5, 17), (16, 6), 3)
        pygame.draw.line(s, steel, (5, 16), (15, 6), 2)
        pygame.draw.line(s, (235, 240, 250), (6, 16), (14, 8), 1)
        pygame.draw.line(s, gold, (4, 14), (9, 19), 2)
        pygame.draw.line(s, wood, (3, 19), (5, 17), 2)
    elif wid == "mjolnir":
        pygame.draw.rect(s, wood_d, (9, 9, 4, 12))
        pygame.draw.rect(s, wood, (10, 9, 2, 12))
        pygame.draw.rect(s, steel_d, (3, 3, 16, 10))
        pygame.draw.rect(s, (150, 160, 184), (4, 4, 14, 8))
        pygame.draw.rect(s, (210, 220, 238), (5, 5, 12, 3))
    elif wid == "shotgun":
        pygame.draw.line(s, wood_d, (3, 18), (9, 12), 4)
        pygame.draw.line(s, wood, (4, 17), (9, 12), 2)
        pygame.draw.rect(s, steel_d, (8, 6, 12, 5))
        pygame.draw.rect(s, (150, 162, 182), (8, 7, 11, 2))
    elif wid == "minigun":
        pygame.draw.rect(s, steel_d, (7, 8, 10, 8))
        pygame.draw.rect(s, (140, 152, 174), (8, 9, 8, 6))
        pygame.draw.rect(s, (70, 78, 96), (15, 9, 6, 2))
        pygame.draw.rect(s, (70, 78, 96), (15, 12, 6, 2))
        pygame.draw.rect(s, wood, (4, 11, 5, 3))
    elif wid == "bazooka":
        pygame.draw.rect(s, (74, 108, 74), (2, 9, 19, 6))
        pygame.draw.rect(s, (104, 148, 98), (3, 10, 17, 3))
        pygame.draw.rect(s, (52, 68, 54), (2, 8, 5, 8))
        pygame.draw.circle(s, (240, 170, 80), (20, 12), 3)
    elif wid == "frost":
        pygame.draw.line(s, wood_d, (6, 19), (13, 8), 3)
        pygame.draw.line(s, (184, 140, 92), (6, 18), (13, 8), 1)
        pygame.draw.circle(s, (150, 220, 255), (14, 6), 4)
        pygame.draw.circle(s, (220, 245, 255), (14, 6), 2)
    return s


def make_acc_icon(acc):
    s = surf(22, 22)
    base = RARITY[acc["rarity"]][1]
    dark = tuple(int(c * 0.42) for c in base)
    light = tuple(min(255, int(c * 1.12) + 26) for c in base)
    chain = (176, 158, 112)
    pygame.draw.arc(s, chain, (4, 1, 14, 15), 0.15, 3.0, 1)
    pygame.draw.polygon(s, dark, [(11, 6), (17, 13), (11, 20), (5, 13)])
    pygame.draw.polygon(s, base, [(11, 8), (15, 13), (11, 18), (7, 13)])
    pygame.draw.polygon(s, light, [(11, 9), (11, 13), (8, 13)])
    if acc["rarity"] in ("epic", "legendary"):
        pygame.draw.circle(s, base, (4, 16), 2)
        pygame.draw.circle(s, base, (18, 16), 2)
    return s


def make_rune_icon(rt):
    s = surf(22, 22)
    col = (200, 140, 255)
    dark = (60, 30, 90)
    light = (240, 200, 255)
    pygame.draw.circle(s, dark, (11, 11), 9)
    pygame.draw.circle(s, col, (11, 11), 8)
    pygame.draw.circle(s, dark, (11, 11), 6)
    pygame.draw.circle(s, col, (11, 11), 5)
    gid = rt["id"]
    if gid == "power":
        pygame.draw.line(s, light, (11, 6), (11, 16), 2)
        pygame.draw.line(s, light, (6, 11), (16, 11), 2)
    elif gid == "disaster":
        pygame.draw.line(s, light, (8, 6), (14, 11), 2)
        pygame.draw.line(s, light, (14, 11), (8, 16), 2)
    elif gid == "perception":
        pygame.draw.circle(s, light, (11, 11), 3, 1)
        pygame.draw.circle(s, light, (11, 11), 1)
    elif gid == "health":
        pygame.draw.line(s, light, (11, 6), (11, 16), 2)
        pygame.draw.line(s, light, (8, 9), (14, 9), 1)
    else:
        pygame.draw.polygon(s, light, [(11, 6), (15, 11), (11, 16), (7, 11)], 1)
    return s


def make_bg(theme_idx=0):
    th = THEMES[theme_idx % len(THEMES)]
    s = pygame.Surface((LW, LH))
    top, bot = th["top"], th["bot"]
    for y in range(LH):
        t = y / LH
        col = (int(top[0] + (bot[0] - top[0]) * t),
               int(top[1] + (bot[1] - top[1]) * t),
               int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(s, col, (0, y), (LW, y))
    rnd = random.Random(1234 + theme_idx * 977)
    for _ in range(180):
        x, y = rnd.randint(0, LW - 1), rnd.randint(0, LH - 1)
        r = rnd.randint(1, 3)
        d = th["dot"]
        f = rnd.uniform(0.55, 1.35)
        pygame.draw.circle(s, (min(255, int(d[0] * f)), min(255, int(d[1] * f)),
                               min(255, int(d[2] * f))), (x, y), r)
    for _ in range(24):
        x, y = rnd.randint(-40, LW), rnd.randint(0, LH)
        pygame.draw.line(s, th["line"], (x, y),
                         (x + rnd.randint(20, 60), y + rnd.randint(1, 4)), 1)
    deco = th["deco"]
    dcol, ddark, trunk = th["deco_col"], th["deco_dark"], th["trunk"]

    def pine(x, y, sc):
        pygame.draw.rect(s, trunk, (x - 1, y - 3, 2, 4))
        for k in range(3):
            w = (10 - k * 3) * sc
            h = (6 - k) * sc
            ty = y - 4 - k * 4 * sc
            pygame.draw.polygon(s, ddark, [(x, ty - h), (x - w - 1, ty), (x + w + 1, ty)])
            pygame.draw.polygon(s, dcol, [(x, ty - h + 1), (x - w, ty - 1), (x + w, ty - 1)])

    def rock(x, y, sc):
        pygame.draw.ellipse(s, ddark, (x - 7 * sc, y - 5 * sc, 14 * sc, 9 * sc))
        pygame.draw.ellipse(s, dcol, (x - 6 * sc, y - 5 * sc, 12 * sc, 7 * sc))

    def pillar(x, y, sc):
        w = 6 * sc
        h = rnd.randint(12, 22) * sc
        pygame.draw.rect(s, ddark, (x - w // 2 - 1, y - h, w + 2, h))
        pygame.draw.rect(s, dcol, (x - w // 2, y - h + 1, w, h - 1))

    def crystal(x, y, sc):
        w = rnd.choice([3, 4, 5]) * sc
        h = rnd.randint(8, 16) * sc
        pts = [(x, y - h), (x + w, y - h // 2), (x, y), (x - w, y - h // 2)]
        pygame.draw.polygon(s, ddark, pts)
        pts2 = [(x, y - h + 2), (x + w - 2, y - h // 2), (x, y - 2), (x - w + 2, y - h // 2)]
        pygame.draw.polygon(s, dcol, pts2)

    for _ in range(38):
        x = rnd.uniform(6, LW - 6)
        y = rnd.uniform(26, LH - 4)
        sc = rnd.choice([1, 1, 1, 2])
        if deco == "pine":
            pine(x, y, sc)
        elif deco == "rock":
            rock(x, y, sc)
        elif deco == "pillar":
            pillar(x, y, sc)
        else:
            crystal(x, y, sc)
    return s


class Snow:
    def __init__(self, n, smin, smax, vmin, vmax, seed, col_bg=(70, 84, 112),
                 col_fg=(200, 214, 236)):
        r = random.Random(seed)
        self.col_bg = col_bg
        self.col_fg = col_fg
        self.p = [dict(x=r.uniform(0, LW), y=r.uniform(0, LH),
                       s=r.randint(smin, smax), v=r.uniform(vmin, vmax),
                       a=r.uniform(0, 6.28)) for _ in range(n)]

    def update(self, dt):
        for q in self.p:
            q["y"] += q["v"] * dt
            q["x"] += math.sin(q["a"] + q["y"] * 0.05) * 6 * dt
            if q["y"] > LH:
                q["y"] -= LH
            if q["x"] < 0:
                q["x"] += LW
            elif q["x"] > LW:
                q["x"] -= LW

    def draw(self, s, fg=False):
        col = self.col_fg if fg else self.col_bg
        for q in self.p:
            pygame.draw.rect(s, col, (int(q["x"]), int(q["y"]), q["s"], q["s"]))


class WeaponItem:
    """Weapon drop on the ground."""
    def __init__(self, wid, tier, pos):
        self.wid = wid
        self.tier = tier
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(random.uniform(-60, 60), random.uniform(-60, 60))
        self.life = 0.0
        self.bob = random.uniform(0, 6.28)
        self.dead = False


class Player:
    def __init__(self):
        self.pos = pygame.Vector2(LW / 2, LH / 2)
        self.radius = 7
        self.hp = 5
        self.max_hp = 5
        self.speed = 95.0
        self.damage = 1
        self.fire_interval = 0.32
        self.shoot_cd = 0.0
        self.multishot = 1
        self.pierce = 0
        self.bullet_speed = 260.0
        self.magnet = 28.0
        self.coin_mult = 1.0
        self.regen = 0.0
        self.iframe = 0.0
        self.facing = 1
        self.bob = 0.0
        self.walk = 0.0
        self.hero = HEROES[0]
        self.weapon = WEAPONS[0]
        self.weapon_id = "sword"
        self.weapon_tier = 0
        self.dash_time = 0.0
        self.dash_dir = pygame.Vector2(1, 0)
        self.ability_cd = 0.0
        self.ability_max = 1.4
        self.guard_time = 0.0
        self.last_aim = pygame.Vector2(1, 0)
        self.crit_chance = 0.10
        self.crit_mult = 2.0
        self.dev_chance = 0.0
        self.dev_mult = 2.0
        self.rewind_stacks = {u["id"]: 0 for u in REWIND_UPGRADES}
        self.runes = []
        # draft bonuses (per-run)
        self.draft_bonuses = {
            "dmg": 0.0, "rate": 0.0, "hp": 0, "speed": 0.0,
            "crit": 0.0, "dev": 0.0, "pierce": 0, "multi": 0,
            "magnet": 0, "regen": 0.0, "coin": 0.0,
            "crit_mult": 0.0, "dev_mult": 0.0, "cdr": 0.0, "bspeed": 0.0,
        }


class Enemy:
    def __init__(self, kind, pos, wave, diff=None):
        d = diff or DIFFICULTIES[1]
        base = ENEMY_TYPES[kind]
        self.kind = kind
        self.pos = pygame.Vector2(pos)
        self.radius = base["radius"]
        self.hp = max(1, round(base["hp"] * (1 + 0.18 * (wave - 1)) * d["hp"]))
        self.max_hp = self.hp
        self.speed = base["speed"] * (1 + 0.03 * (wave - 1))
        self.dmg = base["dmg"] * d["dmg"]
        self.reward = max(1, round(base["reward"] * d["coin"]))
        self.flash = 0.0
        self.phase = random.uniform(0, 6.28)
        self.wob = random.uniform(0.5, 1.5)
        self.is_boss = (kind == "boss")
        self.boss_type = None
        self.enraged = False
        self.spin = 0.0
        self.atk = random.uniform(1.2, 2.2) if kind == "spitter" else 1.6
        self.atk2 = 3.2
        self.summon = 5.0
        self.freeze = 0.0
        self.squash = 1.0


class Bullet:
    def __init__(self, pos, vel, damage, pierce, kind="shot", explode=0,
                 freeze=0.0, life=None, color=(120, 220, 255)):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.damage = damage
        self.pierce = pierce
        self.kind = kind
        self.explode = explode
        self.freeze = freeze
        self.color = color
        self.radius = 2
        self.dead = False
        self.age = 0.0
        self.life = life
        self.returning = False
        self.spin = 0.0
        self.hits = set()
        self.trail = []


class EBullet:
    def __init__(self, pos, vel, dmg=1, radius=3, color=(140, 220, 255)):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.dmg = dmg
        self.radius = radius
        self.color = color
        self.dead = False


class Coin:
    def __init__(self, pos, value):
        self.pos = pygame.Vector2(pos)
        ang = random.uniform(0, 6.28)
        spd = random.uniform(40, 120)
        self.vel = pygame.Vector2(math.cos(ang) * spd, math.sin(ang) * spd)
        self.value = value
        self.life = 0.0


class Particle:
    def __init__(self, pos, vel, color, life, size):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size


class FloatText:
    def __init__(self, pos, s, color, size=8, vy=-34, life=0.55):
        self.pos = pygame.Vector2(pos)
        self.s = s
        self.color = color
        self.size = size
        self.vy = vy
        self.life = life
        self.max_life = life


class Game:
    def __init__(self):
        pygame.display.set_caption("Guinea Arena")
        self.render = pygame.Surface((LW, LH))
        self.clock = pygame.time.Clock()
        self.running = True
        self.time = 0.0
        self.flash = 0.0
        self.flash_col = (255, 255, 255)
        self.fullscreen = not ("--selftest" in sys.argv or "--windowed" in sys.argv)
        self.screen = None
        self.set_display(self.fullscreen)
        self.ui_text = []
        self.world_text = []
        self.sfx = Sfx()
        self.sfx.build()

        self.spr_hero = {}
        for h in HEROES:
            img = make_guinea(h["fur"], h["fur2"], h["ear"], h["blaze"], h["eye"], h.get("outline"))
            self.spr_hero[h["id"]] = (img, pygame.transform.flip(img, True, False))
        self.spr_weapon = {w["id"]: make_weapon_icon(w["id"]) for w in WEAPONS}
        self.spr_enemy = {k: make_enemy(k, v["color"], v["outline"], v["radius"])
                          for k, v in ENEMY_TYPES.items() if k != "boss"}
        self.spr_boss = {k: make_boss(v["color"], v["outline"], v["eye"], ENEMY_TYPES["boss"]["radius"])
                         for k, v in BOSS_CFG.items()}
        self.spr_coin_frames = make_coin_frames()
        self.spr_bullet = make_bullet()
        self.spr_acc = {a["id"]: make_acc_icon(a) for a in ACCESSORIES}
        self.spr_rune = {rt["id"]: make_rune_icon(rt) for rt in RUNE_TYPES}
        self.theme_idx = 0
        th = THEMES[0]
        self.bg = make_bg(0)
        self.snow_bg = Snow(90, 1, 1, 14, 40, 11, (70, 84, 112), th["snow"])
        self.snow_fg = Snow(26, 1, 2, 40, 90, 22, (70, 84, 112), th["snow"])

        self.hero_id, self.diff_id, self.best = self.load_save()
        self.hero_idx = next((i for i, h in enumerate(HEROES) if h["id"] == self.hero_id), 0)
        self.hero = HEROES[self.hero_idx]
        self.diff_idx = next((i for i, d in enumerate(DIFFICULTIES) if d["id"] == self.diff_id), 1)
        self.diff = DIFFICULTIES[self.diff_idx]
        self.state = "MENU"
        self.msg = ""
        self.msg_t = 0.0
        self.shake = 0.0
        self.prev_dash = False
        self.texts = []
        self.music_on = True
        self.music_channel = None
        self.build_music()
        self.rewind_elixir_total = 0
        _elixir, _stacks, _runes = self.load_meta()
        self.rewind_elixir_total = _elixir
        self.reset_run()
        for uid, val in _stacks.items():
            if uid in self.player.rewind_stacks:
                self.player.rewind_stacks[uid] = val
        self.player.runes = list(_runes)

    def set_display(self, fullscreen):
        self.fullscreen = fullscreen
        try:
            if fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            self.fullscreen = False
            self.screen = None
        if self.screen is None or not self.fullscreen:
            self.fullscreen = False
            self.screen = pygame.display.set_mode((WW, WH))
        sw, sh = self.screen.get_size()
        self.scale = max(1, min(sw // LW, sh // LH))
        self.off_x = (sw - LW * self.scale) // 2
        self.off_y = (sh - LH * self.scale) // 2

    def toggle_fullscreen(self):
        self.set_display(not self.fullscreen)

    def mouse_logical(self):
        mx, my = pygame.mouse.get_pos()
        return ((mx - self.off_x) / self.scale, (my - self.off_y) / self.scale)

    def tx(self, s, pos, size, color, center=False, bold=False, shadow=True):
        self.ui_text.append((s, pos[0], pos[1], size, color, center, bold, shadow))

    def load_save(self):
        hero, diff, best = "snow", "normal", 0
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            best = int(d.get("best_wave", 0))
            hid = d.get("hero", "snow")
            if any(h["id"] == hid for h in HEROES):
                hero = hid
            did = d.get("difficulty", "normal")
            if any(x["id"] == did for x in DIFFICULTIES):
                diff = did
        except Exception:
            pass
        return hero, diff, best

    def load_meta(self):
        elixir, stacks, runes = 0, {}, []
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            elixir = int(d.get("rewind_elixir", 0))
            raw_stacks = d.get("rewind_stacks", {})
            for u in REWIND_UPGRADES:
                if u["id"] in raw_stacks:
                    stacks[u["id"]] = int(raw_stacks[u["id"]])
            raw_runes = d.get("runes", [])
            if isinstance(raw_runes, list):
                for r in raw_runes:
                    if isinstance(r, dict) and "id" in r and "level" in r:
                        runes.append(dict(id=str(r["id"]), level=int(r["level"])))
        except Exception:
            pass
        return elixir, stacks, runes

    def save_progress(self):
        try:
            with open(SAVE_PATH, "w", encoding="utf-8") as fh:
                json.dump({
                    "best_wave": self.best,
                    "hero": self.hero_id,
                    "difficulty": self.diff_id,
                    "rewind_elixir": self.rewind_elixir_total,
                    "rewind_stacks": self.player.rewind_stacks,
                    "runes": self.player.runes,
                }, fh)
        except Exception:
            pass

    def build_music(self):
        try:
            import numpy as np
            if not self.sfx.ok:
                self.music = None
                self.music_channel = None
                self.music_on = False
                return
            sr = 44100
            chords = [(220.00, 261.63, 329.63), (174.61, 220.00, 261.63),
                      (261.63, 329.63, 392.00), (196.00, 246.94, 293.66)]
            seg = 3.2
            total = int(sr * seg * len(chords))
            buf = np.zeros(total, np.float32)
            for ci, ch in enumerate(chords):
                start = int(sr * seg * ci)
                n = int(sr * seg)
                t = np.arange(n) / sr
                env = np.minimum(1, t / 0.55) * np.minimum(1, (seg - t) / 0.7)
                pad = np.zeros(n, np.float32)
                for f in ch:
                    pad += np.sin(2 * np.pi * f * t) * 0.32
                    pad += np.sin(2 * np.pi * f * 1.004 * t) * 0.18
                    pad += np.sin(2 * np.pi * f * 0.5 * t) * 0.10
                buf[start:start + n] += pad * env * 0.42
            k = 7
            buf = np.convolve(buf, np.ones(k) / k, mode="same")
            peak = float(np.max(np.abs(buf))) + 1e-6
            buf = (buf / peak * 0.55 * 32767).astype(np.int16)
            self.music = self.sfx._to_sound(buf)
            self.music_channel = self.music.play(loops=-1)
            if self.music_channel:
                self.music_channel.set_volume(0.85)
            self.music_on = self.music_channel is not None
        except Exception:
            self.music = None
            self.music_channel = None
            self.music_on = False

    def toggle_music(self):
        if not self.music_channel:
            return
        self.music_on = not self.music_on
        self.music_channel.set_volume(0.85 if self.music_on else 0.0)

    def reset_run(self):
        old = getattr(self, "player", None)
        self.wave = 0
        self.coins = 0
        self.up = {u["id"]: 0 for u in UPGRADES}
        self.player = Player()
        if old is not None:
            self.player.rewind_stacks = dict(old.rewind_stacks)
            self.player.runes = list(old.runes)
        self.enemies = []
        self.bullets = []
        self.ebullets = []
        self.coin_list = []
        self.weapon_items = []
        self.particles = []
        self.texts = []
        self.prev_dash = False
        self.to_spawn = 0
        self.spawn_interval = 0.8
        self.spawn_timer = 0.0
        self.acc = []
        self.loot_choices = []
        self.loot_pending = False
        self.draft_choices = []
        self.theme_idx = -1
        self.state = "MENU"
        self.flash = 0.0

    def acc_bonus(self):
        keys = ("dmg", "rate", "speed", "hp", "coin", "magnet", "regen", "pierce", "multi", "cdr")
        b = {k: 0 for k in keys}
        for a in self.acc:
            for k in keys:
                b[k] += a.get(k, 0)
        return b

    def apply_upgrades(self):
        u = self.up
        p = self.player
        h = self.hero
        w = WEAPONS_DICT.get(p.weapon_id, WEAPONS[0])
        p.weapon = w
        b = self.acc_bonus()
        rw = p.rewind_stacks
        dr = p.draft_bonuses
        p.hero = h

        tier_info = WEAPON_TIERS[p.weapon_tier]
        wt_dmg = tier_info["dmg_mul"]
        wt_rate = tier_info["rate_mul"]

        p.damage = ((1 + u["dmg"]) * h["dmg"] * w["dmg"] * (1 + b["dmg"])
                    * wt_dmg * (1 + dr["dmg"]))
        p.fire_interval = ((0.32 / h["rate"] / w["rate"]) / (1 + 0.16 * u["rate"])
                           / (1 + b["rate"]) / (1 + dr["rate"])) / wt_rate
        p.speed = 95.0 * h["speed"] * (1 + 0.08 * u["speed"]) * (1 + b["speed"]) * (1 + dr["speed"])
        oldmax = p.max_hp
        newmax = h["hp"] + u["hp"] + b["hp"] + dr["hp"]
        p.max_hp = newmax
        if newmax > oldmax:
            p.hp = min(newmax, p.hp + (newmax - oldmax))
        p.multishot = 1 + u["multi"] + b["multi"] + dr["multi"]
        p.pierce = u["pierce"] + b["pierce"] + dr["pierce"]
        p.magnet = 28 + 18 * u["magnet"] + b["magnet"] + dr["magnet"]
        p.coin_mult = (1 + 0.2 * u["coin"]) * (1 + b["coin"]) * (1 + dr["coin"])
        p.regen = 0.25 * u["regen"] + b["regen"] + dr["regen"]
        p.bullet_speed = 260.0 * w["spd"] * (1 + 0.12 * u["bspeed"]) * (1 + dr["bspeed"])
        p.ability_max = h["acd"] * (1 - min(0.6, b["cdr"] + dr["cdr"]))

        # rewind
        p.damage *= (1 + 0.10 * rw.get("rw_dmg", 0))
        hp_bonus = rw.get("rw_hp", 0)
        if hp_bonus:
            p.max_hp += hp_bonus
            p.hp = min(p.max_hp, p.hp + hp_bonus)
        p.speed *= (1 + 0.04 * rw.get("rw_speed", 0))

        # crit/dev
        p.crit_chance = (0.10 + 0.02 * rw.get("rw_crit", 0)
                         + dr["crit"])
        p.crit_mult = 2.0 + dr["crit_mult"]
        p.dev_chance = (0.00 + 0.05 * rw.get("rw_dev", 0)
                        + dr["dev"])
        p.dev_mult = 2.0 + dr["dev_mult"]

        # runes
        for r in p.runes:
            rt = next((t for t in RUNE_TYPES if t["id"] == r.get("id")), None)
            if not rt:
                continue
            lvl = max(1, int(r.get("level", 1)))
            bonus = rt["base"] + rt["per_lvl"] * (lvl - 1)
            if rt["stat"] == "dmg":
                p.damage *= (1 + bonus)
            elif rt["stat"] == "crit":
                p.crit_chance += bonus
            elif rt["stat"] == "dev":
                p.dev_chance += bonus
            elif rt["stat"] == "hp":
                hb = int(bonus)
                p.max_hp += hb
                p.hp = min(p.max_hp, p.hp + hb)

        # stars
        stars = rw.get("rw_star", 0)
        if stars:
            mult = 1 + ASCENSION_BONUS * stars
            p.damage *= mult
            p.max_hp = int(p.max_hp * mult)
            p.hp = min(p.max_hp, p.hp + int(p.max_hp * (mult - 1)))

    def start_new_game(self):
        self.hero = HEROES[self.hero_idx]
        self.hero_id = self.hero["id"]
        self.diff = DIFFICULTIES[self.diff_idx]
        self.diff_id = self.diff["id"]
        self.reset_run()
        self.wave = 0
        # starting weapon
        self.player.weapon_id = "sword"
        self.player.weapon_tier = 0
        self.apply_upgrades()
        self.player.hp = self.player.max_hp
        self.save_progress()
        self.start_wave(1)

    def start_wave(self, w):
        self.wave = w
        self.spawn_interval = max(0.28, 0.85 - w * 0.03)
        self.spawn_timer = 0.35
        self.enemies.clear()
        self.bullets.clear()
        self.ebullets.clear()
        self.coin_list.clear()
        self.weapon_items.clear()
        self.particles.clear()
        self.texts.clear()
        self.player.pos = pygame.Vector2(LW / 2, LH / 2)
        self.player.hp = min(self.player.max_hp, self.player.hp + 1)
        self.player.iframe = 1.2
        self.state = "PLAY"

        ti = ((w - 1) // 5) % len(THEMES)
        if ti != self.theme_idx:
            self.theme_idx = ti
            th = THEMES[ti]
            self.bg = make_bg(ti)
            self.snow_bg.col_fg = th["snow"]
            self.snow_bg.col_bg = tuple(int(c * 0.55) for c in th["snow"])
            self.snow_fg.col_fg = th["snow"]
            self.snow_fg.col_bg = tuple(int(c * 0.55) for c in th["snow"])
        theme_name = THEMES[ti]["name"]

        if w % 5 == 0:
            btype = BOSS_ORDER[((w // 5) - 1) % len(BOSS_ORDER)]
            boss = Enemy("boss", (LW / 2, -34), w, self.diff)
            boss.boss_type = btype
            boss.hp = boss.max_hp = round((50 + w * 10) * self.diff["hp"])
            boss.speed = 28 + w * 0.8
            self.enemies.append(boss)
            self.to_spawn = max(1, round((2 + w // 5) * self.diff["spawn"]))
            self.msg = "БОСС · %s" % BOSS_CFG[btype]["name"]
        else:
            self.to_spawn = max(1, round((4 + w * 2) * self.diff["spawn"]))
            self.msg = "ВОЛНА %d · %s" % (w, theme_name)
        self.msg_t = 1.9
        self.sfx.play("wave")

    def spawn_enemy(self):
        w = self.wave
        r = random.random()
        if w >= 5 and r < 0.13:
            kind = "brute"
        elif w >= 4 and r < 0.30:
            kind = "spitter"
        elif w >= 3 and r < 0.62:
            kind = "ice"
        else:
            kind = "snow"
        side = random.randint(0, 3)
        if side == 0:
            pos = (random.uniform(0, LW), -12)
        elif side == 1:
            pos = (random.uniform(0, LW), LH + 12)
        elif side == 2:
            pos = (-12, random.uniform(0, LH))
        else:
            pos = (LW + 12, random.uniform(0, LH))
        self.enemies.append(Enemy(kind, pos, w, self.diff))

    def cost(self, u):
        return int(round(u["base"] * (u["mult"] ** self.up[u["id"]])))

    def buy(self, i):
        if i < 0 or i >= len(UPGRADES):
            return False
        u = UPGRADES[i]
        if self.up[u["id"]] >= u["max"]:
            return False
        c = self.cost(u)
        if self.coins < c:
            return False
        self.coins -= c
        self.up[u["id"]] += 1
        self.apply_upgrades()
        self.sfx.play("buy")
        self.msg = "КУПЛЕНО: %s" % u["name"]
        self.msg_t = 1.0
        return True

    def wave_complete(self):
        self.coins += round((3 + self.wave * 2) * self.diff["coin"])
        self.sfx.play("wave")
        if self.loot_pending:
            self.loot_pending = False
            self.roll_loot()
            self.state = "LOOT"
        else:
            self.roll_draft()
            self.state = "DRAFT"

    def roll_loot(self):
        self.loot_choices = []
        pool = list(ACCESSORIES)
        for _ in range(3):
            r = random.random()
            rar = "common" if r < 0.55 else "epic" if r < 0.87 else "legendary"
            cands = [a for a in pool if a["rarity"] == rar and a not in self.loot_choices]
            if not cands:
                cands = [a for a in pool if a not in self.loot_choices]
            self.loot_choices.append(random.choice(cands))

    def take_loot(self, i):
        if 0 <= i < len(self.loot_choices):
            a = self.loot_choices[i]
            self.acc.append(a)
            self.apply_upgrades()
            self.sfx.play("buy")
        self.loot_choices = []
        self.roll_draft()
        self.state = "DRAFT"

    def roll_draft(self):
        pool = list(DRAFT_POOL)
        total_w = sum(d["weight"] for d in pool)
        picks = []
        used_ids = set()
        for _ in range(3):
            attempts = 0
            while attempts < 50:
                r = random.uniform(0, total_w)
                accum = 0
                for d in pool:
                    accum += d["weight"]
                    if r <= accum and d["id"] not in used_ids:
                        picks.append(d)
                        used_ids.add(d["id"])
                        break
                attempts += 1
                if len(picks) > _:
                    break
        while len(picks) < 3:
            picks.append(random.choice(DRAFT_POOL))
        self.draft_choices = picks[:3]

    def apply_draft(self, i):
        if 0 <= i < len(self.draft_choices):
            d = self.draft_choices[i]
            b = self.player.draft_bonuses
            stat = d["stat"]
            val = d["val"]
            if stat in ("hp", "pierce", "multi", "magnet"):
                b[stat] += int(val)
            else:
                b[stat] += float(val)
            self.apply_upgrades()
            self.sfx.play("buy")
            self.msg = d["name"]
            self.msg_t = 1.2
        self.draft_choices = []
        self.state = "SHOP"

    # ----- weapon drops -----
    def drop_weapon(self, pos, tier, wid=None):
        if wid is None:
            wid = random.choice([w["id"] for w in WEAPONS])
        item = WeaponItem(wid, tier, pos)
        self.weapon_items.append(item)
        return item

    def pickup_weapon(self, item):
        wid = item.wid
        drop_tier = item.tier
        p = self.player
        # merge or switch
        if wid == p.weapon_id:
            new_tier = max(p.weapon_tier + 1, drop_tier)
            new_tier = min(new_tier, WEAPON_TIER_MAX)
            if new_tier > p.weapon_tier:
                p.weapon_tier = new_tier
                info = WEAPON_TIERS[p.weapon_tier]
                self.msg = "МЕРДЖ! %s · %s" % (WEAPONS_DICT[wid]["name"], info["name"])
                self.msg_t = 1.6
                self.add_shake(3)
                self.flash = 0.3
                self.flash_col = info["color"]
                self.burst(p.pos, 22, info["color"], 160, 0.6, 2)
            else:
                self.msg = "УЖЕ МАКС"
                self.msg_t = 1.0
        else:
            p.weapon_id = wid
            p.weapon_tier = drop_tier
            info = WEAPON_TIERS[p.weapon_tier]
            self.msg = "НОВОЕ ОРУЖИЕ: %s · %s" % (WEAPONS_DICT[wid]["name"], info["name"])
            self.msg_t = 1.6
            self.flash = 0.25
            self.flash_col = info["color"]
            self.burst(p.pos, 18, info["color"], 140, 0.5, 2)
        self.apply_upgrades()
        self.sfx.play("drop")

    def burst(self, pos, n, color, speed=80, life=0.45, size=2):
        for _ in range(n):
            ang = random.uniform(0, 6.28)
            spd = random.uniform(speed * 0.3, speed)
            self.particles.append(Particle(pos, (math.cos(ang) * spd, math.sin(ang) * spd),
                                           color, life, size))

    def add_shake(self, amt):
        self.shake = min(6, self.shake + amt)

    def hurt_player(self, dmg):
        p = self.player
        if p.guard_time > 0:
            dmg = dmg * 0.5
        p.hp -= dmg
        self.sfx.play("hurt")
        self.flash = 0.35
        self.flash_col = (255, 50, 80)
        if p.hp <= 0:
            self.player_die()
            return True
        return False

    def explode(self, pos, dmg, radius):
        self.burst(pos, 26, (255, 180, 90), 190, 0.6, 2)
        self.burst(pos, 12, C_GOLD, 100, 0.5, 1)
        self.add_shake(4)
        self.sfx.play("hit")
        hit = max(1, int(round(dmg)))
        for e in list(self.enemies):
            if e.hp > 0 and e.pos.distance_to(pos) < radius + e.radius:
                e.hp -= hit
                e.flash = 0.15
                e.squash = 1.35
                self.texts.append(FloatText((e.pos.x, e.pos.y - e.radius), str(hit),
                                            (255, 200, 130), 9, -40, 0.5))
                if e.hp <= 0:
                    self.kill_enemy(e)
        self.enemies = [e for e in self.enemies if e.hp > 0]

    def hero_cards(self):
        cw, ch, gap = 72, 190, 6
        total = len(HEROES) * cw + (len(HEROES) - 1) * gap
        x0 = (LW - total) // 2
        y0 = 46
        return [pygame.Rect(x0 + i * (cw + gap), y0, cw, ch) for i in range(len(HEROES))]

    def difficulty_cards(self):
        cw, ch, gap = 92, 126, 8
        total = len(DIFFICULTIES) * cw + (len(DIFFICULTIES) - 1) * gap
        x0 = (LW - total) // 2
        y0 = 64
        return [pygame.Rect(x0 + i * (cw + gap), y0, cw, ch)
                for i in range(len(DIFFICULTIES))]

    def loot_cards(self):
        n = len(self.loot_choices)
        if n == 0:
            return []
        cw, ch, gap = 116, 152, 10
        total = n * cw + max(0, n - 1) * gap
        x0 = (LW - total) // 2
        y0 = 52
        return [pygame.Rect(x0 + i * (cw + gap), y0, cw, ch) for i in range(n)]

    def draft_cards(self):
        n = len(self.draft_choices)
        if n == 0:
            return []
        cw, ch, gap = 128, 152, 10
        total = n * cw + max(0, n - 1) * gap
        x0 = (LW - total) // 2
        y0 = 60
        return [pygame.Rect(x0 + i * (cw + gap), y0, cw, ch) for i in range(n)]

    def handle_event(self, e):
        if e.type == pygame.QUIT:
            self.running = False
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx = (e.pos[0] - self.off_x) / self.scale
            my = (e.pos[1] - self.off_y) / self.scale
            if self.state == "SELECT":
                for i, rect in enumerate(self.hero_cards()):
                    if rect.collidepoint(mx, my):
                        if i == self.hero_idx:
                            self.state = "DIFFICULTY"
                        else:
                            self.hero_idx = i
                            self.hero = HEROES[i]
                        return
            elif self.state == "DIFFICULTY":
                for i, rect in enumerate(self.difficulty_cards()):
                    if rect.collidepoint(mx, my):
                        if i == self.diff_idx:
                            self.start_new_game()
                        else:
                            self.diff_idx = i
                            self.diff = DIFFICULTIES[i]
                            self.diff_id = self.diff["id"]
                        return
            elif self.state == "LOOT":
                for i, rect in enumerate(self.loot_cards()):
                    if rect.collidepoint(mx, my):
                        self.take_loot(i)
                        return
            elif self.state == "DRAFT":
                for i, rect in enumerate(self.draft_cards()):
                    if rect.collidepoint(mx, my):
                        self.apply_draft(i)
                        return
        if e.type != pygame.KEYDOWN:
            return
        k = e.key
        if k == pygame.K_F11 or (k == pygame.K_RETURN and (e.mod & pygame.KMOD_ALT)):
            self.toggle_fullscreen()
            return
        if k == pygame.K_m:
            self.toggle_music()
            return
        st = self.state
        if st == "MENU":
            if k in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = "SELECT"
            elif k == pygame.K_w:
                self.state = "REWIND"
            elif k == pygame.K_ESCAPE:
                self.running = False
        elif st == "SELECT":
            if k in (pygame.K_LEFT, pygame.K_a):
                self.hero_idx = (self.hero_idx - 1) % len(HEROES)
                self.hero = HEROES[self.hero_idx]
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.hero_idx = (self.hero_idx + 1) % len(HEROES)
                self.hero = HEROES[self.hero_idx]
            elif pygame.K_1 <= k <= pygame.K_6:
                self.hero_idx = k - pygame.K_1
                self.hero = HEROES[self.hero_idx]
            elif k in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = "DIFFICULTY"
            elif k == pygame.K_ESCAPE:
                self.state = "MENU"
        elif st == "DIFFICULTY":
            if k in (pygame.K_LEFT, pygame.K_a):
                self.diff_idx = (self.diff_idx - 1) % len(DIFFICULTIES)
                self.diff = DIFFICULTIES[self.diff_idx]
                self.diff_id = self.diff["id"]
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.diff_idx = (self.diff_idx + 1) % len(DIFFICULTIES)
                self.diff = DIFFICULTIES[self.diff_idx]
                self.diff_id = self.diff["id"]
            elif pygame.K_1 <= k <= pygame.K_4:
                self.diff_idx = k - pygame.K_1
                self.diff = DIFFICULTIES[self.diff_idx]
                self.diff_id = self.diff["id"]
            elif k in (pygame.K_SPACE, pygame.K_RETURN):
                self.start_new_game()
            elif k == pygame.K_ESCAPE:
                self.state = "SELECT"
        elif st == "PLAY":
            if k == pygame.K_ESCAPE:
                self.state = "PAUSE"
        elif st == "PAUSE":
            if k == pygame.K_ESCAPE:
                self.state = "PLAY"
        elif st == "LOOT":
            if pygame.K_1 <= k <= pygame.K_3:
                self.take_loot(k - pygame.K_1)
        elif st == "DRAFT":
            if pygame.K_1 <= k <= pygame.K_3:
                self.apply_draft(k - pygame.K_1)
        elif st == "SHOP":
            idx = None
            if pygame.K_1 <= k <= pygame.K_9:
                idx = k - pygame.K_1
            elif k == pygame.K_0:
                idx = 9
            if idx is not None:
                self.buy(idx)
            elif k in (pygame.K_SPACE, pygame.K_RETURN):
                self.start_wave(self.wave + 1)
        elif st == "REWIND":
            if pygame.K_1 <= k <= pygame.K_6:
                self.buy_rewind_upgrade(k - pygame.K_1)
            elif k in (pygame.K_SPACE, pygame.K_RETURN):
                self.do_rewind()
            elif k == pygame.K_ESCAPE:
                self.state = "MENU"
        elif st == "DEAD":
            if k == pygame.K_r:
                self.start_new_game()
            elif k == pygame.K_t:
                self.state = "REWIND"
            elif k in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = "SELECT"
            elif k == pygame.K_ESCAPE:
                self.state = "MENU"

    def rewind_elixir(self):
        return REWIND_ELIXIR_BASE + REWIND_ELIXIR_PER_WAVE * self.wave

    def rewind_cost(self, u):
        cur = self.player.rewind_stacks.get(u["id"], 0)
        return int(round(u["base"] * (u["mult"] ** cur)))

    def buy_rewind_upgrade(self, i):
        if i < 0 or i >= len(REWIND_UPGRADES):
            return
        u = REWIND_UPGRADES[i]
        cur = self.player.rewind_stacks.get(u["id"], 0)
        if cur >= u["max"]:
            return
        c = self.rewind_cost(u)
        if self.rewind_elixir_total < c:
            return
        self.rewind_elixir_total -= c
        self.player.rewind_stacks[u["id"]] = cur + 1
        self.apply_upgrades()
        self.sfx.play("buy")
        self.save_progress()

    def do_rewind(self):
        gained = self.rewind_elixir()
        self.rewind_elixir_total += gained
        self.best = max(self.best, self.wave)
        self.save_progress()
        self.reset_run()
        self.apply_upgrades()
        self.msg = "+%d ЭЛИКСИРА" % gained
        self.msg_t = 2.0
        self.state = "MENU"
        self.sfx.play("wave")

    def update(self, dt):
        self.time += dt
        self.snow_bg.update(dt)
        self.snow_fg.update(dt)
        if self.msg_t > 0:
            self.msg_t -= dt
        if self.shake > 0:
            self.shake = max(0, self.shake - dt * 18)
        if self.flash > 0:
            self.flash = max(0, self.flash - dt * 1.5)
        if self.state == "PLAY":
            self.update_play(dt)

    def update_play(self, dt):
        p = self.player
        if p.iframe > 0:
            p.iframe -= dt
        if p.regen > 0 and p.hp > 0:
            p.hp = min(p.max_hp, p.hp + p.regen * dt)

        keys = pygame.key.get_pressed()
        mv = pygame.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mv.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mv.x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            mv.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            mv.y += 1
        if mv.length_squared() > 0:
            mv = mv.normalize()
            p.pos += mv * p.speed * dt
            if mv.x != 0:
                p.facing = 1 if mv.x > 0 else -1
            p.walk += dt * 12
        else:
            p.walk *= 0.9
        p.pos.x = clamp(p.pos.x, p.radius, LW - p.radius)
        p.pos.y = clamp(p.pos.y, p.radius, LH - p.radius)

        mx, my = self.mouse_logical()
        aim = pygame.Vector2(mx, my)
        dirv = aim - p.pos
        if dirv.length_squared() < 1:
            dirv = pygame.Vector2(1, 0)
        dirv = dirv.normalize()

        ability_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if p.ability_cd > 0:
            p.ability_cd -= dt
        if p.guard_time > 0:
            p.guard_time -= dt
        if ability_held and not self.prev_dash and p.ability_cd <= 0 and p.dash_time <= 0:
            self.use_ability(p, mv, dirv, aim)
        self.prev_dash = ability_held
        if p.dash_time > 0:
            p.dash_time -= dt
            p.pos += p.dash_dir * 430 * dt
            p.iframe = max(p.iframe, 0.06)
            self.particles.append(Particle(p.pos.copy(), (0, 0), C_ACCENT, 0.22, 2))
            p.pos.x = clamp(p.pos.x, p.radius, LW - p.radius)
            p.pos.y = clamp(p.pos.y, p.radius, LH - p.radius)

        if p.shoot_cd > 0:
            p.shoot_cd -= dt
        if pygame.mouse.get_pressed()[0] and p.shoot_cd <= 0:
            p.shoot_cd = p.fire_interval
            self.shoot(p, dirv)

        for b in self.bullets:
            b.age += dt
            b.trail.append((b.pos.x, b.pos.y))
            if len(b.trail) > 6:
                b.trail.pop(0)
            if b.kind == "hammer":
                b.spin += dt * 26
                if b.age > 0.5:
                    b.returning = True
                if b.returning:
                    to = p.pos - b.pos
                    if to.length_squared() > 1:
                        b.vel = to.normalize() * max(220, p.bullet_speed * 0.95)
                    if b.pos.distance_to(p.pos) < p.radius + 6 and b.age > 0.62:
                        b.dead = True
            b.pos += b.vel * dt
            if b.pos.x < -14 or b.pos.x > LW + 14 or b.pos.y < -14 or b.pos.y > LH + 14:
                if b.explode:
                    self.explode(b.pos, b.damage, b.explode)
                b.dead = True
        self.bullets = [b for b in self.bullets if not b.dead]

        new_minions = []
        for e in self.enemies:
            if e.flash > 0:
                e.flash -= dt
            if e.freeze > 0:
                e.freeze -= dt
                continue
            d = p.pos - e.pos
            if e.is_boss:
                self.update_boss(e, d, dt, new_minions)
            elif e.kind == "spitter":
                dd = d.length()
                if dd > 1:
                    dirn = d.normalize()
                    if dd > 135:
                        e.pos += dirn * e.speed * dt
                    elif dd < 85:
                        e.pos -= dirn * e.speed * dt
                    else:
                        perp = pygame.Vector2(-dirn.y, dirn.x) * e.wob
                        e.pos += perp * e.speed * 0.6 * dt
                e.atk -= dt
                if e.atk <= 0 and dd < 210:
                    e.atk = 2.2
                    dirn = d.normalize() if d.length_squared() > 1 else pygame.Vector2(1, 0)
                    self.ebullets.append(EBullet(e.pos, dirn * 115, 1, 3, (200, 180, 255)))
                    self.sfx.play("hit")
            else:
                if d.length_squared() > 1:
                    d = d.normalize()
                    perp = pygame.Vector2(-d.y, d.x)
                    wob = math.sin(self.time * 3 + e.phase) * e.wob
                    e.pos += (d + perp * wob * 0.25) * e.speed * dt
            if e.pos.distance_to(p.pos) < e.radius + p.radius:
                if p.iframe <= 0:
                    if self.hurt_player(e.dmg):
                        return
                    p.iframe = 0.9
                    self.add_shake(7 if e.is_boss else 5)
                    self.burst(p.pos, 8, C_RED, 90, 0.4, 2)
        self.enemies.extend(new_minions)

        for b in self.ebullets:
            b.pos += b.vel * dt
            if b.pos.x < -8 or b.pos.x > LW + 8 or b.pos.y < -8 or b.pos.y > LH + 8:
                b.dead = True
                continue
            if b.pos.distance_to(p.pos) < b.radius + p.radius:
                b.dead = True
                if p.iframe <= 0:
                    if self.hurt_player(b.dmg):
                        return
                    p.iframe = 0.8
                    self.add_shake(4)
                    self.burst(p.pos, 6, C_RED, 80, 0.35, 2)
        self.ebullets = [b for b in self.ebullets if not b.dead]

        for b in self.bullets:
            if b.dead:
                continue
            for e in self.enemies:
                if e.hp <= 0:
                    continue
                if b.kind == "hammer" and id(e) in b.hits:
                    continue
                if b.pos.distance_to(e.pos) <= e.radius + b.radius:
                    if b.explode:
                        self.explode(b.pos, b.damage, b.explode)
                        b.dead = True
                        break
                    dmg = b.damage
                    is_crit = random.random() < p.crit_chance
                    dev_hit = False
                    if is_crit:
                        dmg *= p.crit_mult
                        if random.random() < p.dev_chance:
                            dmg *= p.dev_mult
                            dev_hit = True
                    dmg_int = max(1, int(round(dmg)))
                    e.hp -= dmg_int
                    e.flash = 0.12
                    e.squash = 1.3
                    if b.freeze > 0:
                        e.freeze = max(e.freeze, b.freeze)
                        self.burst(e.pos, 5, (190, 235, 255), 60, 0.3, 1)
                    if b.kind == "hammer":
                        b.hits.add(id(e))
                        self.add_shake(2)
                    self.sfx.play("hit")
                    self.burst(b.pos, 4, C_SNOW, 70, 0.25, 1)
                    if is_crit:
                        self.burst(e.pos, 5, (255, 220, 100), 100, 0.3, 2)
                    if dev_hit:
                        self.texts.append(FloatText((e.pos.x, e.pos.y - e.radius - 10),
                                                    "DEV!", (255, 100, 255), 12, -60, 0.8))
                        self.burst(e.pos, 10, (255, 100, 255), 150, 0.4, 2)
                        self.add_shake(3)
                    dmg_col = (255, 230, 100) if is_crit else (255, 240, 180)
                    dmg_size = 10 if is_crit else 9
                    self.texts.append(FloatText((e.pos.x, e.pos.y - e.radius), str(dmg_int),
                                                dmg_col, dmg_size, -40, 0.45))
                    if e.hp <= 0:
                        self.kill_enemy(e)
                    if b.kind != "hammer":
                        if b.pierce > 0:
                            b.pierce -= 1
                        else:
                            b.dead = True
                            break
        self.bullets = [b for b in self.bullets if not b.dead]
        self.enemies = [e for e in self.enemies if e.hp > 0]

        # magnet coins
        ppos = p.pos
        for c in self.coin_list:
            c.life += dt
            to = ppos - c.pos
            dist = to.length()
            if dist < p.magnet and dist > 0.1:
                spd = min(1200.0, 360.0 + (p.magnet - dist) * 6.0)
                c.vel = to.normalize() * spd
            else:
                c.vel *= (1 - min(1, 4 * dt))
            c.pos += c.vel * dt
            if c.pos.distance_to(ppos) < p.radius + 5:
                gain = max(1, int(round(c.value * p.coin_mult)))
                self.coins += gain
                c.value = 0
                self.sfx.play("coin")
                self.burst(c.pos, 3, C_GOLD, 50, 0.25, 1)
                self.texts.append(FloatText(c.pos, "+%d" % gain, C_GOLD, 8, -30, 0.5))
            c.pos.x = clamp(c.pos.x, -10, LW + 10)
            c.pos.y = clamp(c.pos.y, -10, LH + 10)
        self.coin_list = [c for c in self.coin_list if c.value > 0]

        # weapon items on ground — pull toward player
        for it in self.weapon_items:
            it.life += dt
            to = ppos - it.pos
            dist = to.length()
            if dist < 80 and dist > 0.1:
                it.vel += to.normalize() * 500 * dt
            it.vel *= (1 - min(1, 3 * dt))
            it.pos += it.vel * dt
            it.pos.x = clamp(it.pos.x, 6, LW - 6)
            it.pos.y = clamp(it.pos.y, 6, LH - 6)
            if dist < p.radius + 8 or it.life > 20:
                self.pickup_weapon(it)
                it.dead = True
        self.weapon_items = [it for it in self.weapon_items if not it.dead]

        for e in self.enemies:
            if abs(e.squash - 1.0) > 0.01:
                e.squash += (1.0 - e.squash) * min(1.0, 10 * dt)
            else:
                e.squash = 1.0

        for q in self.particles:
            q.life -= dt
            q.pos += q.vel * dt
            q.vel *= (1 - min(1, 2 * dt))
        self.particles = [q for q in self.particles if q.life > 0]

        for t in self.texts:
            t.life -= dt
            t.pos.y += t.vy * dt
        self.texts = [t for t in self.texts if t.life > 0]
        if len(self.texts) > 90:
            self.texts = self.texts[-90:]

        if self.to_spawn > 0:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_enemy()
                self.to_spawn -= 1
                self.spawn_timer = self.spawn_interval
        elif not self.enemies:
            self.wave_complete()

    def update_boss(self, e, d, dt, new_minions):
        cfg = BOSS_CFG.get(e.boss_type, BOSS_CFG["frost"])
        if not e.enraged and e.hp < e.max_hp * 0.5:
            e.enraged = True
            e.atk = 0.6
            e.atk2 = 1.2
            e.summon = 1.5
            self.add_shake(6)
            self.sfx.play("wave")
            self.msg = "ЯРОСТЬ!"
            self.msg_t = 1.0
            self.burst(e.pos, 24, cfg["eye"], 140, 0.7, 2)
        spd_mul = 1.3 if e.enraged else 1.0
        cd_mul = 0.68 if e.enraged else 1.0
        if d.length_squared() > 1:
            e.pos += d.normalize() * e.speed * spd_mul * dt
        e.atk -= dt
        e.atk2 -= dt
        e.summon -= dt
        if e.atk <= 0:
            e.atk = cfg["atk_cd"] * cd_mul
            n = cfg["ring"] + (4 if e.enraged else 0)
            e.spin += 0.5
            spd = cfg["ring_spd"] * (1.15 if e.enraged else 1.0)
            for i in range(n):
                ang = e.spin + i * 2 * math.pi / n
                self.ebullets.append(EBullet(e.pos, (math.cos(ang) * spd, math.sin(ang) * spd),
                                             1, 3, cfg["bullet"]))
        if e.atk2 <= 0:
            e.atk2 = cfg["fan_cd"] * cd_mul
            base = math.atan2(d.y, d.x) if d.length_squared() > 0 else 0.0
            fn = cfg["fan"] + (2 if e.enraged else 0)
            spread = 0.16
            spd = cfg["fan_spd"] * (1.1 if e.enraged else 1.0)
            for k in range(fn):
                a = base + (k - (fn - 1) / 2) * spread
                self.ebullets.append(EBullet(e.pos, (math.cos(a) * spd, math.sin(a) * spd),
                                             1, 3, cfg["bullet"]))
        if e.summon <= 0 and len(self.enemies) < 20:
            e.summon = cfg["summon"] * (0.8 if e.enraged else 1.0)
            for _ in range(2 + (1 if e.enraged else 0)):
                off = pygame.Vector2(random.uniform(-e.radius, e.radius), random.uniform(-e.radius, e.radius))
                new_minions.append(Enemy(random.choice(["snow", "ice"]),
                                         e.pos + off, self.wave, self.diff))

    def use_ability(self, p, mv, dirv, aim=None):
        h = p.hero
        a = h["ability"]
        p.ability_cd = p.ability_max
        if a == "gust":
            length_ = 132
            dmg = max(1, int(round(p.damage * 1.4)))
            for e in list(self.enemies):
                rel = e.pos - p.pos
                along = rel.dot(dirv)
                if 0 < along < length_ and abs(rel.cross(dirv)) < 26 + e.radius:
                    e.hp -= dmg
                    e.flash = 0.15
                    e.squash = 1.4
                    e.pos += dirv * 34
                    self.texts.append(FloatText((e.pos.x, e.pos.y - e.radius), str(dmg),
                                                (210, 240, 255), 9, -40, 0.5))
                    if e.hp <= 0:
                        self.kill_enemy(e)
            self.enemies = [e for e in self.enemies if e.hp > 0]
            for k in range(18):
                t = k / 17
                pos = p.pos + dirv * (8 + t * length_)
                pos += pygame.Vector2(random.uniform(-7, 7), random.uniform(-7, 7))
                self.particles.append(Particle(pos, dirv * 40, (200, 235, 255), 0.3, 2))
            self.sfx.play("wave")
            self.add_shake(2)
        elif a == "guard":
            p.guard_time = 6.0
            self.add_shake(3)
            self.sfx.play("wave")
            self.burst(p.pos, 22, h["ear"], 150, 0.6, 2)
        elif a == "zap":
            target = pygame.Vector2(aim) if aim is not None else p.pos + dirv * 80
            target.x = clamp(target.x, 8, LW - 8)
            target.y = clamp(target.y, 8, LH - 8)
            dmg = max(1, int(round(p.damage * 1.8)))
            for e in list(self.enemies):
                if e.pos.distance_to(target) < 56 + e.radius:
                    e.hp -= dmg
                    e.flash = 0.15
                    e.squash = 1.4
                    e.freeze = max(e.freeze, 0.3)
                    self.texts.append(FloatText((e.pos.x, e.pos.y - e.radius), str(dmg),
                                                (255, 240, 120), 9, -40, 0.5))
                    if e.hp <= 0:
                        self.kill_enemy(e)
            self.enemies = [e for e in self.enemies if e.hp > 0]
            for k in range(16):
                ang = k * 2 * math.pi / 16
                self.particles.append(Particle(target + pygame.Vector2(math.cos(ang), math.sin(ang)) * 10,
                                               (math.cos(ang) * 120, math.sin(ang) * 120),
                                               (255, 240, 140), 0.3, 2))
            self.sfx.play("hit")
            self.add_shake(3)
        elif a == "blink":
            old = p.pos.copy()
            target = p.pos + dirv * 108
            target.x = clamp(target.x, p.radius, LW - p.radius)
            target.y = clamp(target.y, p.radius, LH - p.radius)
            p.pos = target
            p.iframe = max(p.iframe, 0.45)
            self.sfx.play("shoot")
            self.burst(old, 12, h["ear"], 90, 0.45, 2)
            self.burst(target, 12, C_ACCENT, 90, 0.45, 2)
        elif a == "storm":
            targets = sorted(self.enemies, key=lambda e: e.pos.distance_squared_to(p.pos))[:6]
            dmg = max(1, int(round(p.damage * 2.2)))
            for e in targets:
                e.hp -= dmg
                e.flash = 0.18
                e.squash = 1.4
                self.texts.append(FloatText((e.pos.x, e.pos.y - e.radius), str(dmg),
                                            (255, 240, 120), 9, -40, 0.5))
                if e.hp <= 0:
                    self.kill_enemy(e)
            self.enemies = [e for e in self.enemies if e.hp > 0]
            self.sfx.play("hit")
            self.add_shake(4)
        elif a == "fireball":
            target = pygame.Vector2(aim) if aim is not None else p.pos + dirv * 80
            target.x = clamp(target.x, 8, LW - 8)
            target.y = clamp(target.y, 8, LH - 8)
            self.explode(target, p.damage * 2.4, 62)
            self.add_shake(5)

    def shoot(self, p, dirv):
        w = WEAPONS_DICT.get(p.weapon_id, WEAPONS[0])
        kind = w["kind"]
        base_ang = math.atan2(dirv.y, dirv.x)
        muzzle = p.pos + dirv * (p.radius + 3)
        self.sfx.play("shoot")
        self.particles.append(Particle(muzzle, (math.cos(base_ang) * 40, math.sin(base_ang) * 40),
                                       (255, 236, 170), 0.12, 2))
        if kind == "hammer":
            count = p.multishot
            for i in range(count):
                ang = base_ang + (i - (count - 1) / 2) * 0.30
                d = pygame.Vector2(math.cos(ang), math.sin(ang))
                b = Bullet(muzzle, d * p.bullet_speed * 0.9, p.damage, 999,
                           kind="hammer", color=(200, 208, 226))
                b.radius = 5
                self.bullets.append(b)
            return
        pellets = w.get("pellets", 0)
        if pellets:
            count = pellets + (p.multishot - 1) * 2
            spread = w.get("spread", 0.3)
        else:
            count = p.multishot
            spread = 0.13 if kind == "shot" else 0.05
        for i in range(count):
            if count == 1:
                ang = base_ang
            else:
                ang = base_ang + (i - (count - 1) / 2) * spread
            if kind == "shot" and pellets:
                ang += random.uniform(-0.03, 0.03)
            d = pygame.Vector2(math.cos(ang), math.sin(ang))
            spd = p.bullet_speed * (random.uniform(0.92, 1.08) if kind == "shot" else 1.0)
            b = Bullet(muzzle, d * spd, p.damage, p.pierce, kind=kind,
                       explode=w.get("explode", 0), freeze=w.get("freeze", 0.0))
            if kind == "rocket":
                b.radius = 3
                b.color = (255, 190, 110)
            elif kind == "frost":
                b.color = (170, 235, 255)
            else:
                b.color = (140, 225, 255)
            self.bullets.append(b)

    def kill_enemy(self, e):
        # weapon drop
        if e.is_boss:
            # boss always drops weapon
            tier = min(WEAPON_TIER_MAX, random_weapon_tier() + 1)
            self.drop_weapon(e.pos, tier)
            self.loot_pending = True
            self.burst(e.pos, 40, C_SNOW, 160, 0.9, 2)
            self.add_shake(8)
            self.flash = 0.4
            self.flash_col = (255, 255, 200)
            # rune drop
            if random.random() < 0.4:
                rt = random.choice(RUNE_TYPES)
                self.player.runes.append(dict(id=rt["id"], level=1))
                self.texts.append(FloatText(e.pos, "РУНА: %s" % rt["name"],
                                            (200, 140, 255), 10, -40, 1.5))
                self.apply_upgrades()
        else:
            # 4% weapon drop from normal enemies
            if random.random() < 0.04:
                self.drop_weapon(e.pos, random_weapon_tier())
            self.burst(e.pos, 10, C_SNOW, 110, 0.5, 2)
            self.add_shake(2)
        n = e.reward
        for _ in range(n):
            self.coin_list.append(Coin(e.pos, 1))

    def player_die(self):
        self.state = "DEAD"
        self.best = max(self.best, self.wave)
        self.save_progress()
        self.add_shake(6)
        self.burst(self.player.pos, 24, C_RED, 140, 0.7, 2)
        self.flash = 0.6
        self.flash_col = (200, 30, 40)

    def draw(self):
        r = self.render
        self.ui_text.clear()
        self.world_text.clear()
        r.blit(self.bg, (0, 0))
        self.snow_bg.draw(r)
        if self.state in ("PLAY", "PAUSE", "SHOP", "DEAD", "LOOT", "DRAFT"):
            self.draw_world(r)
        if self.state == "MENU":
            self.draw_menu(r)
        elif self.state == "SELECT":
            self.draw_select(r)
        elif self.state == "DIFFICULTY":
            self.draw_difficulty(r)
        elif self.state == "PLAY":
            self.draw_hud(r)
        elif self.state == "PAUSE":
            self.draw_pause(r)
        elif self.state == "SHOP":
            self.draw_shop(r)
        elif self.state == "LOOT":
            self.draw_loot(r)
        elif self.state == "DRAFT":
            self.draw_draft(r)
        elif self.state == "REWIND":
            self.draw_rewind(r)
        elif self.state == "DEAD":
            self.draw_dead(r)
        self.snow_fg.draw(r, fg=True)
        if self.flash > 0:
            fl = surf(LW, LH)
            a = int(min(255, self.flash * 300))
            fl.fill((*self.flash_col, a))
            r.blit(fl, (0, 0))
        scaled = pygame.transform.scale(r, (LW * self.scale, LH * self.scale))
        self.screen.fill((0, 0, 0))
        ox = oy = 0
        if self.shake > 0:
            ox = random.randint(-int(self.shake), int(self.shake)) * self.scale
            oy = random.randint(-int(self.shake), int(self.shake)) * self.scale
        self.screen.blit(scaled, (self.off_x + ox, self.off_y + oy))
        self.draw_text(ox, oy)
        if self.state == "PLAY":
            self.draw_crosshair()
        pygame.display.flip()

    def draw_text(self, ox=0, oy=0):
        d = max(1, self.scale // 2)
        for s, x, y, size, color, center, bold, shadow in self.ui_text:
            f = F(max(8, int(round(size * self.scale))), bold)
            img = f.render(s, False, color)
            rect = img.get_rect()
            px = int(x * self.scale) + self.off_x
            py = int(y * self.scale) + self.off_y
            if center:
                rect.center = (px, py)
            else:
                rect.topleft = (px, py)
            if shadow:
                self.screen.blit(f.render(s, False, (0, 0, 0)), (rect.x + d, rect.y + d))
            self.screen.blit(img, rect)
        for s, x, y, size, color in self.world_text:
            f = F(max(8, int(round(size * self.scale))), False)
            img = f.render(s, False, color)
            rect = img.get_rect(center=(int(x * self.scale) + self.off_x + ox,
                                        int(y * self.scale) + self.off_y + oy))
            outline = f.render(s, False, (0, 0, 0))
            for ddx, ddy in ((-d, 0), (d, 0), (0, -d), (0, d)):
                self.screen.blit(outline, (rect.x + ddx, rect.y + ddy))
            self.screen.blit(img, rect)

    def draw_crosshair(self):
        mx, my = self.mouse_logical()
        cx = int(mx * self.scale) + self.off_x
        cy = int(my * self.scale) + self.off_y
        k = max(2, self.scale)
        pygame.draw.circle(self.screen, C_ACCENT, (cx, cy), 4 * k // 2, k)
        pygame.draw.line(self.screen, C_ACCENT, (cx - 6 * k // 2, cy), (cx - 2 * k // 2, cy), k)
        pygame.draw.line(self.screen, C_ACCENT, (cx + 2 * k // 2, cy), (cx + 6 * k // 2, cy), k)
        pygame.draw.line(self.screen, C_ACCENT, (cx, cy - 6 * k // 2), (cx, cy - 2 * k // 2), k)
        pygame.draw.line(self.screen, C_ACCENT, (cx, cy + 2 * k // 2), (cx, cy + 6 * k // 2), k)

    def draw_world(self, r):
        for b in self.bullets:
            for i, (tx, ty) in enumerate(b.trail):
                fade = (i + 1) / len(b.trail)
                s = max(1, int(2 * fade))
                pygame.draw.circle(r, b.color, (int(tx), int(ty)), s)
        for c in self.coin_list:
            frame = int(c.life * 12) % 4
            g = glow(6, C_GOLD)
            r.blit(g, (int(c.pos.x) - g.get_width() // 2, int(c.pos.y) - g.get_height() // 2),
                   special_flags=pygame.BLEND_ADD)
            r.blit(self.spr_coin_frames[frame], (int(c.pos.x) - 4, int(c.pos.y) - 4))

        # weapon drops
        for it in self.weapon_items:
            info = WEAPON_TIERS[it.tier]
            bob = math.sin(it.life * 4 + it.bob) * 2
            g = glow(12 + it.tier * 3, info["color"])
            r.blit(g, (int(it.pos.x) - g.get_width() // 2,
                       int(it.pos.y) - g.get_height() // 2 + bob), special_flags=pygame.BLEND_ADD)
            icon = self.spr_weapon[it.wid]
            r.blit(icon, (int(it.pos.x) - icon.get_width() // 2,
                          int(it.pos.y) - icon.get_height() // 2 + bob))
            # tier pips
            for p in range(it.tier + 1):
                pygame.draw.circle(r, info["color"],
                                   (int(it.pos.x) - it.tier * 3 + p * 6, int(it.pos.y) + 14 + bob), 1)

        for e in self.enemies:
            sw = int(e.radius * 1.6 * e.squash)
            sh = max(2, int(e.radius * 0.45))
            shadow = pygame.Surface((sw * 2, sh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, sw * 2, sh * 2))
            r.blit(shadow, (int(e.pos.x) - sw, int(e.pos.y + e.radius * 0.7) - sh // 2))
            if e.is_boss:
                img = self.spr_boss[e.boss_type or "frost"]
                bg = glow(30, BOSS_CFG[e.boss_type]["eye"])
                r.blit(bg, (int(e.pos.x) - bg.get_width() // 2,
                            int(e.pos.y) - bg.get_height() // 2), special_flags=pygame.BLEND_ADD)
            else:
                img = self.spr_enemy[e.kind]
            ox = int(math.sin(self.time * 2 + e.phase) * 2) if e.is_boss else 0
            if e.squash != 1.0:
                w2 = max(1, int(img.get_width() * e.squash))
                h2 = max(1, int(img.get_height() / e.squash))
                img = pygame.transform.scale(img, (w2, h2))
            r.blit(img, (int(e.pos.x) - img.get_width() // 2 + ox,
                         int(e.pos.y) - img.get_height() // 2))
            if e.freeze > 0:
                pygame.draw.circle(r, (150, 215, 255), (int(e.pos.x), int(e.pos.y)), e.radius + 2, 1)
            if e.flash > 0:
                pygame.draw.circle(r, (255, 255, 255), (int(e.pos.x), int(e.pos.y)), e.radius + 1, 1)
            if e.is_boss and e.enraged:
                ring = 1 + int(abs(math.sin(self.time * 4)) * 3)
                cfg = BOSS_CFG.get(e.boss_type, BOSS_CFG["frost"])
                pygame.draw.circle(r, cfg["eye"], (int(e.pos.x), int(e.pos.y)),
                                   e.radius + 4 + ring, 1)
        for b in self.bullets:
            g = glow(6, b.color)
            r.blit(g, (int(b.pos.x) - g.get_width() // 2, int(b.pos.y) - g.get_height() // 2),
                   special_flags=pygame.BLEND_ADD)
            px, py = int(b.pos.x), int(b.pos.y)
            if b.kind == "hammer":
                pygame.draw.circle(r, (60, 66, 84), (px, py), 6)
                pygame.draw.circle(r, (170, 182, 204), (px, py), 5)
                ax = math.cos(b.spin) * 4
                ay = math.sin(b.spin) * 4
                pygame.draw.line(r, (100, 84, 60), (px - ax, py - ay), (px + ax, py + ay), 2)
            elif b.kind == "rocket":
                pygame.draw.circle(r, (255, 150, 60), (px, py), 3)
                pygame.draw.circle(r, (255, 232, 150), (px, py), 1)
            elif b.kind == "frost":
                pygame.draw.circle(r, (120, 200, 255), (px, py), 3)
                pygame.draw.circle(r, (235, 250, 255), (px, py), 1)
            else:
                r.blit(self.spr_bullet, (px - 2, py - 2))
        for b in self.ebullets:
            g = glow(5, b.color)
            r.blit(g, (int(b.pos.x) - g.get_width() // 2, int(b.pos.y) - g.get_height() // 2),
                   special_flags=pygame.BLEND_ADD)
            pygame.draw.circle(r, (30, 40, 60), (int(b.pos.x), int(b.pos.y)), b.radius + 1)
            pygame.draw.circle(r, b.color, (int(b.pos.x), int(b.pos.y)), b.radius)
            pygame.draw.circle(r, (255, 255, 255), (int(b.pos.x) - 1, int(b.pos.y) - 1), 1)
        p = self.player
        shadow_w = p.radius * 3
        shadow = pygame.Surface((shadow_w * 2, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 110), (0, 0, shadow_w * 2, 10))
        r.blit(shadow, (int(p.pos.x) - shadow_w, int(p.pos.y + p.radius - 1)))
        pair = self.spr_hero.get(p.hero["id"], self.spr_hero["snow"])
        img = pair[0] if p.facing >= 0 else pair[1]
        by = int(math.sin(p.walk) * 1.6)
        if p.iframe > 0 and int(p.iframe * 20) % 2 == 0:
            img = img.copy()
            img.set_alpha(120)
        r.blit(img, (int(p.pos.x) - img.get_width() // 2,
                     int(p.pos.y) - img.get_height() // 2 + by))
        # equipped weapon with tier glow
        tier_info = WEAPON_TIERS[p.weapon_tier]
        if p.weapon_tier > 0:
            g = glow(10 + p.weapon_tier * 2, tier_info["color"])
            r.blit(g, (int(p.pos.x) - g.get_width() // 2 + 12,
                       int(p.pos.y) - g.get_height() // 2 - 8), special_flags=pygame.BLEND_ADD)
        if p.guard_time > 0:
            rad = p.radius + 7 + int(abs(math.sin(self.time * 6)) * 2)
            pygame.draw.circle(r, (255, 214, 120), (int(p.pos.x), int(p.pos.y)), rad, 2)
        for q in self.particles:
            a = clamp(q.life / q.max_life, 0, 1)
            col = tuple(int(c * a + 20 * (1 - a)) for c in q.color)
            pygame.draw.rect(r, col, (int(q.pos.x), int(q.pos.y), q.size, q.size))
        for t in self.texts:
            a = clamp(t.life / t.max_life, 0, 1)
            col = tuple(int(c * a + 30 * (1 - a)) for c in t.color)
            self.world_text.append((t.s, t.pos.x, t.pos.y, t.size, col))

    def draw_heart(self, r, x, y, filled):
        col = (255, 80, 110) if filled else (55, 30, 42)
        pygame.draw.circle(r, col, (x + 2, y + 2), 2)
        pygame.draw.circle(r, col, (x + 5, y + 2), 2)
        pygame.draw.polygon(r, col, [(x, y + 3), (x + 7, y + 3), (x + 3, y + 7)])

    def draw_hud(self, r):
        p = self.player
        if p.max_hp <= 14:
            hpshow = int(math.ceil(p.hp))
            for i in range(p.max_hp):
                self.draw_heart(r, 6 + i * 9, 5, i < hpshow)
            self.tx("%d/%d" % (hpshow, p.max_hp),
                    (10 + p.max_hp * 9 + 14, 12), 7, C_WHITE, bold=True, shadow=False)
        else:
            pygame.draw.rect(r, (24, 28, 42), (6, 6, 88, 12), border_radius=3)
            pygame.draw.rect(r, (48, 54, 76), (7, 7, 86, 10), border_radius=2)
            frac = clamp(p.hp / p.max_hp, 0, 1)
            col = C_GREEN if frac > 0.35 else C_RED
            pygame.draw.rect(r, col, (7, 7, int(86 * frac), 10), border_radius=2)
        self.tx("ВОЛНА %d" % self.wave, (LW / 2, 12), 10, C_ACCENT, center=True, bold=True)
        pygame.draw.circle(r, (170, 110, 20), (LW - 55, 9), 4)
        pygame.draw.circle(r, C_GOLD, (LW - 55, 9), 3)
        self.tx(str(self.coins), (LW - 48, 4), 10, C_GOLD, bold=True)
        # weapon with tier color
        tier_info = WEAPON_TIERS[p.weapon_tier]
        wname = WEAPONS_DICT[p.weapon_id]["name"]
        self.tx(wname, (LW - 34, 20), 7, tier_info["color"], center=True, bold=True, shadow=False)
        # tier pips
        for i in range(p.weapon_tier + 1):
            pygame.draw.circle(r, tier_info["color"], (LW - 34 - p.weapon_tier * 3 + i * 6, 28), 1)
        boss = next((e for e in self.enemies if e.is_boss), None)
        if boss is not None:
            cfg = BOSS_CFG.get(boss.boss_type, BOSS_CFG["frost"])
            bw = 190
            bx = (LW - bw) // 2
            by = 26
            pygame.draw.rect(r, (28, 28, 44), (bx - 1, by - 1, bw + 2, 9), border_radius=2)
            pygame.draw.rect(r, (58, 40, 62), (bx, by, bw, 7), border_radius=2)
            bf = clamp(boss.hp / boss.max_hp, 0, 1)
            bc = (255, 110, 140) if boss.enraged else cfg["eye"]
            pygame.draw.rect(r, bc, (bx, by, int(bw * bf), 7), border_radius=2)
            label = "БОСС · %s" % cfg["name"]
            self.tx(label, (LW / 2, by + 12), 7, (255, 220, 235), center=True, shadow=False)
        # ability bar
        ac = clamp(1 - p.ability_cd / max(0.01, p.ability_max), 0, 1)
        pygame.draw.rect(r, (24, 28, 42), (6, 21, 74, 6), border_radius=2)
        if ac < 1:
            pygame.draw.rect(r, (30, 74, 96), (7, 22, int(72 * ac), 4), border_radius=1)
        else:
            pulse = int(abs(math.sin(self.time * 4)) * 40) + 180
            pygame.draw.rect(r, (min(255, pulse), 230, 255), (7, 22, 72, 4), border_radius=1)
        self.tx(p.hero["aname"], (84, 20), 6,
                C_ACCENT if ac >= 1 else (120, 140, 165), bold=True, shadow=False)
        # draft crit/dev display
        if p.dev_chance > 0:
            self.tx("DEV %d%%" % int(p.dev_chance * 100),
                    (LW - 50, 30), 6, (255, 130, 255), bold=True, shadow=False)
        hint = "WASD · Shift · ЛКМ · ESC · M"
        self.tx(hint, (LW / 2, LH - 12), 7, (150, 170, 200), center=True)
        if self.msg_t > 0:
            self.tx(self.msg, (LW / 2, LH / 2 - 40), 15, C_WHITE, center=True, bold=True)

    def draw_menu(self, r):
        ov = surf(LW, LH)
        ov.fill((6, 8, 16))
        ov.set_alpha(120)
        r.blit(ov, (0, 0))
        self.tx("GUINEA", (LW / 2, 62), 30, C_ACCENT, center=True, bold=True)
        self.tx("ARENA", (LW / 2, 92), 30, C_GOLD, center=True, bold=True)
        self.tx("Days Bygone Edition", (LW / 2, 116), 9, (200, 210, 230), center=True)
        h = HEROES[self.hero_idx]
        img = self.spr_hero[h["id"]][0]
        big = pygame.transform.scale(img, (img.get_width() * 4, img.get_height() * 4))
        r.blit(big, (LW // 2 - big.get_width() // 2, 124))
        self.tx(h["name"], (LW / 2, 198), 9, C_WHITE, center=True, bold=True)
        self.tx("%s · %s" % (h["role"], h["aname"]), (LW / 2, 209), 7, C_ACCENT, center=True)
        if self.best > 0:
            self.tx("лучшая волна: %d" % self.best, (LW / 2, 224), 8, C_GOLD, center=True)
        total_stars = self.player.rewind_stacks.get("rw_star", 0)
        if self.rewind_elixir_total > 0 or total_stars > 0:
            info = "Эликсир: %d" % self.rewind_elixir_total
            if total_stars > 0:
                info += "  ·  " + "★" * total_stars
            self.tx(info, (LW / 2, 236), 7, C_PURPLE, center=True, bold=True)
        if int(self.time * 2) % 2 == 0:
            self.tx("SPACE — играть   W — перерождение",
                    (LW / 2, 250), 10, C_WHITE, center=True, bold=True)

    def draw_select(self, r):
        ov = surf(LW, LH)
        ov.fill((5, 7, 14))
        ov.set_alpha(190)
        r.blit(ov, (0, 0))
        self.tx("ВЫБЕРИ ГЕРОЯ", (LW / 2, 18), 14, C_ACCENT, center=True, bold=True)
        self.tx("у каждого своя способность на SHIFT", (LW / 2, 32), 7, (170, 190, 215), center=True)
        mx, my = self.mouse_logical()
        for i, rect in enumerate(self.hero_cards()):
            h = HEROES[i]
            sel = (i == self.hero_idx)
            hover = rect.collidepoint(mx, my)
            fill = (30, 42, 70) if sel else ((24, 32, 52) if hover else (16, 22, 38))
            pygame.draw.rect(r, fill, rect, border_radius=3)
            pygame.draw.rect(r, C_ACCENT if sel else (44, 58, 88), rect,
                             2 if sel else 1, border_radius=3)
            cx = rect.centerx
            self.tx(h["name"], (cx, rect.y + 10), 8,
                    C_WHITE if sel else (200, 210, 228), center=True, bold=True)
            self.tx(h["role"], (cx, rect.y + 19), 6, (150, 170, 195), center=True)
            img = self.spr_hero[h["id"]][0]
            big = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            r.blit(big, (cx - big.get_width() // 2, rect.y + 28))
            self.tx("HP %d   УРОН %.1f" % (h["hp"], h["dmg"]),
                    (cx, rect.y + 82), 7, C_WHITE, center=True)
            self.tx(h["aname"], (cx, rect.y + 112), 8, C_ACCENT, center=True, bold=True)
            self.tx(h["adesc"], (cx, rect.y + 126), 6, (190, 205, 225), center=True)
            self.tx("[%d]" % (i + 1), (cx, rect.y + 160), 9,
                    C_GOLD if sel else (130, 140, 160), center=True, bold=True)
        if int(self.time * 2) % 2 == 0:
            self.tx("← → / 1-6 — герой    SPACE — в бой    ESC — назад",
                    (LW / 2, 248), 8, C_WHITE, center=True, bold=True)

    def draw_difficulty(self, r):
        ov = surf(LW, LH)
        ov.fill((5, 7, 14))
        ov.set_alpha(200)
        r.blit(ov, (0, 0))
        self.tx("СЛОЖНОСТЬ", (LW / 2, 20), 16, C_ACCENT, center=True, bold=True)
        mx, my = self.mouse_logical()
        for i, rect in enumerate(self.difficulty_cards()):
            d = DIFFICULTIES[i]
            sel = (i == self.diff_idx)
            hover = rect.collidepoint(mx, my)
            fill = (30, 42, 70) if sel else ((24, 32, 52) if hover else (16, 22, 38))
            pygame.draw.rect(r, fill, rect, border_radius=3)
            pygame.draw.rect(r, d["color"] if sel else (44, 58, 88),
                             rect, 2 if sel else 1, border_radius=3)
            cx = rect.centerx
            self.tx(d["name"], (cx, rect.y + 12), 9,
                    d["color"] if sel else (200, 210, 228), center=True, bold=True)
            self.tx("HP x%.2f" % d["hp"], (cx, rect.y + 40), 7, C_WHITE, center=True)
            self.tx("DMG x%.2f" % d["dmg"], (cx, rect.y + 52), 7, C_WHITE, center=True)
            self.tx("МОНЕТЫ x%.2f" % d["coin"], (cx, rect.y + 70), 7, C_GOLD, center=True, bold=True)
            self.tx("[%d]" % (i + 1), (cx, rect.y + 100), 9,
                    C_GOLD if sel else (130, 140, 160), center=True, bold=True)
        if int(self.time * 2) % 2 == 0:
            self.tx("← → / 1-4   SPACE — в бой   ESC — назад",
                    (LW / 2, LH - 20), 8, C_WHITE, center=True, bold=True)

    def draw_pause(self, r):
        ov = surf(LW, LH)
        ov.fill((4, 6, 12))
        ov.set_alpha(150)
        r.blit(ov, (0, 0))
        self.tx("ПАУЗА", (LW / 2, LH / 2 - 26), 20, C_ACCENT, center=True, bold=True)
        self.tx("%s · %s" % (self.hero["name"], self.hero["aname"]),
                (LW / 2, LH / 2 + 2), 8, C_GOLD, center=True)
        self.tx("ESC — продолжить", (LW / 2, LH / 2 + 20), 9, C_WHITE, center=True)

    def draw_shop(self, r):
        ov = surf(LW, LH)
        ov.fill((4, 6, 12))
        ov.set_alpha(185)
        r.blit(ov, (0, 0))
        px, py, pw, ph = 30, 22, LW - 60, LH - 44
        pygame.draw.rect(r, C_UI, (px, py, pw, ph), border_radius=4)
        pygame.draw.rect(r, C_UI2, (px, py, pw, ph), 1, border_radius=4)
        self.tx("МАГАЗИН", (LW / 2, py + 12), 14, C_ACCENT, center=True, bold=True)
        self.tx("Волна %d · Монеты: %d" % (self.wave, self.coins),
                (LW / 2, py + 30), 8, C_GOLD, center=True)
        col_x = [px + 14, px + pw // 2 + 6]
        row_y0 = py + 46
        row_h = 30
        for i, u in enumerate(UPGRADES):
            col = 0 if i < 5 else 1
            row = i % 5
            x = col_x[col]
            y = row_y0 + row * row_h
            lvl = self.up[u["id"]]
            maxed = lvl >= u["max"]
            cost = self.cost(u)
            afford = (not maxed) and self.coins >= cost
            key = str((i + 1) % 10)
            if maxed:
                name_col = C_GREEN
            elif afford:
                name_col = C_WHITE
            else:
                name_col = (130, 140, 160)
            self.tx("[%s] %s  ур.%d" % (key, u["name"], lvl), (x, y), 8,
                    name_col, bold=True, shadow=False)
            status = "МАКС" if maxed else "%d монет" % cost
            sc = C_GREEN if maxed else (C_GOLD if afford else (150, 110, 90))
            self.tx(u["desc"], (x, y + 10), 7, (150, 165, 190), shadow=False)
            self.tx(status, (x, y + 19), 8, sc, shadow=False)
        self.tx("1-9,0 — купить   SPACE — следующая волна",
                (LW / 2, py + ph - 12), 8, C_ACCENT, center=True, bold=True)

    def draw_loot(self, r):
        ov = surf(LW, LH)
        ov.fill((4, 6, 12))
        ov.set_alpha(205)
        r.blit(ov, (0, 0))
        self.tx("НАГРАДА ЗА БОССА", (LW / 2, 18), 15, C_GOLD, center=True, bold=True)
        self.tx("выбери аксессуар", (LW / 2, 34), 8, (200, 210, 230), center=True)
        mx, my = self.mouse_logical()
        for i, rect in enumerate(self.loot_cards()):
            a = self.loot_choices[i]
            rar_name, rar_col = RARITY[a["rarity"]]
            hover = rect.collidepoint(mx, my)
            fill = (32, 40, 62) if hover else (16, 22, 38)
            pygame.draw.rect(r, fill, rect, border_radius=4)
            pygame.draw.rect(r, rar_col, rect, 2, border_radius=4)
            cx = rect.centerx
            self.tx(rar_name, (cx, rect.y + 10), 7, rar_col, center=True, bold=True)
            icon = self.spr_acc[a["id"]]
            big = pygame.transform.scale(icon, (icon.get_width() * 3, icon.get_height() * 3))
            r.blit(big, (cx - big.get_width() // 2, rect.y + 22))
            self.tx(a["name"], (cx, rect.y + 98), 7, C_WHITE, center=True, bold=True)
            self.tx(a["desc"], (cx, rect.y + 112), 7, (190, 205, 225), center=True)
            self.tx("[%d]" % (i + 1), (cx, rect.y + 132), 10, C_GOLD, center=True, bold=True)
        self.tx("клик или 1-3 — взять", (LW / 2, LH - 18), 8, C_ACCENT, center=True, bold=True)

    def draw_draft(self, r):
        ov = surf(LW, LH)
        ov.fill((4, 6, 20))
        ov.set_alpha(210)
        r.blit(ov, (0, 0))
        self.tx("ВЫБЕРИ УЛУЧШЕНИЕ", (LW / 2, 20), 15, C_GOLD, center=True, bold=True)
        self.tx("бесплатный бонус на этот забег", (LW / 2, 38), 8, (200, 220, 255), center=True)
        mx, my = self.mouse_logical()
        for i, rect in enumerate(self.draft_cards()):
            d = self.draft_choices[i]
            hover = rect.collidepoint(mx, my)
            fill = (32, 42, 72) if hover else (16, 22, 38)
            pygame.draw.rect(r, fill, rect, border_radius=5)
            pygame.draw.rect(r, C_ACCENT, rect, 2, border_radius=5)
            if hover:
                pygame.draw.rect(r, C_GOLD, rect.inflate(-4, -4), 1, border_radius=5)
            cx = rect.centerx
            self.tx(d["name"], (cx, rect.y + 24), 11, C_GOLD, center=True, bold=True)
            self.tx(d["desc"], (cx, rect.y + 60), 8, (200, 220, 255), center=True)
            # big icon
            pygame.draw.circle(r, C_ACCENT, (cx, rect.y + 100), 14, 1)
            pygame.draw.circle(r, C_ACCENT, (cx, rect.y + 100), 2)
            self.tx("[%d]" % (i + 1), (cx, rect.y + 130), 10, C_WHITE, center=True, bold=True)
        self.tx("клик или 1-3 — взять улучшение",
                (LW / 2, LH - 18), 8, C_ACCENT, center=True, bold=True)

    def draw_rewind(self, r):
        ov = surf(LW, LH)
        ov.fill((4, 6, 16))
        ov.set_alpha(210)
        r.blit(ov, (0, 0))
        self.tx("ПЕРЕРОЖДЕНИЕ", (LW / 2, 16), 15, C_PURPLE, center=True, bold=True)
        self.tx("Эликсир: %d  ·  +%d за этот забег" % (self.rewind_elixir_total, self.rewind_elixir()),
                (LW / 2, 32), 8, (200, 240, 255), center=True)
        for i, u in enumerate(REWIND_UPGRADES):
            y = 56 + i * 28
            cur = self.player.rewind_stacks.get(u["id"], 0)
            maxed = cur >= u["max"]
            cost = self.rewind_cost(u)
            afford = (not maxed) and self.rewind_elixir_total >= cost
            col = C_GREEN if maxed else (C_WHITE if afford else (130, 140, 160))
            self.tx("[%d] %s  ур.%d/%d" % (i + 1, u["name"], cur, u["max"]),
                    (26, y), 8, col, bold=True, shadow=False)
            self.tx(u["desc"], (26, y + 10), 7, (160, 175, 195), shadow=False)
            self.tx("МАКС" if maxed else "%d Э" % cost,
                    (LW - 50, y), 8,
                    C_GREEN if maxed else (C_GOLD if afford else (150, 110, 90)),
                    bold=True, shadow=False)
        if int(self.time * 2) % 2 == 0:
            self.tx("1-6 — купить   SPACE — переродиться   ESC — назад",
                    (LW / 2, LH - 14), 8, C_WHITE, center=True, bold=True)

    def draw_dead(self, r):
        ov = surf(LW, LH)
        ov.fill((10, 2, 4))
        ov.set_alpha(175)
        r.blit(ov, (0, 0))
        self.tx("ТЫ ПАЛ...", (LW / 2, LH / 2 - 44), 24, C_RED, center=True, bold=True)
        self.tx("дошёл до волны %d" % self.wave, (LW / 2, LH / 2 - 12), 11, C_WHITE, center=True)
        self.tx("%s · монет: %d" % (self.hero["name"], self.coins),
                (LW / 2, LH / 2 + 4), 9, C_GOLD, center=True)
        if self.best > 0:
            self.tx("рекорд: волна %d" % self.best, (LW / 2, LH / 2 + 20), 9, C_ACCENT, center=True)
        self.tx("Получишь +%d ЭЛИКСИРА" % self.rewind_elixir(),
                (LW / 2, LH / 2 + 36), 9, C_PURPLE, center=True, bold=True)
        if int(self.time * 2) % 2 == 0:
            self.tx("R — заново   T — перерождение   SPACE — герой   ESC — меню",
                    (LW / 2, LH / 2 + 56), 8, C_WHITE, center=True, bold=True)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            for e in pygame.event.get():
                self.handle_event(e)
            self.update(dt)
            self.draw()
        pygame.quit()


WEAPONS_DICT = {w["id"]: w for w in WEAPONS}


def selftest():
    global SAVE_PATH
    SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_selftest_save.json")
    pygame.init()
    g = Game()
    g.draw()
    g.state = "SELECT"
    g.draw()
    g.state = "DIFFICULTY"
    g.draw()
    g.hero_idx = 0
    g.start_new_game()
    assert g.state == "PLAY" and g.wave == 1
    assert g.player.weapon_id == "sword"
    # weapon drop test
    g.drop_weapon(g.player.pos, 2, "bazooka")
    for _ in range(60):
        g.update(1 / 60)
    assert g.player.weapon_id == "bazooka", "weapon not picked up"
    assert g.player.weapon_tier == 2
    # merge test: same weapon drop
    g.drop_weapon(g.player.pos, 2, "bazooka")
    for _ in range(60):
        g.update(1 / 60)
    assert g.player.weapon_tier == 3, "merge failed (tier=%d)" % g.player.weapon_tier
    # wave clear → draft
    for e in list(g.enemies):
        g.kill_enemy(e)
    g.enemies.clear()
    g.to_spawn = 0
    g.update(1 / 60)
    assert g.state == "DRAFT", "expected DRAFT, got %s" % g.state
    assert len(g.draft_choices) == 3
    g.draw()
    g.apply_draft(0)
    assert g.state == "SHOP"
    g.coins = 10000
    for i in range(len(UPGRADES)):
        g.buy(i)
    g.draw()
    g.start_wave(2)
    for _ in range(60):
        g.update(1 / 60)
    # boss wave + LOOT
    g.player.max_hp = 999
    g.player.hp = 999
    g.start_wave(5)
    assert any(e.is_boss for e in g.enemies)
    for _ in range(120):
        g.update(1 / 60)
    boss = next(e for e in g.enemies if e.is_boss)
    boss.hp = 0
    g.kill_enemy(boss)
    g.enemies = [e for e in g.enemies if e.hp > 0]
    for e in list(g.enemies):
        e.hp = 0
    g.enemies = []
    g.to_spawn = 0
    g.update(1 / 60)
    assert g.state == "LOOT"
    g.take_loot(0)
    assert g.state == "DRAFT"
    g.apply_draft(0)
    assert g.state == "SHOP"
    # rewind test
    g.rewind_elixir_total = 999
    g.state = "REWIND"
    g.buy_rewind_upgrade(0)
    assert g.player.rewind_stacks["rw_dmg"] >= 1
    g.wave = 5
    old = g.player.rewind_stacks["rw_dmg"]
    g.do_rewind()
    assert g.player.rewind_stacks["rw_dmg"] == old
    # death
    g.player.hp = 0
    g.player_die()
    assert g.state == "DEAD"
    pygame.quit()
    try:
        os.remove(SAVE_PATH)
    except Exception:
        pass
    print("SELFTEST OK wave=%d coins=%d tier=%d" % (g.wave, g.coins, g.player.weapon_tier))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        try:
            Game().run()
        except Exception:
            import traceback
            traceback.print_exc()
            pygame.quit()
            raise
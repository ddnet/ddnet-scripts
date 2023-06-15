#!/usr/bin/env python3

import sys
import re

def escape(inp):
    return inp

tunings = {
    "ground_control_speed": 0,
    "ground_control_accel": 1,
    "ground_friction": 2,
    "ground_jump_impulse": 3,
    "air_jump_impulse": 4,
    "air_control_speed": 5,
    "air_control_accel": 6,
    "air_friction": 7,
    "hook_length": 8,
    "hook_fire_speed": 9,
    "hook_drag_accel": 10,
    "hook_drag_speed": 11,
    "gravity": 12,
    "velramp_start": 13,
    "velramp_range": 14,
    "velramp_curvature": 15,
    "gun_curvature": 16,
    "gun_speed": 17,
    "gun_lifetime": 18,
    "shotgun_curvature": 19,
    "shotgun_speed": 20,
    "shotgun_speeddiff": 21,
    "shotgun_lifetime": 22,
    "grenade_curvature": 23,
    "grenade_speed": 24,
    "grenade_lifetime": 25,
    "laser_reach": 26,
    "laser_bounce_delay": 27,
    "laser_bounce_num": 28,
    "laser_bounce_cost": 29,
    "laser_damage": 30,
    "player_collision": 31,
    "player_hooking": 32,
    "jetpack_strength": 33,
    "shotgun_strength": 34,
    "explosion_strength": 35,
    "hammer_strength": 36,
    "hook_duration": 37,
    "hammer_fire_delay": 38,
    "gun_fire_delay": 39,
    "shotgun_fire_delay": 40,
    "grenade_fire_delay": 41,
    "laser_fire_delay": 42,
    "ninja_fire_delay": 43,
    "hammer_hit_fire_delay": 44,
    # add new tunings below here with increasing numbers
}

offset = int(sys.argv[1])

print('{| class="wikitable"')
print(f"! <translate><!--T:{offset+1}--> Tuning</translate>")
print(f"! <translate><!--T:{offset+2}--> Description</translate>")
print(f"! <translate><!--T:{offset+3}--> Default</translate>")

def foo(x):
  if x.endswith("f / TicksPerSecond"):
    x = x.rstrip("f / TicksPerSecond")
    return float(x) / 50.0
  return x.strip("f")


for line in sys.stdin:
  x = re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', line)

  idx = offset + 100 + tunings[x[1].strip()] * 5
  result = (escape(x[1].strip()), idx, escape(x[3].strip(" )\n").split('"')[-2]), escape(str(foo(x[2]))))

  print("|-")
  print("| %s\n| <translate><!--T:%s--> %s</translate>\n| %s" % result)

print('|}')

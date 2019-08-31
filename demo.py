"""
import sys
from importlib import reload
sys.path.insert(0, "/home/tbrown/t/Proj/misc_py/blender_maker")
import demo
reload(demo); demo.main()
"""
from cad import (
    DR,
    MATERIALS,
    OFFSET,
    TEXT_ALIGN,
    _v,
    bind_parents,
    bpy,
    crange,
    delete,
    do_bool,
    move_to,
    new_obj,
    obj_add,
    origin,
    rel_coords,
    replicate,
    reset_blend,
    rotate,
    scale,
    size,
    translate,
)

FINAL = True  # use slower code to get details right


def main():

    reset_blend()

    pyb = new_obj("PyBoard")
    obj_add(pyb)
    size(pyb, (32, 41, 1))
    translate(pyb, (-70, 70, 0))
    # make ~toroid mount points, but don't attach yet, that would change bounds
    cyl = new_obj()
    obj_add(cyl, what='unit_cyl')
    size(cyl, (3, 3, 1))
    drill = replicate(cyl)
    size(drill, (2, 2, 2))
    do_bool(cyl, drill, 'DIFFERENCE')

    hole = {
        ('PyBoard', (0, 0, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(I) V+',
            'off': (-2, 0.5, 0),
        },
        ('PyBoard', (0, 2, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(J) GND',
            'off': (-2, 0.5, 0),
        },
        ('PyBoard', (0, 4, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(C) Y12',
            'off': (-2, 0.5, 0),
        },
        ('PyBoard', (0, 6, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(L) Y10',
            'off': (-2, 0.5, 0),
        },
        ('PyBoard', (0, 7, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(K) Y9',
            'off': (-2, 0.5, 0),
        },
        ('PyBoard', (0, 14, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(H) X2',
            'off': (-4, 0.5, 0),
        },
        ('PyBoard', (0, 15, 0), 'pybside'): {
            'g': 'RC',
            'lab': '(G) X1',
            'off': (-4, 0.5, 0),
        },
        ('PyBoard', (1, 0, 0), 'pybtop'): {
            'g': 'RC',
            'lab': '(F) V+',
            'off': (0.5, 2, 0),
            'rot': (0, 0, -90),
        },
        ('PyBoard', (2, 0, 0), 'pybtop'): {
            'g': 'RC',
            'lab': '(E) GND',
            'off': (0.5, 2, 0),
            'rot': (0, 0, -90),
        },
        ('PyBoard', (1, 15, 0), 'pybside'): {
            'lab': '(B) V+',
            'off': (2, 0.5, 0),
        },
        ('PyBoard', (1, 13, 0), 'pybside'): {
            'lab': '(A) GND',
            'off': (2, 0.5, 0),
        },
        ('PyBoard', (1, 11, 0), 'pybside'): {
            'lab': '(D) X12',
            'off': (2, 0.5, 0),
        },
        ('GPS', (0, 4, 0)): {'lab': '(L) TX', 'off': (3, 0.5, 0)},
        ('GPS', (0, 5, 0)): {'lab': '(K) RX', 'off': (3, 0.5, 0)},
        ('GPS', (0, 6, 0)): {'lab': '(J) GND', 'off': (3, 0.5, 0)},
        ('GPS', (0, 7, 0)): {'lab': '(I) VIN', 'off': (3, 0.5, 0)},
        ('rad.adapt', (3, 0, 0)): {
            'rot': (0, 0, -90),
            'lab': '(E) GND',
            'off': (0.5, -3.5, 0),
        },
        ('rad.adapt', (5, 0, 0)): {
            'rot': (0, 0, -90),
            'lab': '(F) +5V',
            'off': (0.5, -3.5, 0),
        },
        ('rad.adapt', (6, 0, 0)): {
            'rot': (0, 0, -90),
            'lab': '(G) RX',
            'off': (0.5, -3.5, 0),
        },
        ('rad.adapt', (7, 0, 0)): {
            'rot': (0, 0, -90),
            'lab': '(H) TX',
            'off': (0.5, -3.5, 0),
        },
        ('Cond_controller', (0, 0, 0), 's'): {
            'g': 'RC',
            'rot': (0, 0, -90),
            'lab': 'SI1',
            'off': (0.5, 7.5, 0),
        },
        ('Cond_controller', (1, 0, 0), 's'): {
            'g': 'RC',
            'rot': (0, 0, -90),
            'lab': 'SI2',
            'off': (0.5, 7.5, 0),
        },
        ('Cond_controller', (2, 0, 0), 's'): {
            'g': 'RC',
            'rot': (0, 0, -90),
            'lab': 'SI3',
            'off': (0.5, 7.5, 0),
        },
        ('Cond_controller', (3, 0, 0), 's'): {
            'g': 'RC',
            'rot': (0, 0, -90),
            'lab': 'SI4',
            'off': (0.5, 7.5, 0),
        },
        ('Cond_controller', (4, 0, 0), 's'): {
            'g': 'RC',
            'rot': (0, 0, -90),
            'lab': 'SI5',
            'off': (0.5, 7.5, 0),
        },
        ('Cond_controller', (5, 0, 0), 's'): {
            'g': 'RC',
            'rot': (0, 0, -90),
            'lab': 'SI6',
            'off': (0.5, 7.5, 0),
        },
        ('Cond_controller', (0, 0, 0), 'o'): {
            'lab': '(C) Temp Out',
            'off': (4, 0.5, 0),
        },
        ('Cond_controller', (0, 2, 0), 'o'): {
            'lab': '(D) Cond Out',
            'off': (4, 0.5, 0),
        },
        ('Cond_controller', (0, 0, 0), 'p'): {
            'rot': (0, 0, -90),
            'lab': '(A) GND',
            'off': (0.5, -5, 0),
        },
        ('Cond_controller', (1, 0, 0), 'p'): {
            'rot': (0, 0, -90),
            'lab': '(B) +5V',
            'off': (0.5, -5, 0),
        },
    }

    size(drill, (0.75, 0.75, 2))  # to drill holes around the edge
    # rather than diffing out each hole one at a time, merge all holes
    # into `alt` and diff all at once, much cleaner mesh
    alt = new_obj()
    for enum, coord in crange(
        pyb, (0.03, 0.03, 0.5), (0.97, 0.97, 0.5), (2, 16, 1), enum=True
    ):
        key = (pyb.name, enum, 'pybside')
        if key in hole:
            hole[key]['coord'] = coord
        move_to(drill, coord)
        if FINAL:  # slow
            do_bool(alt, drill, "UNION")
            rotate(drill, (0, 0, DR))
        else:
            replicate(drill, "tmp_hole")
    for enum, coord in crange(
        pyb, (0.03, 0.97, 0.5), (0.97, 0.97, 0.5), (12, 1, 1), enum=True
    ):
        key = (pyb.name, enum, 'pybtop')
        if key in hole:
            hole[key]['coord'] = coord
        if enum[0] in (0, 11):
            continue
        move_to(drill, coord)
        if FINAL:  # slow
            do_bool(alt, drill, "UNION")
            rotate(drill, (0, 0, DR))
        else:
            replicate(drill, "tmp_hole")
    do_bool(pyb, alt, "DIFFERENCE")
    delete(alt)

    # "chip" objects with ccb origin
    chip = new_obj("CPU", parent=pyb)
    obj_add(chip)
    size(chip, (11, 11, 1))
    origin(chip, 'ccb', offset=OFFSET)
    move_to(chip, rel_coords(pyb, 'cct'))
    base = replicate(chip, "reset")
    move_to(base, rel_coords(pyb, (0.25, 0.25, 1)))
    size(base, (3, 2, 1))
    knob = replicate(base)
    size(knob, (1.2, 1, 1))
    move_to(knob, rel_coords(base, 'cct'))
    do_bool(base, knob, "UNION")
    delete(knob)
    base = replicate(base, "user")
    move_to(base, rel_coords(pyb, (0.45, 0.25, 1)))
    for n, coord in enumerate(
        crange(pyb, (0.375, 0.02, 1), (0.375, 0.2, 1), (1, 4, 1))
    ):
        led = replicate(chip, "LED")
        if n >= 2:
            rotate(led, (0, 0, 90))
        size(led, (0.5, 0.7, 0.5))
        move_to(led, coord)

    # with cfb origin
    chip = replicate(chip, "USB")
    origin(chip, 'cfb', offset=OFFSET)
    move_to(chip, rel_coords(pyb, (0.2, 0, 1)))
    size(chip, (6, 4, 2))
    chip = replicate(chip, "uSD")
    move_to(chip, rel_coords(pyb, (0.6, 0, 1)))
    size(chip, (11, 5, 2))

    # now add the ~toroid mount points
    origin(cyl, 'lcc', offset=-0.1)
    move_to(cyl, rel_coords(pyb, (1, 0.05, 0.5)))
    do_bool(pyb, cyl, 'UNION')
    rotate(cyl, (0, 0, 180))
    move_to(cyl, rel_coords(pyb, (0, 0.95, 0.5)))
    do_bool(pyb, cyl, 'UNION')
    delete(cyl)

    cond = new_obj("Cond_controller")
    obj_add(cond)
    size(cond, (38, 65, 1))
    translate(cond, (-70, 0, 0))
    cap = new_obj("Cap.", parent=cond)
    obj_add(cap, what='unit_cyl')
    size(cap, (7, 7, 10))
    origin(cap, 'ccb', offset=0.01)
    move_to(cap, rel_coords(cond, (0.35, 0.225, 1)))
    cap = replicate(cap)
    scale(cap, (0.65, 0.65, 0.5))
    move_to(cap, rel_coords(cond, (0.3, 0.12, 1)))

    alt = new_obj()
    size(drill, (3, 3, 3))
    for coord in crange(
        cond, (0.075, 0.05, 0.5), (0.925, 0.95, 0.5), (2, 2, 1)
    ):
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
    size(drill, (0.75, 0.75, 3))
    for enum, coord in crange(
        cond, (0.925, 0.35, 0.5), (0.925, 0.45, 0.5), (1, 3, 1), enum=True
    ):
        key = (cond.name, enum, 'o')
        if key in hole:
            print(key, hole[key], hole[key].get('set'))
            hole[key]['coord'] = coord
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    for enum, coord in crange(
        cond, (0.1, 0.9, 0.5), (0.45, 0.9, 0.5), (6, 1, 1), enum=True
    ):
        key = (cond.name, enum, 's')
        if key in hole:
            print(key, hole[key], hole[key].get('set'))
            hole[key]['coord'] = coord
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    for enum, coord in crange(
        cond, (0.45, 0.05, 0.5), (0.55, 0.05, 0.5), (2, 1, 1), enum=True
    ):
        key = (cond.name, enum, 'p')
        if key in hole:
            print(key, hole[key], hole[key].get('set'))
            hole[key]['coord'] = coord
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    do_bool(cond, alt, "DIFFERENCE")
    delete(alt)

    switch = new_obj("switch", parent=cond)
    obj_add(switch)
    size(switch, (5, 4, 2))
    origin(switch, 'ccb', offset=0.01)
    move_to(switch, rel_coords(cond, (0.15, 0.825, 1)))
    knob = replicate(switch)
    size(knob, (1, 0.5, 0.7))
    for coord in crange(switch, (0.3, 0.3, 1), (0.3, 0.7, 1), (1, 2, 1)):
        move_to(knob, coord)
        do_bool(switch, knob, "UNION")
    delete(knob)

    gps = new_obj("GPS")
    obj_add(gps)
    size(gps, (34, 22, 1))
    translate(gps, (0, 70, 0))
    ant = replicate(gps, "Ant", parent=gps)
    size(ant, (16, 16, 5))
    origin(ant, 'ccb', offset=0.01)
    move_to(ant, rel_coords(gps, 'cct'))

    alt = new_obj()
    size(drill, (3, 3, 3))
    for coord in crange(gps, (0.07, 0.1, 0.5), (0.07, 0.9, 0.5), (1, 2, 1)):
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
    size(drill, (0.75, 0.75, 3))
    for enum, coord in crange(
        gps, (0.95, 0.05, 0.5), (0.95, 0.95, 0.5), (1, 9, 1), enum=True
    ):
        key = (gps.name, enum)
        if key in hole:
            if hole[key].get('set') in (None, 'gps'):
                hole[key]['coord'] = coord
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    do_bool(gps, alt, "DIFFERENCE")
    delete(alt)

    adpt = new_obj("rad.adapt")
    obj_add(adpt)
    size(adpt, (26, 40, 1))
    translate(adpt, (0, 0, 0))

    size(drill, (0.75, 0.75, 3))
    alt = new_obj()
    for enum, coord in crange(
        adpt, (0.07, 0.065, 0.5), (1 - 0.07, 0.065, 0.5), (10, 1, 1), enum=True
    ):
        key = (adpt.name, enum)
        if key in hole:
            if hole[key].get('set') in (None, 'gps'):
                hole[key]['coord'] = coord
        move_to(drill, coord)
        do_bool(alt, drill, "UNION")
        rotate(drill, (0, 0, DR))
    do_bool(adpt, alt, "DIFFERENCE")
    delete(alt)

    blk = new_obj(name='socket', parent=adpt)
    obj_add(blk)
    size(blk, (2.5, 21, 7))
    origin(blk, 'lfb', offset=OFFSET)
    move_to(blk, rel_coords(adpt, (0, 0.35, 1)))
    replicate(blk)
    origin(blk, 'rfb', offset=OFFSET)
    move_to(blk, rel_coords(adpt, (1, 0.35, 1)))

    rad = new_obj('rad', parent=adpt)
    obj_add(rad)
    size(rad, (26, 35, 1))

    origin(rad, 'cbb', offset=OFFSET)
    move_to(rad, rel_coords(adpt, 'cbt') + _v(0, 0, blk.dimensions.z))
    bvl = new_obj()
    obj_add(bvl)
    size(bvl, 40)
    rotate(bvl, (0, 0, 45))
    move_to(bvl, rel_coords(rad, 'ccc') + _v(0, -2.8, 0))
    do_bool(rad, bvl, "INTERSECT")
    delete(bvl)

    cap = new_obj("Cap.", parent=adpt)
    obj_add(cap, what='unit_cyl')
    size(cap, (3, 3, 6.7))
    origin(cap, 'ccb', offset=0.01)
    move_to(cap, rel_coords(adpt, (0.9, 1, 1)) - _v(0, 35, 0))

    d = 2.5
    led = new_obj(name='red', parent=adpt)
    obj_add(led, what='unit_cyl')
    size(led, (d, d, 4))
    top = new_obj()
    obj_add(top, what='uvsphere', u_segments=40, v_segments=40, diameter=1)
    size(top, d - OFFSET)
    move_to(top, rel_coords(led, 'cct'))
    do_bool(led, top, "UNION")
    delete(top)
    origin(led, 'ccb', offset=OFFSET)
    move_to(led, rel_coords(adpt, (0.075, 0.95, 1)))
    grn = replicate(led, name='grn')
    move_to(grn, rel_coords(adpt, (1 - 0.075, 0.95, 1)))

    keys = sorted(hole, key=lambda k: hole[k]['coord'].y)
    text_group = bpy.data.collections.new("Text")
    MATERIALS[:] = ["Text"]
    for key in keys:
        d = hole[key]
        text = new_obj(d['lab'], what='text', parent=key[0])
        text_group.objects.link(text)
        data = text.data
        data.body = d['lab']
        x, y = d.get('g', 'LC')
        data.align_x = TEXT_ALIGN[x]
        data.align_y = TEXT_ALIGN[y]
        data.size = 2.5
        move_to(text, d['coord'] + _v(d.get('off', (0, 0, 0))))
        rotate(text, d.get('rot', (0, 0, 0)))

    delete(drill)
    bind_parents()

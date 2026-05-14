"""Calibration discs for the magnetic thickness gauge.

Emits flat round discs in 1-5mm thicknesses with the thickness engraved
on the top face near the edge (clear of where the housing rests).
Print in any non-magnetic filament (PLA / PETG / nylon are all fine).
"""
from build123d import *

DISC_DIA    = 30.0
THICKNESSES = (1, 2, 3, 4, 5)   # mm
TEXT_SIZE   = 5.0
TEXT_DEPTH  = 0.4
TEXT_X      = 11.0              # radial offset — outside the ~18.6mm housing footprint

for t in THICKNESSES:
    with BuildPart() as disc:
        Cylinder(radius=DISC_DIA / 2, height=t,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Engrave thickness label on top face
        with BuildSketch(Plane.XY.offset(t)):
            with Locations((TEXT_X, 0)):
                Text(f"{t}", font_size=TEXT_SIZE,
                     align=(Align.CENTER, Align.CENTER))
        extrude(amount=-TEXT_DEPTH, mode=Mode.SUBTRACT)

    name = f"disc_{t}mm.step"
    export_step(disc.part, name)
    print(name)

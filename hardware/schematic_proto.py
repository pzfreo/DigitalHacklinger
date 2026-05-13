"""Single-sensor prototype wiring diagram: XIAO ESP32S3 + ADS1219 + SS495A1."""
import matplotlib.pyplot as plt
import matplotlib.patches as mp

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.set_aspect('equal')
ax.axis('off')


def block(x, y, w, h, title, pins_right=None, pins_left=None, subtitle=None):
    """A device block with named pins on the right and/or left edges."""
    ax.add_patch(mp.FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.05",
                                   linewidth=1.8, edgecolor='black',
                                   facecolor='#f7f7f7'))
    ax.text(x + w / 2, y + h - 0.4, title,
            ha='center', va='top', fontsize=12, weight='bold')
    if subtitle:
        ax.text(x + w / 2, y + h - 0.9, subtitle,
                ha='center', va='top', fontsize=8, style='italic', color='gray')
    pin_positions = {}
    if pins_right:
        for i, p in enumerate(pins_right):
            py = y + h - 1.6 - i * 0.55
            ax.plot([x + w, x + w + 0.2], [py, py], 'k-', linewidth=1.5)
            ax.text(x + w - 0.15, py, p, ha='right', va='center', fontsize=10)
            pin_positions[p] = (x + w + 0.2, py)
    if pins_left:
        for i, p in enumerate(pins_left):
            py = y + h - 1.6 - i * 0.55
            ax.plot([x, x - 0.2], [py, py], 'k-', linewidth=1.5)
            ax.text(x + 0.15, py, p, ha='left', va='center', fontsize=10)
            pin_positions[p] = (x - 0.2, py)
    return pin_positions


def wire(p1, p2, color='black', label=None):
    """Manhattan-routed wire between two pin positions, with optional label."""
    x1, y1 = p1
    x2, y2 = p2
    midx = (x1 + x2) / 2
    ax.plot([x1, midx, midx, x2], [y1, y1, y2, y2], color=color, linewidth=1.6)
    if label:
        ax.text(midx, (y1 + y2) / 2 + 0.18, label,
                ha='center', va='bottom', fontsize=9, color=color)


# ── Three device blocks ─────────────────────────────────────────────────────
xiao = block(0.3, 4.0, 2.8, 4.5,
             title="XIAO ESP32S3",
             pins_right=["3V3", "GND", "SDA (D4)", "SCL (D5)"])

ads = block(5.5, 3.0, 3.4, 5.5,
            title="SparkX ADS1219",
            subtitle="VDDA jumper → 3V3",
            pins_left=["3V3", "GND", "SDA", "SCL"],
            pins_right=["VDDA", "GND", "AIN0"])

sens = block(11.3, 4.0, 2.4, 4.5,
             title="SS495A1",
             subtitle="marked face → magnet",
             pins_left=["Vcc", "GND", "Out"])

# ── Wires ───────────────────────────────────────────────────────────────────
wire(xiao["3V3"],      ads["3V3"], color='#c00', label='3.3 V')
wire(xiao["GND"],      ads["GND"])
wire(xiao["SDA (D4)"], ads["SDA"], label='SDA')
wire(xiao["SCL (D5)"], ads["SCL"], label='SCL')

wire(ads["VDDA"], sens["Vcc"], color='#c00', label='Vcc 3.3 V')
wire(ads["GND"],  sens["GND"])
wire(ads["AIN0"], sens["Out"], label='analog → AIN0')

# ── 0.1 µF bypass cap at the sensor ─────────────────────────────────────────
vcc_x, vcc_y = sens["Vcc"]
gnd_x, gnd_y = sens["GND"]
cap_x = vcc_x - 0.6
ax.plot([vcc_x, cap_x], [vcc_y, vcc_y], 'k-', linewidth=1.5)
ax.plot([vcc_x, cap_x], [gnd_y, gnd_y], 'k-', linewidth=1.5)
ax.plot([cap_x, cap_x], [vcc_y, vcc_y - 0.15], 'k-', linewidth=1.5)
ax.plot([cap_x, cap_x], [gnd_y, gnd_y + 0.15], 'k-', linewidth=1.5)
ax.plot([cap_x - 0.3, cap_x + 0.3],
        [vcc_y - 0.35, vcc_y - 0.35], 'k-', linewidth=2.5)
ax.plot([cap_x - 0.3, cap_x + 0.3],
        [gnd_y + 0.35, gnd_y + 0.35], 'k-', linewidth=2.5)
ax.plot([cap_x, cap_x], [vcc_y - 0.15, vcc_y - 0.35], 'k-', linewidth=1.5)
ax.plot([cap_x, cap_x], [gnd_y + 0.15, gnd_y + 0.35], 'k-', linewidth=1.5)
ax.text(cap_x - 0.5, (vcc_y + gnd_y) / 2, '0.1 µF\nbypass',
        ha='right', va='center', fontsize=9)

# ── Notes ───────────────────────────────────────────────────────────────────
notes = (
    "Notes\n"
    "• Qwiic cable carries 3V3 / GND / SDA / SCL in one connector — use it instead of 4 jumpers if you have one.\n"
    "• I2C pull-ups (4.7 kOhm) are already on the SparkX board.\n"
    "• Default I2C address: 0x40.\n"
    "• ADS1219 config: gain 1, internal 2.048 V ref, AIN0 single-ended (vs AVSS), continuous @ 20 SPS.\n"
    "• Magnet (N52, 6 x 5 mm) sits in the housing bore; ball on the far side of the workpiece, on-axis.\n"
    "• If the output reads pinned high (>= 2.048 V) with the magnet present, flip the sensor 180 deg."
)
ax.text(0.3, 2.6, notes, ha='left', va='top', fontsize=9,
        family='monospace',
        bbox=dict(facecolor='#fffbe6', edgecolor='#ddc',
                  boxstyle='round,pad=0.5'))

plt.title("Digital Hacklinger — single-sensor prototype",
          fontsize=14, weight='bold', pad=14)
plt.tight_layout()
plt.savefig('schematic_proto.png', dpi=160, bbox_inches='tight')
print("Saved schematic_proto.png")

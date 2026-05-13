# DigitalHacklinger

A magnetic thickness gauge for measuring instrument plates and purfling strips (1–5mm range) from one side only.

## Principle

A steel ball bearing is placed on the reverse face of the material. A neodymium magnet in the housing holds it through the material. Hall effect sensors detect the field perturbation to calculate thickness.

## Hardware

- Seeed XIAO ESP32S3
- ADC chip — not finalised (prototyping with the SparkX ADS1219 breakout)
- SS495A1 linear Hall effect sensors
- N52 neodymium magnet
- 3–4mm steel ball bearing
- LiPo battery + boost converter (5V rail)
- Small OLED display
- 3D printed nylon housing

## Repository Structure

- `firmware/` — ESP32S3 Arduino/PlatformIO code
- `hardware/` — 3D printed housing designs
- `docs/` — specs, calibration notes, test data

// Digital Hacklinger — single-sensor bring-up.
// Reads SS495A1 → ADS1219 AIN0 single-ended; prints mean + stddev every 10 s.

#include <Arduino.h>
#include <Wire.h>
#include <math.h>

constexpr uint8_t ADS1219_ADDR  = 0x40;   // SparkX board default

// Commands (datasheet table 13)
constexpr uint8_t CMD_RESET     = 0x06;
constexpr uint8_t CMD_START     = 0x08;
constexpr uint8_t CMD_RDATA     = 0x10;
constexpr uint8_t CMD_WREG      = 0x40;

// Config register (datasheet table 14)
//   bits 7:5  MUX = 011  → AIN0 vs AVSS (single-ended)
//   bit  4    GAIN = 0   → 1×
//   bits 3:2  DR  = 00   → 20 SPS
//   bit  1    CM  = 1    → continuous conversions
//   bit  0    VREF = 0   → internal 2.048 V
constexpr uint8_t  CFG_VALUE    = (0b011 << 5) | (0 << 4) | (0b00 << 2) | (1 << 1) | 0;
constexpr float    VREF_MV      = 2048.0f;
constexpr float    FS_COUNTS    = 8388608.0f;   // 2^23 — single-ended range

constexpr uint32_t REPORT_MS    = 10000;        // print every 10 s
constexpr uint32_t SAMPLE_MS    = 50;           // matches 20 SPS

static void sendCmd(uint8_t cmd) {
  Wire.beginTransmission(ADS1219_ADDR);
  Wire.write(cmd);
  Wire.endTransmission();
}

static void writeConfig(uint8_t value) {
  Wire.beginTransmission(ADS1219_ADDR);
  Wire.write(CMD_WREG);
  Wire.write(value);
  Wire.endTransmission();
}

static int32_t readData() {
  Wire.beginTransmission(ADS1219_ADDR);
  Wire.write(CMD_RDATA);
  Wire.endTransmission();
  Wire.requestFrom((uint8_t)ADS1219_ADDR, (uint8_t)3);
  int32_t v = ((int32_t)Wire.read() << 16)
            | ((int32_t)Wire.read() << 8)
            |  (int32_t)Wire.read();
  if (v & 0x800000) v |= 0xFF000000;   // sign-extend 24 → 32
  return v;
}

// Welford accumulator — numerically stable mean/variance over the 10-s window.
static uint32_t n_samples       = 0;
static double   mean_mV         = 0.0;
static double   M2              = 0.0;
static uint32_t window_start_ms = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {}
  Wire.begin();

  delay(50);
  sendCmd(CMD_RESET);
  delay(5);
  writeConfig(CFG_VALUE);
  sendCmd(CMD_START);
  delay(100);   // let the first 20-SPS conversion complete

  Serial.println("# every 10 s: n, mean_mV, sd_mV");
  window_start_ms = millis();
}

void loop() {
  int32_t raw = readData();
  double  mV  = ((double)raw / FS_COUNTS) * VREF_MV;

  // Welford online update
  n_samples++;
  double delta  = mV - mean_mV;
  mean_mV      += delta / n_samples;
  M2           += delta * (mV - mean_mV);

  if (millis() - window_start_ms >= REPORT_MS) {
    double sd = (n_samples > 1) ? sqrt(M2 / (n_samples - 1)) : 0.0;
    Serial.printf("n=%lu  mean=%.4f mV  sd=%.4f mV\n",
                  (unsigned long)n_samples, mean_mV, sd);
    n_samples       = 0;
    mean_mV         = 0.0;
    M2              = 0.0;
    window_start_ms = millis();
  }

  delay(SAMPLE_MS);
}

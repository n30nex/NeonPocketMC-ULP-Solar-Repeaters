#pragma once

#include "DisplayDriver.h"
#include <helpers/RefCountedDigitalPin.h>

#ifndef NV3001B_USE_SOFTWARE_SPI
  #define NV3001B_USE_SOFTWARE_SPI 0
#endif

#ifndef NV3001B_USE_FAST_GPIO
  #define NV3001B_USE_FAST_GPIO 0
#endif

#ifndef NV3001B_USE_FRAMEBUFFER
  #define NV3001B_USE_FRAMEBUFFER 0
#endif

#ifndef NV3001B_USE_INDEXED_FRAMEBUFFER
  #define NV3001B_USE_INDEXED_FRAMEBUFFER 0
#endif

#if NV3001B_USE_INDEXED_FRAMEBUFFER && !NV3001B_USE_FRAMEBUFFER
  #error "NV3001B_USE_INDEXED_FRAMEBUFFER requires NV3001B_USE_FRAMEBUFFER"
#endif

#if NV3001B_USE_FAST_GPIO && !NV3001B_USE_SOFTWARE_SPI
  #error "NV3001B_USE_FAST_GPIO requires NV3001B_USE_SOFTWARE_SPI"
#endif

#if !NV3001B_USE_SOFTWARE_SPI
  #include <SPI.h>
#endif

#ifndef NV3001B_LOGICAL_WIDTH
  #define NV3001B_LOGICAL_WIDTH 128
#endif

#ifndef NV3001B_LOGICAL_HEIGHT
  #define NV3001B_LOGICAL_HEIGHT 64
#endif

#ifndef NV3001B_PANEL_WIDTH
  #define NV3001B_PANEL_WIDTH 128
#endif

#ifndef NV3001B_PANEL_HEIGHT
  #define NV3001B_PANEL_HEIGHT 220
#endif

#if !NV3001B_USE_SOFTWARE_SPI && !defined(NV3001B_SPI_HOST)
  #define NV3001B_SPI_HOST HSPI
#endif

class NV3001BDisplay : public DisplayDriver {
#if !NV3001B_USE_SOFTWARE_SPI
#if !defined(NRF52_PLATFORM)
  SPIClass owned_spi;
#endif
  SPIClass* spi;
  bool external_spi;
#endif
  RefCountedDigitalPin* periph_power;
  bool is_on = false;
  uint16_t color = 0xffff;
  uint8_t text_size = 1;
  int cursor_x = 0;
  int cursor_y = 0;
#if NV3001B_USE_FRAMEBUFFER
#if NV3001B_USE_INDEXED_FRAMEBUFFER
  uint8_t* framebuffer = nullptr;
  static constexpr uint16_t framebuffer_palette_capacity = 256;
  uint16_t framebuffer_palette[framebuffer_palette_capacity] = {};
  uint16_t framebuffer_palette_size = 0;
#else
  uint16_t* framebuffer = nullptr;
#endif
  bool framebuffer_allocation_attempted = false;
  static constexpr uint8_t framebuffer_band_rows = 8;
  static constexpr uint16_t framebuffer_max_dimension =
      NV3001B_PANEL_WIDTH > NV3001B_PANEL_HEIGHT ? NV3001B_PANEL_WIDTH : NV3001B_PANEL_HEIGHT;
  static constexpr uint8_t framebuffer_hash_capacity =
      (framebuffer_max_dimension + framebuffer_band_rows - 1) / framebuffer_band_rows;
  uint64_t framebuffer_band_hashes[framebuffer_hash_capacity] = {};
  bool framebuffer_hashes_valid = false;
  uint8_t framebuffer_flushes_since_full = 0;
#endif

  void beginTransport();
  void beginTransfer();
  void transferByte(uint8_t value);
  void endTransfer();
  void writeCommand(uint8_t cmd);
  void writeBytes(const uint8_t* data, size_t len);
  void writeCommandData(uint8_t cmd, const uint8_t* data, size_t len);
  void setAddrWindow(uint16_t x, uint16_t y, uint16_t w, uint16_t h);
  void writeColor(uint16_t rgb, uint32_t count);
#if NV3001B_USE_FRAMEBUFFER
#if NV3001B_USE_INDEXED_FRAMEBUFFER
  bool framebufferPaletteIndex(uint16_t rgb, uint8_t& index);
#endif
  void flushFramebuffer();
#endif
  void fillPhysicalRect(int x, int y, int w, int h);
  void initPanel();
  void drawChar(int x, int y, char ch);

public:
  NV3001BDisplay(RefCountedDigitalPin* power = nullptr) :
      DisplayDriver(NV3001B_LOGICAL_WIDTH, NV3001B_LOGICAL_HEIGHT)
#if !NV3001B_USE_SOFTWARE_SPI
#if defined(NRF52_PLATFORM)
      , spi(&SPI), external_spi(true)
#else
      , owned_spi(NV3001B_SPI_HOST), spi(&owned_spi), external_spi(false)
#endif
#endif
      , periph_power(power) { }

#if !NV3001B_USE_SOFTWARE_SPI
  NV3001BDisplay(SPIClass& bus, RefCountedDigitalPin* power = nullptr) :
      DisplayDriver(NV3001B_LOGICAL_WIDTH, NV3001B_LOGICAL_HEIGHT)
#if defined(NRF52_PLATFORM)
      , spi(&bus), external_spi(true)
#else
      , owned_spi(NV3001B_SPI_HOST), spi(&bus), external_spi(true)
#endif
      , periph_power(power) { }
#endif

  bool begin();
  static const char* driverName() { return "NV3001B"; }
  static uint16_t physicalWidth() { return NV3001B_PANEL_WIDTH; }
  static uint16_t physicalHeight() { return NV3001B_PANEL_HEIGHT; }

  bool isOn() override { return is_on; }
  void turnOn() override;
  void turnOff() override;
  void clear() override;
  void startFrame(ColorVal bkg = UIColor::window_bkg) override;
  void setTextSize(int sz) override;
  void setColor(ColorVal c) override;
  void setCursor(int x, int y) override;
  void print(const char* str) override;
  void printWordWrap(const char* str, int max_width) override;
  void fillRect(int x, int y, int w, int h) override;
  void drawRect(int x, int y, int w, int h) override;
  void drawXbm(int x, int y, const uint8_t* bits, int w, int h) override;
  uint16_t getTextWidth(const char* str) override;
  void endFrame() override;
};

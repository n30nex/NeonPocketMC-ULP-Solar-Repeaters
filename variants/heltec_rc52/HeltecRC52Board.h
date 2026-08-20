#pragma once

#include <Arduino.h>
#include <helpers/NRF52Board.h>

class HeltecRC52Board : public NRF52BoardDCDC {
protected:
#ifdef NRF52_POWER_MANAGEMENT
  void initiateShutdown(uint8_t reason) override;
#endif

public:
  HeltecRC52Board() : NRF52Board("RC52_OTA") { }
  void begin() override;
  void powerOff() override;
  uint16_t getBattMilliVolts() override;
  const char* getManufacturerName() const override { return "Heltec RC52"; }
};

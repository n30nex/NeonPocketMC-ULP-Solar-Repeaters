#!/usr/bin/env python3
"""Exercise the configurator against synthetic USB CDC replies, without hardware."""

import contextlib
import io
import itertools
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import configure_ulp as wizard


VERSION = "v1.17.1-neonpocket-ulp-v1.0.0-rc.3 (Build: synthetic)"
WIRE_REPLY = f"ver\r\n  -> {VERSION}\r\n".encode()


class SerialTests(unittest.TestCase):
    def setUp(self):
        # PySerial defaults both control lines to active. The nRF52 USB stack
        # drops outgoing bytes unless the host asserts DTR.
        self.port = Mock(dtr=True, rts=True, is_open=True, in_waiting=4096)
        self.chunks = iter(())
        self.port.read.side_effect = lambda _size: next(self.chunks, b"") if self.port.dtr else b""
        self.output = io.StringIO()
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(contextlib.redirect_stdout(self.output))
        stack.enter_context(patch.dict(sys.modules, {"serial": Mock(Serial=lambda: self.port)}))
        stack.enter_context(patch.object(wizard.time, "sleep"))
        stack.enter_context(patch.object(wizard.time, "monotonic", side_effect=itertools.count(0, 0.001)))
        self.device = wizard.Device("/dev/cu.usbmodem-test")
        self.addCleanup(self.device.close)

    def answer(self, chunks, command="ver", **kwargs):
        self.chunks = iter(chunks)
        return self.device.command(command, **kwargs)

    def test_nrf52_version_reply_requires_dtr(self):
        self.assertEqual(self.answer([WIRE_REPLY]), VERSION)
        self.assertIs(self.port.rts, False)
        self.assertEqual(self.port.baudrate, 115200)
        self.port.write.assert_called_once_with(b"ver\r")

    def test_every_usb_split_preserves_the_complete_version(self):
        self.port.dtr = True  # Test framing independently of the control-line fix.
        for split in range(1, len(WIRE_REPLY)):
            with self.subTest(split=split):
                self.assertEqual(self.answer([WIRE_REPLY[:split], WIRE_REPLY[split:]]), VERSION)

    def test_bytewise_reply_and_unsolicited_lines(self):
        self.port.dtr = True
        wire = b"Boot ready\r\n" + WIRE_REPLY
        self.assertEqual(self.answer([bytes([value]) for value in wire]), VERSION)

    def test_silence_and_truncated_replies_timeout_without_retransmitting(self):
        self.port.dtr = True
        for wire in (b"", b"ver\r\n", b"  -> v1.17.1", b"  -> \r\nBoot ready\r\n"):
            with self.subTest(wire=wire):
                self.port.write.reset_mock()
                with self.assertRaisesRegex(wizard.SetupError, "did not answer"):
                    self.answer([wire], timeout=0.1)
                self.port.write.assert_called_once_with(b"ver\r")

    def test_fragmented_device_error_is_rejected(self):
        self.port.dtr = True
        with self.assertRaisesRegex(wizard.SetupError, "Device rejected.*ERR: unsupported"):
            self.answer([b"  -> E", b"RR: unsupported\r\n"])

    def test_secret_echo_is_hidden(self):
        self.port.dtr = True
        password = "synthetic-secret"
        self.answer([f"password {password}\r\n  -> password now: {password}\r\n".encode()],
                    command=f"password {password}", secret=True)
        self.assertNotIn(password, self.output.getvalue())

    def test_other_firmware_is_refused_before_settings_are_written(self):
        self.port.dtr = True
        self.port.read.side_effect = lambda _size: b"  -> other-firmware\r\n"
        with patch.object(wizard, "Device", return_value=self.device):
            with self.assertRaisesRegex(wizard.SetupError, "not NeonPocket ULP"):
                wizard.run("/dev/cu.usbmodem-test")
        self.assertEqual([call.args[0] for call in self.port.write.call_args_list], [b"ver\r", b"board\r"])
        self.port.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()

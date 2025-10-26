#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

from .StreamDeck import StreamDeck, ControlType, DialEventType, TouchscreenEventType


def _dials_rotation_transform(value):
    if value < 0x80:
        # Clockwise rotation
        return value
    else:
        # Counterclockwise rotation
        return -(0x100 - value)


class WaveXLR(StreamDeck):
    KEY_COUNT = 1
    """?"""

    DIAL_COUNT = 4

    DECK_TYPE = "Wave XLR"
    DECK_TOUCH = True

    _DIAL_EVENT_TRANSFORM = {
        DialEventType.TURN: _dials_rotation_transform,
        DialEventType.PUSH: bool,
    }

    def _reset_key_stream(self):
        """payload = bytearray(self._IMG_PACKET_LEN)
        payload[0] = 0x02
        self.device.write(payload)"""

    def reset(self):
        payload = bytearray(32)
        payload[0:2] = [0x03, 0x02]
        self.device.write_feature(payload)

    def _read_control_states(self):
        states = self.device.read(14)

        if states is None:
            return None

        states = states[1:]

        if states[0] == 0x02: # Touchscreen Event
            if states[3] == 1:
                event_type = TouchscreenEventType.SHORT
            elif states[3] == 2:
                event_type = TouchscreenEventType.LONG
            elif states[3] == 3:
                event_type = TouchscreenEventType.DRAG
            else:
                return None

            value = {
                'x': (states[6] << 8) + states[5],
                'y': (states[8] << 8) + states[7]
            }

            if event_type == TouchscreenEventType.DRAG:
                value["x_out"] = (states[10] << 8) + states[9]
                value["y_out"] = (states[12] << 8) + states[11]

            return {
                ControlType.TOUCHSCREEN: (event_type, value),
            }
        elif states[0] == 0x03: # Dial Event
            if states[3] == 0x01:
                event_type = DialEventType.TURN
            elif states[3] == 0x00:
                event_type = DialEventType.PUSH
            else:
                return None

            values = [self._DIAL_EVENT_TRANSFORM[event_type](s) for s in states[4:4 + self.DIAL_COUNT]]

            return {
                ControlType.DIAL: {
                    event_type: values,
                }
            }

    def set_brightness(self, percent):
        return

    def get_serial_number(self):
        serial = self.device.read_feature(0x06, 32)
        return self._extract_string(serial[5:])

    def get_firmware_version(self):
        version = self.device.read_feature(0x05, 32)
        return self._extract_string(version[5:])

    def set_key_image(self, key, image):
        pass

    def set_touchscreen_image(self, image, x_pos=0, y_pos=0, width=0, height=0):
        pass

    def set_key_color(self, key, r, g, b):
        pass

    def set_screen_image(self, image):
        pass

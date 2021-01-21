# -----------------------------------------------------------------------------
# qwiic_alphanumeric_display.py
#
# Python library for the Qwiic alphanumeric display on SparkFun.
#
#   https://www.sparkfun.com/products/16391
#   https://www.sparkfun.com/products/16425
#   https://www.sparkfun.com/products/16426
#   https://www.sparkfun.com/products/16427
#
# ------------------------------------------------------------------------
#
#
# This python library supports the SparkFun Electroncis qwiic
# qwiic sensor/board ecosystem
#
# More information on qwiic is at https:// www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
# ==================================================================================
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==================================================================================
#
#

"""
qwiic_alphanumeric_display
===============
TODO: This
"""
# -----------------------------------------------------------------------------
from __future__ import print_function
import struct

import qwiic_i2c

# Define the device name and I2C addresses. These are set in the class defintion
# as class variables, making them avilable without having to create a class instance.
# This allows higher level logic to rapidly create a index of qwiic devices at
# runtine
#
# The name of this device
_DEFAULT_NAME = "SparkFun Qwiic Alphanumeric Display"

# Some devices have multiple availabel addresses - this is a list of these addresses.
# NOTE: The first address in this list is considered the default I2C address for the
# device.
# TODO: Add other addresses here!
_AVAILABLE_I2C_ADDRESS = [0x70]

# Alpha Commands
ALPHA_CMD_SYSTEM_SETUP = 0b00100000
ALPHA_CMD_DISPLAY_SETUP = 0b10000000
ALPHA_CMD_DIMMING_SETUP = 0b11100000

# Blink rates
ALPHA_BLINK_RATE_NOBLINK = 0b00
ALPHA_BLINK_RATE_2HZ = 0b01
ALPHA_BLINK_RATE_1HZ = 0b10
ALPHA_BLINK_RATE_0_5HZ = 0b11

# define the class that encapsulates the device being created. All information associated with this
# device is encapsulated by this class. The device class should be the only value exported
# from this module.


class QwiicAlphanumericDisplay(object):
    """
    QwiicAlphanumericDisplay

        :param address: The I2C address to use for the device. Included so this
                        follows the same pattern as other drivers, but the `addresses`
                        parameter should typically be used instead.
                        If not provided, the default address is used.
        :param addresses: The address(es) to use for these displays. Chaining them together
                        like this means a message can span an individual display. Addresses
                        should be specified from first char to last (i.e. left to right in 
                        Latin based languages, etc.)
                        If not provided, a single segment with the default address is used.
        :param i2c_driver: An existing i2c driver object. If not provided
                        a driver object is created.
        :return: The QwiicAlphanumericDisplay device object.
        :rtype: Object
    """
    # Constructor
    device_name = _DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS

    # Constructor
    def __init__(self, address=None, addresses=[], i2c_driver=None):

        # Did the user specify I2C addresses?
        if addresses:
            self.addresses = addresses
        elif address:
            self.addresses = [address]
        else:
            self.addresses = [self.available_addresses[0]]

        # load the I2C driver if one isn't provided
        if i2c_driver is None:
            self._i2c = qwiic_i2c.getI2CDriver()
            if self._i2c is None:
                print("Unable to load I2C driver for this platform.")
                return
        else:
            self._i2c = i2c_driver

    # ----------------------------------
    # isConnected()
    #
    # Is an actual board connected to our system?

    def is_connected(self):
        """
            Determine if a device is conntected to the system..

            :return: True if the device is connected, otherwise False.
            :rtype: bool

        """
        connected = False

        # Optimization: we could just exit after the first disconnected display, but
        # I like the idea of pinging them all during this process.
        for display_address in addresses:
            connected &= qwiic_i2c.isDeviceConnected(display_address)
        return connected

    connected = property(is_connected)
    # ----------------------------------
    # begin()
    #
    # Initialize the system/validate the board.

    def begin(self):
        """
            Initialize the operation of the Alphanumeric Display

            :return: Returns true of the initializtion was successful, otherwise False.
            :rtype: bool

        """
        # Make sure everything is connected
        if not self.is_connected():
            return False

        self._init_displays()

        # Basically return True if we are connected...

        return self.is_connected()

    def _init_displays(self, address):
        self.enableSystemClock()
        self.setBrightness(15)
        self.setBlinkRate(ALPHA_BLINK_RATE_NOBLINK)

    def enableSystemClock(self):
        for address in addresses:
            self.enableSingleSystemClock(address)

    def enableSingleSystemClock(self, address):
        self._i2c.writeCommand(address, ALPHA_CMD_SYSTEM_SETUP | 1)
        time.sleep(.01)  # Wait for it to initialize

    # Duty (brightness) valid value between 0 and 15
    # (heh, I said doody)
    def setBrightness(self, duty):
        for address in addresses:
            self.setSingleBrightness(address, duty)

    def setSingleBrightness(self, address, duty):
        if duty > 15:
            duty = 15
        elif duty < 0:
            duty = 0
        self._i2c.writeCommand(address, ALPHA_CMD_DIMMING_SETUP | duty)

    def setBlinkRate(self, blinkRate):
        for address in addresses:
            self.setSingleBlinkRate(address, blinkRate)

    def setSingleBlinkRate(self, address, blinkRate):
        self._i2c.writeCommand(
            address, ALPHA_CMD_DISPLAY_SETUP | (blinkRate << 1))
    # ----------------------------------------------------------------
    # clear_interrupts()
    #
    # Clears the moved bit

    def clear_interrupts(self):
        """
            Clears the moved bit

            :return: No return Value

        """
        self._i2c.writeByte(self.address, QDER_STATUS, 0)

    # ----------------------------------------------------------------
    # get_count1()
    #
    # Returns the number of "ticks" the encoder1 has turned

    def get_count1(self):
        """
            Returns the number of "ticks" the encoder1 has turned

            :return: number of encoder pulses
            :rtype: word as integer

        """
        c1 = self._i2c.readWord(self.address, QDER_COUNT1)
        # encoder reader returns a SIGNED 16 bit int
        # python receives this as simply 16 bits of data
        # we need to accept negative values
        if c1 > 32767:
            c1 -= 65536
        return c1

    # ----------------------------------------------------------------
    # get_count2()
    #
    # Returns the number of "ticks" the encoder2 has turned

    def get_count2(self):
        """
            Returns the number of "ticks" the encoder2 has turned

            :return: number of encoder pulses
            :rtype: word as integer

        """
        c2 = self._i2c.readWord(self.address, QDER_COUNT2)
        # encoder reader returns a SIGNED 16 bit int
        # python receives this as simply 16 bits of data
        # we need to accept negative values
        if c2 > 32767:
            c2 -= 65536
        return c2

    # ----------------------------------------------------------------
    # set_count1()
    #
    # Set the encoder count1 to a specific amount
    def set_count1(self, amount):
        """
            Set the encoder count1 to a specific amount

            :param amount: the value to set the counter to
            :return: no return value

        """

        return self._i2c.writeWord(self.address, QDER_COUNT1, amount)

    # ----------------------------------------------------------------
    # set_count2()
    #
    # Set the encoder count2 to a specific amount
    def set_count2(self, amount):
        """
            Set the encoder count2 to a specific amount

            :param amount: the value to set the counter to
            :return: no return value

        """

        return self._i2c.writeWord(self.address, QDER_COUNT2, amount)

    count1 = property(get_count1, set_count1)
    count2 = property(get_count2, set_count2)

    # ----------------------------------------------------------------
    # get_limit()
    #
    # Returns the limit of allowed counts before wrapping. 0 is disabled

    def get_limit(self):
        """
            Returns the limit of allowed counts before wrapping. 0 is disabled

            :return: The limit
            :rtype: integer

        """
        return self._i2c.readWord(self.address, QDER_LIMIT)

    # ----------------------------------------------------------------
    # set_limit()
    #
    # Set the encoder count limit to a specific amount

    def set_limit(self, amount):
        """
            Set the encoder count limit to a specific amount

            :param amount: the value to set the limit to
            :return: no return value

        """
        return self._i2c.writeWord(self.address, QDER_LIMIT, amount)

    limit = property(get_limit, set_limit)

    # ----------------------------------------------------------------
    # get_diff()
    #
    # Returns the number of ticks since last check

    def get_diff(self, clear_value=False):
        """
            Returns the number of ticks since last check

            :param clearValue: Set to True to clear the current value. Default is False

            :return: the difference
            :rtype: integer

        """
        difference = self._i2c.readWord(self.address, QDER_DIFFERENCE1)

        if clear_value:
            self._i2c.writeWord(self.address, QDER_DIFFERENCE1, 0)

        return difference

    # ----------------------------------------------------------------
    # has_moved()
    #
    # Returns true if encoder has moved

    def has_moved(self):
        """
            Returns true if encoder has moved

            :return: Moved state
            :rtype: Boolean

        """
        status = self._i2c.readByte(self.address, QDER_STATUS)

        self._i2c.writeByte(self.address, QDER_STATUS,
                            status & ~(1 << _statusEncoderMovedBit))

        return (status & (1 << _statusEncoderMovedBit)) != 0

    moved = property(has_moved)
    # ----------------------------------------------------------------
    # since_last_movement()
    #
    # Returns the number of milliseconds since the last encoder movement
    # By default, clear the current value

    def since_last_movement(self, clear_value=True):
        """
            Returns the number of milliseconds since the last encoder movement
            By default, clear the current value

            :param clearValue: Clear out the value? True by default

            :return: time since last encoder movement
            :rtype: integer

        """
        time_elapsed = self._i2c.readWord(
            self.address, QDER_LAST_ENCODER_EVENT)

        # Clear the current value if requested
        if clear_value:
            self._i2c.writeWord(QDER_LAST_ENCODER_EVENT, 0)

        return time_elapsed

    # ----------------------------------------------------------------
    # get_version()
    #
    # Returns a int of the firmware version number

    def get_version(self):
        """
        Returns a integer of the firmware version number

        :return: The firmware version
        :rtype: integer
        """
        return self._i2c.readWord(self.address, QDER_VERSION)

    version = property(get_version)

    # ----------------------------------------------------------------
    # set_int_timeout()
    #
    # Set number of milliseconds that elapse between end of encoder turning and interrupt firing

    def set_int_timeout(self, timeout):
        """
            Set number of milliseconds that elapse between end of encoder turning and interrupt firing

            :param timeout: the timeout value in milliseconds

            :return: No return value

        """
        self._i2c.writeWord(self.address, QDER_TURN_INT_TIMEOUT, timeout)

    # ----------------------------------------------------------------
    # get_int_timeout()
    #
    # Get number of milliseconds that elapse between end of encoder turning and interrupt firing

    def get_int_timeout(self):
        """
            Get number of milliseconds that elapse between end of encoder turning and interrupt firing

            :return: the timeout value
            :rtype: integer

        """
        return self._i2c.readWord(self.address, QDER_TURN_INT_TIMEOUT)

    int_timeout = property(get_int_timeout, set_int_timeout)

# Copyright (c) 2025, Victor Chavez (vchavezb@protonmail.com)
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Custom HCI Commands for Zephyr-based HCI driver
for use with Bumble
"""
from bumble.controller import Controller
from bumble.hci import HCI_SUCCESS, HCI_Command, hci_vendor_command_op_code

HARDWARE_PLATFORM = 0x1234
HARDWARE_VARIANT = 0x5678
FIRMWARE_VARIANT = 0x01
FIRMWARE_VERSION = 0x0
FIRMWARE_REVISION = 0x0
FIRMWARE_BUILD = 0x202

HCI_ZEPHYR_VS_INF_COMMAND = hci_vendor_command_op_code(0x0001)
HCI_ZEPHYR_VS_SUPPORTED_COMMANDS_COMMAND = hci_vendor_command_op_code(0x0002)


HCI_Command.register_commands(globals())


def on_hci_zephyr_vs_inf_command(self, command):
    """
    See
    https://github.com/zephyrproject-rtos/zephyr/blob/f537cf311d7ad19ba00221f9022b7dc4c2daef43/doc/connectivity/bluetooth/api/hci.txt#L161
    """
    response = (
        bytes([HCI_SUCCESS])  # Success code
        + HARDWARE_PLATFORM.to_bytes(2, "little")  # Hardware Platform (2 bytes)
        + HARDWARE_VARIANT.to_bytes(2, "little")  # Hardware Variant (2 bytes)
        + bytes([FIRMWARE_VARIANT])  # Firmware Variant (1 byte)
        + bytes([FIRMWARE_VERSION])  # Firmware Version (1 byte)
        + FIRMWARE_REVISION.to_bytes(2, "little")  # Firmware Revision (2 bytes)
        + FIRMWARE_BUILD.to_bytes(4, "little")  # Firmware Build (4 bytes)
    )
    return response


def on_hci_zephyr_vs_supported_commands_command(self, command):
    """
    See
    https://github.com/zephyrproject-rtos/zephyr/blob/f537cf311d7ad19ba00221f9022b7dc4c2daef43/doc/connectivity/bluetooth/api/hci.txt#L248
    """
    return bytes([HCI_SUCCESS]) + bytes([0])


def load_hci_zephyr_vs_commands():
    """
    Load custom HCI Zephyr vendor specific commands into the controller.
    This is necessary to ensure that the controller can handle these commands.
    """
    Controller.on_hci_zephyr_vs_inf_command = on_hci_zephyr_vs_inf_command
    Controller.on_hci_zephyr_vs_supported_commands_command = (
        on_hci_zephyr_vs_supported_commands_command
    )

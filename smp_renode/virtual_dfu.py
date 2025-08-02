# Copyright (c) 2025, Victor Chavez (vchavezb@protonmail.com)
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import asyncio
import logging
import pathlib

from smp_renode.simulator import run_simulator
from smp_renode.smp_ble import upload_firmware

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


bleak_logger = logging.getLogger("bumble")
# Bleak logger only with info to avoid getting
# to much information from BLE low-level HCI commands
bleak_logger.setLevel(logging.INFO)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Virtual BLE DFU Demo with Renode for NRF52840"
    )
    parser.add_argument(
        "app_hex",
        help="Path to the NRF52840 merged application (Mcuboot+App)"
        "It is assumed that SMP Server is built in app, and HCI"
        "is bridged to UART0",
    )
    parser.add_argument("dfu_bin", help="Binary with DFU image")
    parser.add_argument(
        "--port", type=int, default=1234, help="HCI port to connect to."
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="HCI Port open timeout."
    )

    port = parser.parse_args().port
    app_hex = parser.parse_args().app_hex
    if not pathlib.Path(app_hex).exists():
        raise FileNotFoundError(f"Application hex file {app_hex} does not exist.")

    dfu_bin = pathlib.Path(parser.parse_args().dfu_bin)
    await run_simulator(port, app_hex)
    await upload_firmware(dfu_bin)


if __name__ == "__main__":
    asyncio.run(main())

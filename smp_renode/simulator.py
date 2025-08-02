# Copyright (c) 2025, Victor Chavez (vchavezb@protonmail.com)
# SPDX-License-Identifier: GPL-3.0-or-later
import socket
from pyrenode3.wrappers import Emulation, Monitor, Peripheral, Machine
from pyrenode3 import RPath
from Antmicro.Renode.Core.Extensions import FileLoaderExtensions
from Antmicro.Renode.Peripherals.UART import IUART
from Antmicro.Renode.Time import TimeInterval
import logging
import asyncio
from typing import Dict
from smp_renode.hci_custom import load_hci_zephyr_vs_commands
import time

_APP_LOG_PORT = 4567
nrf52840_flash_repo = (
    "https://raw.githubusercontent.com/vChavezB/renode-nrf52840_flash/refs/heads/main"
)


logger = logging.getLogger(__name__)


load_hci_zephyr_vs_commands()


def get_uart_peripherals(machine: Machine) -> Dict[str, IUART]:
    """
    Get all IUART peripherals from a renode machine.
    Previously, it was attempted to directly retrieve them
    from object device.sysbus.uartX alas they are of type IPeripheral.
    We need the IUART interface to use the method e.Connector.Connect
    :param machine: Renode machine object
    :return: Dictionary mapping UART names to IUART peripherals
    """
    uarts = dict()
    peripherals = list(machine.GetPeripheralsOfType[IUART]())
    for p in peripherals:
        name = Peripheral(p).name
        uarts[name] = p
    return uarts


async def wait_hci_open(port: int, host: str = "127.0.0.1", timeout: int = 10):
    """
    Wait for Virtual HCI created with Renode to open on the specified port
    :param port: Port to check for HCI connection
    :param host: Host to check for HCI connection
    :param timeout: Timeout in seconds to wait for the port to open
    """
    start_time = time.time()
    logger.info(f"Waiting for port {port} on {host} to open (timeout {timeout} s).")
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            try:
                s.connect((host, port))
                logger.info(f"Port {port} on {host} is open.")
                return True
            except (socket.timeout, ConnectionRefusedError):
                if time.time() - start_time > timeout:
                    raise Exception(
                        f"Timeout: Port {port} on {host} did not open within {timeout} seconds."
                    )
                await asyncio.sleep(0.1)


async def run_simulator(hci_port: int, application_path: str) -> None:
    """
    Run the renode simulator with the nRF52840 platform
    with an application that uses HCI over serial
    :param hci_port: Port to use for HCI communication
    :return: None
    """
    e = Emulation()
    m = Monitor()

    # Tested value for reliable simulation
    e.SetGlobalQuantum(TimeInterval.FromMicroseconds(100))

    # Load external driver to simulate NVCM flash peripheral
    res = m.Parse(f"include @{nrf52840_flash_repo}/nrf52840_nvcm.cs")
    print("Load NVCM Res", res)
    device = e.add_mach("nrf")
    device.load_repl("platforms/cpus/nrf52840.repl")
    device.load_repl(f"{nrf52840_flash_repo}/nrf52840_flash.repl")

    device.sysbus.cpu.PerformanceInMips = 100

    # Load application
    app_path = RPath(application_path).read_file_path
    FileLoaderExtensions.LoadHEX(device.sysbus.internal, app_path)

    # Open renode socket for HCI communication
    e.CreateServerSocketTerminal(hci_port, "hci", False, False)
    # Create a socket to monitor Logs from application
    e.CreateServerSocketTerminal(_APP_LOG_PORT, "term", False, False)
    logger.info(
        f"Created HCI socket on port {hci_port} and log terminal on port {_APP_LOG_PORT}"
    )

    # Connect Uarts to external sockets
    uarts = get_uart_peripherals(device)
    e.Connector.Connect(uarts["uart1"], e.externals.hci)
    e.Connector.Connect(uarts["uart0"], e.externals.term)
    """
    def uart0_callback(char):
        print(chr(char), end="")
    uarts["uart0"].CharReceived += uart0_callback
    """
    e.StartAll()
    await wait_hci_open(hci_port)

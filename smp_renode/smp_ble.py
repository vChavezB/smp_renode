# Copyright (c) 2025, Victor Chavez (vchavezb@protonmail.com)
# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio
import logging
import time
from typing import Final

from bleak import BLEDevice
from rich.progress import (BarColumn, DownloadColumn, Progress, TextColumn,
                           TimeRemainingColumn, TransferSpeedColumn)
from smpclient import SMPClient
from smpclient.generics import SMPRequest, TEr1, TEr2, TRep, error, success
from smpclient.mcuboot import IMAGE_TLV, ImageInfo
from smpclient.requests.image_management import (ImageStatesRead,
                                                 ImageStatesWrite)
from smpclient.requests.os_management import ResetWrite
from smpclient.transport.ble import SMPBLETransport

logger = logging.getLogger(__name__)


async def ensure_request(
    client: SMPClient, request: SMPRequest[TRep, TEr1, TEr2]
) -> TRep | TEr1 | TEr2:
    response = await client.request(request)
    if success(response):
        return response
    elif error(response):
        raise Exception(f"Received error: {response}")
    else:
        raise Exception(f"Unknown response: {response}")


async def read_image_states(client: SMPClient):
    response = await client.request(ImageStatesRead())
    if success(response):
        images = response.images
        for img in images:
            logging.info(
                f"Image slot: {img.slot} version {img.version} active {img.active} bootable {img.bootable} confirmed {img.confirmed} pending {img.pending} hash: {img.hash.hex()} "
            )
        return response
    elif error(response):
        raise Exception(f"Received error: {response}")
    else:
        raise Exception(f"Unknown response: {response}")


async def get_ble_device() -> BLEDevice:
    devices = await SMPBLETransport.scan(timeout=10)
    if not devices:
        raise RuntimeError("No BLE devices found.")
    return devices[0]


async def upload_firmware(dfu_bin: str):
    with open(dfu_bin, "rb") as f:
        fw_file: Final = f.read()
    fw_hash: Final = ImageInfo.load_file(str(dfu_bin)).get_tlv(IMAGE_TLV.SHA256)
    device = await get_ble_device()

    async with SMPClient(SMPBLETransport(), device.name or device.address) as client:

        await read_image_states(client)
        start_s = time.time()
        with Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(
                "Uploading", filename=dfu_bin.name, total=len(fw_file), start=True
            )
            async for offset in client.upload(fw_file, 1, upgrade=True):
                progress.update(task, completed=offset)

        logger.info(f"Upload time (s): {time.time() - start_s:.2f}")
        logger.info("\n--------------------------------[State read]")
        rsp = await read_image_states(client)
        assert rsp.images[1].hash == fw_hash.value
        assert rsp.images[1].slot == 1
        logger.info("--------------------------------[Write state]")
        await ensure_request(client, ImageStatesWrite(hash=rsp.images[1].hash))
        logger.info("--------------------------------[Resetting]")
        await ensure_request(client, ResetWrite())
        # wait for reboot
        await asyncio.sleep(5)

    # Check if image was uploaded successfully
    device = await get_ble_device()
    async with SMPClient(
        SMPBLETransport(), device.name or device.address
    ) as client:
        await read_image_states(client)

# SMP Renode

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform: NRF52840](https://img.shields.io/badge/Platform-NRF52840-green)
![Status: PoC](https://img.shields.io/badge/Status-Proof%20of%20Concept-yellow)

> 🚀 A proof-of-concept project to simulate a bootloader using the **NRF52840** platform and **SMP Server** with Renode and Bumble HCI over serial.

---

## 📚 Overview

**SMP Renode** enables full virtual firmware upgrade workflows by simulating an BLE SMP Server.

Internally this module uses

- [SMP Client](https://github.com/intercreate/smpclient) - Implementation in python of a [Simple Management Protocol](https://docs.zephyrproject.org/4.2.0/services/device_mgmt/smp_protocol.html) client.
- [Bumble](https://github.com/google/bumble) - Virtual HCI Controller
- [Renode](https://renode.io/) - Simulator tool for MCUs
---

## 🔧 How to Use

<details>
<summary><strong>1. Build and Merge the SMP Demo (Optional)</strong></summary>

Build the Zephyr-based SMP demo for the NRF52840 platform. HCI is bridged via UART to use the Bumble controller.

> 🔧 A pre-built hex file is already available at:  
> `zephyr/hex/smp_hci_uart_nrf52840.hex`

### ✅ Build from source:

```bash
git clone https://github.com/vChavezB/smp_renode
cd smp_renode/zephyr
west init -l smp_hci_uart
west build --sysbuild -b nrf52840dk/nrf52840 smp_hci_uart
```

### 🧩 Merge MCUBoot and App:

Use `srec_cat` to combine MCUBoot and the signed application into a single hex image.

```bash
srec_cat build/mcuboot/zephyr/zephyr.hex -Intel \
         build/smp_hci_uart/zephyr/zephyr.signed.hex -Intel \
         -o nrf52840_smp_ble_uart.hex -intel
```

</details>

<details>
<summary><strong>2. Install Dependencies</strong></summary>

Python

```bash
poetry install
```

Renode

```bash
mkdir renode_portable
wget https://builds.renode.io/renode-latest.linux-portable.tar.gz
tar xf  renode-latest.linux-portable.tar.gz -C renode_portable --strip-components=1
cd renode_portable
export PATH="`pwd`:$PATH"
sudo apt-get install mono-devel -y
```

</details>

<details>
<summary><strong>3. Configure Bumble as Backend for Bleak</strong></summary>

```bash
export BLEAK_BUMBLE=tcp-client:127.0.0.1:1230
```

</details>

<details>
<summary><strong>4. Run the Virtual DFU Demo</strong></summary>

```bash
poetry run python3 virtual_dfu.py \
  zephyr/hex/smp_hci_uart_nrf52840.hex \
  zephyr/dfu/2.0.1.bin \
  --port=1230 --timeout=20
```

### 🧾 Arguments:
| Argument    | Description                                  |
|-------------|----------------------------------------------|
| `arg 1`     | NRF52840 firmware image with SMP + MCUBoot   |
| `arg 2`     | DFU binary image                             |
| `--port`    | HCI socket for Renode                        |
| `--timeout` | Timeout in seconds for Renode session        |

</details>

---

## 🗂️ Project Structure

```text
smp_renode/
├── zephyr/
│   ├── dfu/                 # DFU binaries
│   ├── hex/                 # Pre-built hex files
│   └── smp_hci_uart/        # SMP BLE app
├── smp_renode               # source files
├── pyproject.toml           # Poetry configuration
└── README.md                # This readme
```

---

## 📜 License

This project is licensed under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html).

---



## 💬 Contributions

Feel free to fork, open issues, or submit pull requests.

---

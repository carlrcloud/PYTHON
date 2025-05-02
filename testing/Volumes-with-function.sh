#!/bin/bash
set -euo pipefail

ROOT_DEVICE=$(lsblk -no PKNAME "$(findmnt -n -o SOURCE /)")
DEVICE=$(lsblk -b -o NAME,SIZE,TYPE,MOUNTPOINTS | awk -v root="$ROOT_DEVICE" '$2 == 53687091200 && $1 !~ root {print "/dev/" $1}' | head -n 1)

# Create PV and VG
sudo pvcreate "$DEVICE"
sudo vgcreate rootvg "$DEVICE"

# Helper to create and mount LV
create_lv_and_mount() {
  local lv_name=$1
  local mount_point=$2
  local size=$3
  local device="/dev/mapper/rootvg-${lv_name}"

  sudo lvcreate -n "$lv_name" -L "$size" rootvg
  sudo mkfs.xfs "$device"
  sudo mkdir -p "$mount_point"
  sudo mount "$device" "$mount_point"

  # Move data if exists
  if [ -d "${mount_point}.bak" ]; then
    sudo rsync -aAX "${mount_point}.bak/" "${mount_point}/"
  fi

  # Write to fstab if not present
  if ! grep -qsE "^[^#].*\s${mount_point}\s" /etc/fstab; then
    echo "${device}  ${mount_point}  xfs  defaults  0 2" | sudo tee -a /etc/fstab
  fi
}

# Logical Volumes with sizes and targets
create_lv_and_mount "opt" "/opt" "3G"
create_lv_and_mount "tmp" "/tmp" "2G"
create_lv_and_mount "var" "/var" "5G"
create_lv_and_mount "log" "/var/log" "3G"
create_lv_and_mount "audit" "/var/log/audit" "1G"
create_lv_and_mount "home" "/home" "5G"
create_lv_and_mount "local" "/usr/local" "3G"

# Reload systemd to pick up any fstab changes
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo mount -a
df -h

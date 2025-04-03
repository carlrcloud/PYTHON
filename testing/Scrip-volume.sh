#!/bin/bash
set -eux

# Install LVM tools if missing
sudo yum install -y lvm2 || sudo apt-get install -y lvm2

# Auto-detect unmounted 50 GB disk
DEVICE=$(lsblk -b -o NAME,SIZE,TYPE,MOUNTPOINT -dn | awk '$2 == 53687091200 && $3 == "disk" && $4 == "" { print "/dev/" $1; exit }')

if [ -z "$DEVICE" ]; then
  echo "ERROR: No unmounted 50 GB disk found!"
  lsblk -b -o NAME,SIZE,TYPE,MOUNTPOINT
  exit 1
fi

echo "Using disk: $DEVICE"
sudo pvcreate "$DEVICE"
sudo vgcreate rootvg "$DEVICE"

# Create and format logical volumes
sudo lvcreate -n opt   -L 5G rootvg
sudo lvcreate -n tmp   -L 5G rootvg
sudo lvcreate -n local -L 3G rootvg
sudo lvcreate -n home  -L 5G rootvg
sudo lvcreate -n var   -L 5G rootvg
sudo lvcreate -n log   -L 1G rootvg
sudo lvcreate -n audit -L 1G rootvg

for lv in opt tmp local home var log audit; do
  sudo mkfs.xfs /dev/mapper/rootvg-$lv
done

# Temporary mount location
sudo mkdir -p /mnt/lvm

# Home
sudo mount /dev/mapper/rootvg-home /mnt/lvm
sudo cp -Rp /home/ec2-user /mnt/lvm || true
sudo umount /mnt/lvm

# Var, log, audit
sudo mount /dev/mapper/rootvg-var /mnt/lvm
sudo mkdir -p /mnt/lvm/log
sudo mount /dev/mapper/rootvg-log /mnt/lvm/log
sudo mkdir -p /mnt/lvm/log/audit
sudo mount /dev/mapper/rootvg-audit /mnt/lvm/log/audit
sudo cp -Rp /var/* /mnt/lvm || true
sudo umount /mnt/lvm/log/audit || true
sudo umount /mnt/lvm/log || true
sudo umount /mnt/lvm || true

# Tmp
sudo mount /dev/mapper/rootvg-tmp /mnt/lvm
sudo cp -Rp /tmp/* /mnt/lvm || true
sudo umount /mnt/lvm || true

# Local
sudo mount /dev/mapper/rootvg-local /mnt/lvm
sudo cp -Rp /usr/local/* /mnt/lvm || true
sudo umount /mnt/lvm || true

# Opt
sudo mount /dev/mapper/rootvg-opt /mnt/lvm
sudo cp -Rp /opt/* /mnt/lvm || true
sudo umount /mnt/lvm || true

# Create final mount points
sudo mkdir -p /home /opt /tmp /usr/local /var/log/audit

# Clean fstab entries using /dev/mapper
sudo tee /etc/fstab > /dev/null <<EOF
/dev/mapper/rootvg-opt    /opt            xfs defaults 0 0
/dev/mapper/rootvg-tmp    /tmp            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-local  /usr/local      xfs defaults 0 0
/dev/mapper/rootvg-home   /home           xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-var    /var            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-log    /var/log        xfs defaults,nodev,noexec,nosuid 0 0
/dev/mapper/rootvg-audit  /var/log/audit  xfs defaults,nodev,noexec,nosuid 0 0
EOF

# Mount and reload
sudo mount -a
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "LVM storage setup complete."

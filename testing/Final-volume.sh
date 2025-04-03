#!/bin/bash
set -eux

# Create PV and VG on /dev/sdb
sudo pvcreate /dev/sdb
sudo vgcreate rootvg /dev/sdb

# Create and format LVs
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

# Create mount points
sudo mkdir -p /opt /tmp /usr/local /home /var/log/audit

# Optional: Copy content to volumes if needed (no-op if empty)
sudo mkdir -p /mnt/lvm

for lv in home var tmp opt local; do
  sudo mount /dev/mapper/rootvg-${lv} /mnt/lvm
  [ -d /$lv ] && [ "$(ls -A /$lv 2>/dev/null)" ] && sudo cp -Rp /$lv/* /mnt/lvm || echo "/$lv is empty or missing"
  sudo umount /mnt/lvm
done

# Handle nested mounts for log/audit
sudo mount /dev/mapper/rootvg-var /mnt/lvm
sudo mkdir -p /mnt/lvm/log
sudo mount /dev/mapper/rootvg-log /mnt/lvm/log
sudo mkdir -p /mnt/lvm/log/audit
sudo mount /dev/mapper/rootvg-audit /mnt/lvm/log/audit
[ -d /var/log/audit ] && sudo cp -Rp /var/log/audit/* /mnt/lvm/log/audit || echo "Audit log empty or missing"
sudo umount /mnt/lvm/log/audit || true
sudo umount /mnt/lvm/log || true
sudo umount /mnt/lvm || true

# Deduplicate /etc/fstab and write clean entries
sudo cp /etc/fstab /etc/fstab.bak.$(date +%s)
sudo sed -i '/\/dev\/mapper\/rootvg-/d' /etc/fstab

cat <<EOF | sudo tee -a /etc/fstab > /dev/null
/dev/mapper/rootvg-opt    /opt            xfs defaults 0 0
/dev/mapper/rootvg-tmp    /tmp            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-local  /usr/local      xfs defaults 0 0
/dev/mapper/rootvg-home   /home           xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-var    /var            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-log    /var/log        xfs defaults,nodev,noexec,nosuid 0 0
/dev/mapper/rootvg-audit  /var/log/audit  xfs defaults,nodev,noexec,nosuid 0 0
EOF

# Create target directory for your app/user
sudo mkdir -p /home/company-name

echo "LVM setup complete. Clean /etc/fstab written and /home/company-name prepared."

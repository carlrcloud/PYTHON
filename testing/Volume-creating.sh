#!/bin/bash
set -eux

# Ensure the LVM tools are available
sudo yum install -y lvm2 || sudo apt-get install -y lvm2

# Step 1: Create Physical Volume and Volume Group
sudo pvcreate /dev/sdb
sudo vgcreate rootvg /dev/sdb
DEVICE=$(lsblk -b -o NAME,SIZE -dn | awk '$2 == 500107862016 { print "/dev/" $1 }')
sudo pvcreate $DEVICE
sudo vgcreate rootvg $DEVICE

# Step 2: Create Logical Volumes
sudo lvcreate -n opt   -L 5G  rootvg
sudo lvcreate -n tmp   -L 5G  rootvg
sudo lvcreate -n local -L 3G  rootvg
sudo lvcreate -n home  -L 5G  rootvg
sudo lvcreate -n var   -L 5G  rootvg
sudo lvcreate -n log   -L 1G  rootvg
sudo lvcreate -n audit -L 1G  rootvg

# Step 3: Format Logical Volumes
for lv in opt tmp local home var log audit; do
  sudo mkfs.xfs /dev/mapper/rootvg-${lv}
done

# Step 4: Temporary Mount and Data Copy
sudo mkdir -p /mnt/lvm

# Home
sudo mount /dev/mapper/rootvg-home /mnt/lvm
sudo cp -Rp /home/* /mnt/lvm || true
sudo umount /mnt/lvm

# Var, log, audit
sudo mount /dev/mapper/rootvg-var /mnt/lvm
sudo mkdir -p /mnt/lvm/log /mnt/lvm/log/audit
sudo mount /dev/mapper/rootvg-log /mnt/lvm/log
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

# Step 5: Create Required Mount Points
sudo mkdir -p /home /opt /tmp /usr/local /var/log/audit

# Step 6: Write Clean /etc/fstab
sudo tee /etc/fstab > /dev/null <<EOF
/dev/mapper/rootvg-opt    /opt            xfs defaults 0 0
/dev/mapper/rootvg-tmp    /tmp            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-local  /usr/local      xfs defaults 0 0
/dev/mapper/rootvg-home   /home           xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-var    /var            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-log    /var/log        xfs defaults,nodev,noexec,nosuid 0 0
/dev/mapper/rootvg-audit  /var/log/audit  xfs defaults,nodev,noexec,nosuid 0 0
EOF

# Step 7: Mount All and Reload Daemons
sudo mount -a
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "LVM setup complete. All mount points created and active."

name: ConfigureLVMStorage
description: Set up LVM volumes using /dev/sdb and mount them with clean /etc/fstab entries
schemaVersion: 1.0
phases:
  build:
    commands:
      - |
        set -eux

        # Prepare LVM using /dev/sdb (50 GB volume)
        sudo pvcreate /dev/sdb
        sudo vgcreate rootvg /dev/sdb

        # Create logical volumes
        sudo lvcreate -n opt   -L 5G  rootvg
        sudo lvcreate -n tmp   -L 5G  rootvg
        sudo lvcreate -n local -L 3G  rootvg
        sudo lvcreate -n home  -L 5G  rootvg
        sudo lvcreate -n var   -L 5G  rootvg
        sudo lvcreate -n log   -L 1G  rootvg
        sudo lvcreate -n audit -L 1G  rootvg

        # Format volumes
        for lv in opt tmp local home var log audit; do
          sudo mkfs.xfs /dev/mapper/rootvg-${lv}
        done

        # Temporary mount point
        sudo mkdir -p /mnt/lvm

        # Copy existing data to logical volumes (optional/safe)
        sudo mount /dev/mapper/rootvg-home /mnt/lvm
        sudo cp -Rp /home/* /mnt/lvm || true
        sudo umount /mnt/lvm

        sudo mount /dev/mapper/rootvg-var /mnt/lvm
        sudo mkdir -p /mnt/lvm/log /mnt/lvm/log/audit
        sudo mount /dev/mapper/rootvg-log /mnt/lvm/log
        sudo mount /dev/mapper/rootvg-audit /mnt/lvm/log/audit
        sudo cp -Rp /var/* /mnt/lvm || true
        sudo umount /mnt/lvm/log/audit || true
        sudo umount /mnt/lvm/log || true
        sudo umount /mnt/lvm || true

        sudo mount /dev/mapper/rootvg-tmp /mnt/lvm
        sudo cp -Rp /tmp/* /mnt/lvm || true
        sudo umount /mnt/lvm || true

        sudo mount /dev/mapper/rootvg-local /mnt/lvm
        sudo cp -Rp /usr/local/* /mnt/lvm || true
        sudo umount /mnt/lvm || true

        sudo mount /dev/mapper/rootvg-opt /mnt/lvm
        sudo cp -Rp /opt/* /mnt/lvm || true
        sudo umount /mnt/lvm || true

        # Create necessary directories before mounting
        sudo mkdir -p /home /opt /tmp /usr/local /var/log/audit

        # Write clean /etc/fstab using /dev/mapper paths (no duplicates)
        sudo tee /etc/fstab > /dev/null <<EOF
/dev/mapper/rootvg-opt    /opt            xfs defaults 0 0
/dev/mapper/rootvg-tmp    /tmp            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-local  /usr/local      xfs defaults 0 0
/dev/mapper/rootvg-home   /home           xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-var    /var            xfs defaults,nodev,nosuid 0 0
/dev/mapper/rootvg-log    /var/log        xfs defaults,nodev,noexec,nosuid 0 0
/dev/mapper/rootvg-audit  /var/log/audit  xfs defaults,nodev,noexec,nosuid 0 0
EOF

        # Mount everything to verify
        sudo mount -a
        sudo systemctl daemon-reexec
        sudo systemctl daemon-reload

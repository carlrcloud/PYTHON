# 1. Create physical and volume groups
ls /sys/block | tail -1 > /tmp/pvname
sudo pvcreate /dev/$(cat /tmp/pvname)
sudo vgcreate rootvg /dev/$(cat /tmp/pvname)

# 2. Create logical volumes
sudo lvcreate -n tmp -L 5G rootvg && sudo mkfs.xfs /dev/rootvg/tmp
sudo lvcreate -n log -L 5G rootvg && sudo mkfs.xfs /dev/rootvg/log
sudo lvcreate -n audit -L 1G rootvg && sudo mkfs.xfs /dev/rootvg/audit
sudo lvcreate -n home -L 5G rootvg && sudo mkfs.xfs /dev/rootvg/home
sudo lvcreate -n var -L 5G rootvg && sudo mkfs.xfs /dev/rootvg/var
sudo lvcreate -n opt -L 3G rootvg && sudo mkfs.xfs /dev/rootvg/opt
sudo lvcreate -n local -L 3G rootvg && sudo mkfs.xfs /dev/rootvg/local

# 3. Mount and copy existing content into the new volumes
for dir in opt tmp local var home; do
    sudo mkdir -p /mnt/$dir
    sudo mount /dev/mapper/rootvg-$dir /mnt/$dir
    sudo rsync -aAXv /$dir/ /mnt/$dir/
    sudo umount /mnt/$dir
done

# For nested paths like /var/log and /var/log/audit:
sudo mkdir -p /mnt/log
sudo mount /dev/mapper/rootvg-log /mnt/log
sudo rsync -aAXv /var/log/ /mnt/log/
sudo umount /mnt/log

sudo mkdir -p /mnt/audit
sudo mount /dev/mapper/rootvg-audit /mnt/audit
sudo rsync -aAXv /var/log/audit/ /mnt/audit/
sudo umount /mnt/audit

# 4. Add fstab entries AFTER copying is done
echo '/dev/mapper/rootvg-opt   /opt           xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-tmp   /tmp           xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-local /usr/local     xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-var   /var           xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-home  /home          xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-log   /var/log       xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-audit /var/log/audit xfs defaults 0 0'   | sudo tee -a /etc/fstab

# 5. Mount all volumes
sudo mount -a
sudo systemctl daemon-reexec

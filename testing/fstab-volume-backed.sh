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

# 3. Backup original data, mount new volume, then restore

for dir in opt tmp local var home; do
    sudo mv /$dir /$dir.bak
    sudo mkdir /$dir
    sudo mount /dev/mapper/rootvg-$dir /$dir
    sudo rsync -aAXv /$dir.bak/ /$dir/
done

# For /var/log
sudo mv /var/log /var/log.bak
sudo mkdir -p /var/log
sudo mount /dev/mapper/rootvg-log /var/log
sudo rsync -aAXv /var/log.bak/ /var/log/

# For /var/log/audit
sudo mv /var/log/audit /var/log/audit.bak
sudo mkdir -p /var/log/audit
sudo mount /dev/mapper/rootvg-audit /var/log/audit
sudo rsync -aAXv /var/log/audit.bak/ /var/log/audit/

# 4. Add fstab entries AFTER restoring data
echo '/dev/mapper/rootvg-opt   /opt           xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-tmp   /tmp           xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-local /usr/local     xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-var   /var           xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-home  /home          xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-log   /var/log       xfs defaults 0 0'   | sudo tee -a /etc/fstab
echo '/dev/mapper/rootvg-audit /var/log/audit xfs defaults 0 0'   | sudo tee -a /etc/fstab

# 5. Optional cleanup (only after full verification)
# sudo rm -rf /opt.bak /tmp.bak /usr/local.bak /var.bak /home.bak /var/log.bak /var/log/audit.bak

# 6. Reload system mounts and services
sudo systemctl daemon-reexec

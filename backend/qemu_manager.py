import subprocess
import random
import os
import signal
import shutil
from datetime import datetime, timedelta


class QEMUManager:
    def __init__(self):
        self.images_dir = "vm_images"
        os.makedirs(self.images_dir, exist_ok=True)
        self.template_image = os.path.join(self.images_dir, "alpine_template.qcow2")

    def create_vm(self, config):
        try:
            if not os.path.exists(self.template_image):
                raise FileNotFoundError(
                    f"Шаблонный образ не найден: {self.template_image}"
                )

            ssh_port = random.randint(11001, 12000)
            vm_suffix = random.randint(1000, 9999)

            vm_image = os.path.join(
                self.images_dir,
                f"{config.name}_{vm_suffix}.qcow2"
            )

            pidfile = os.path.join(
                self.images_dir,
                f"{config.name}_{vm_suffix}.pid"
            )

            shutil.copy(self.template_image, vm_image)

            cmd = [
                "qemu-system-x86_64",
                "-m", str(config.ram),
                "-smp", str(config.cpu),
                "-hda", vm_image,
                "-net", "nic",
                "-net", f"user,hostfwd=tcp::{ssh_port}-:22",
                "-daemonize",
                "-pidfile", pidfile
            ]

            subprocess.run(cmd, check=True)

            if not os.path.exists(pidfile):
                raise RuntimeError("QEMU не создал pidfile")

            with open(pidfile, "r") as f:
                pid = int(f.read().strip())

            expires_at = datetime.now() + timedelta(hours=1)

            return {
                "pid": pid,
                "ssh_port": ssh_port,
                "expires_at": expires_at.isoformat(),
                "status": "running",
                "image_path": vm_image
            }

        except Exception as e:
            print(f"Ошибка создания VM: {e}")
            return None

    def stop_vm(self, pid):
        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except Exception as e:
            print(f"Ошибка остановки VM: {e}")
            return False

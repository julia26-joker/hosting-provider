import subprocess
import random
import os
import signal
from datetime import datetime, timedelta

class QEMUManager:
    def __init__(self):
 
        self.images_dir = "vm_images"
        os.makedirs(self.images_dir, exist_ok=True)
    
    def create_vm(self, config):
        try:
    
            ssh_port = random.randint(11001, 12000)
    
            image_path = f"{self.images_dir}/alpine.qcow2"
            
  
            if not os.path.exists(image_path):
                subprocess.run([
                    "qemu-img", "create", "-f", "qcow2", image_path, "1G"
                ])
            
      
            cmd = [
                "qemu-system-x86_64",
                "-m", str(config.ram),
                "-smp", str(config.cpu),
                "-hda", image_path,
                "-net", f"user,hostfwd=tcp::{ssh_port}-:22",
                "-nographic",
                "-daemonize"  
            ]
            
     
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            expires_at = datetime.now() + timedelta(hours=1)
            
            return {
                'pid': process.pid,
                'ssh_port': ssh_port,
                'expires_at': expires_at,
                'status': 'running'
            }
        except Exception as e:
            print(f"Ошибка создания VM: {e}")
            return None
    
    def stop_vm(self, pid):

        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except:
            return False
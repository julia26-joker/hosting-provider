import time
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from backend.docker_manager import DockerManager
from backend.qemu_manager import QEMUManager
import database.db as db

class Monitor:
    def __init__(self):
        self.docker = DockerManager()
        self.qemu = QEMUManager()
        self.check_interval = 10  
    
    def check_and_kill(self):
        print(f"[{datetime.now()}] Проверка инстансов...")
        
        instances = db.get_all_instances()
        
        for inst in instances:
            instance_id = inst[0]
            inst_type = inst[2]
            status = inst[7]
            expires_at = inst[9]
            pid = inst[10]
            container_id = inst[11]
            
            if status != 'running':
                continue
            
            if expires_at:
                expires = datetime.fromisoformat(expires_at)
                if datetime.now() > expires:
                    print(f"Инстанс {instance_id} просрочен. Убиваем...")
                    print(f"Тип: {inst_type}, Container ID: {container_id}, PID: {pid}")
                    
                    if inst_type == 'container' and container_id:
                        print(f"Пытаюсь остановить контейнер {container_id}")
                        result = self.docker.stop_container(container_id)
                        print(f"Результат остановки контейнера: {result}")
                    elif inst_type == 'vm' and pid:
                        print(f"Пытаюсь остановить VM с PID {pid}")
                        result = self.qemu.stop_vm(pid)
                        print(f"Результат остановки VM: {result}")
                    
                    db.update_instance_status(instance_id, 'expired')
                    print(f"Инстанс {instance_id} остановлен")
    
    def run(self):
        
        print("Монитор запущен. Проверка каждые", self.check_interval, "секунд")
        while True:
            try:
                self.check_and_kill()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                print("Монитор остановлен")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
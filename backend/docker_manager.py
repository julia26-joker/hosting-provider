import docker
import random
from datetime import datetime, timedelta

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
    
    def create_container(self, config):
        try:
            ssh_port = random.randint(10000, 11000)
            
            os_images = {
                "ubuntu": "ubuntu:latest",
                "python": "python:3.9-slim",
                "nginx": "nginx:alpine"
            }
            
            image = os_images.get(config.os, "alpine:latest")
            
            container = self.client.containers.run(
                image=image,
                name=f"hosting_{config.name}_{random.randint(1000, 9999)}",
                detach=True,
                cpu_count=config.cpu,
                mem_limit=f"{config.ram}m",
                ports={'22/tcp': ssh_port}, 
                command="/bin/sh -c 'while true; do sleep 3600; done'"  
            )
            
            expires_at = datetime.now() + timedelta(minutes=1) 
            
            print(f"Контейнер создан: {container.id}, порт: {ssh_port}")
            
            return {
                'container_id': container.id,
                'ssh_port': ssh_port,
                'expires_at': expires_at,
                'status': 'running'
            }
        except Exception as e:
            print(f"Ошибка создания контейнера: {e}")
            return None
    
    def stop_container(self, container_id):
        try:
            print(f"stop_container вызван для {container_id}")
            container = self.client.containers.get(container_id)
            print(f"Контейнер найден: {container.name}, статус: {container.status}")
            
            container.stop()
            print("Контейнер остановлен")
            
            container.remove()
            print("Контейнер удалён")
            
            return True
        except Exception as e:
            print(f"ОШИБКА при остановке контейнера: {e}")
            return False
    
    def list_containers(self):
        containers = self.client.containers.list(all=True)
        return [{'id': c.id, 'name': c.name, 'status': c.status} for c in containers]
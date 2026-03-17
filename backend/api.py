import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta

from backend.models import InstanceCreate
from backend.docker_manager import DockerManager
from backend.qemu_manager import QEMUManager
import database.db as db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

docker_mgr = DockerManager()
qemu_mgr = QEMUManager()

db.init_db()

@app.post("/api/create")
async def create_instance(instance: InstanceCreate):
    
    if instance.type == "container":
        result = docker_mgr.create_container(instance)
        
        if result:
            data = {
                'name': instance.name,
                'type': instance.type,
                'os': instance.os,
                'cpu': instance.cpu,
                'ram': instance.ram,
                'disk': instance.disk,
                'ssh_port': result['ssh_port'],
                'container_id': result['container_id'],
                'expires_at': result['expires_at']
            }
            instance_id = db.add_instance(data)
            return {
                "id": instance_id,
                "ssh_port": result['ssh_port'],
                "status": "created",
                "message": f"Контейнер создан! SSH порт: {result['ssh_port']}"
            }
    
    elif instance.type == "vm":
        result = qemu_mgr.create_vm(instance)
        
        if result:
            data = {
                'name': instance.name,
                'type': instance.type,
                'os': instance.os,
                'cpu': instance.cpu,
                'ram': instance.ram,
                'disk': instance.disk,
                'ssh_port': result['ssh_port'],
                'pid': result['pid'],
                'expires_at': result['expires_at']
            }
            instance_id = db.add_instance(data)
            return {
                "id": instance_id,
                "ssh_port": result['ssh_port'],
                "status": "created",
                "message": f"Виртуалка создана! SSH порт: {result['ssh_port']}"
            }
    
    raise HTTPException(status_code=500, detail="Failed to create instance")

@app.get("/api/list")
async def list_instances():
    instances = db.get_all_instances()
    result = []
    for inst in instances:
        result.append({
            "id": inst[0],
            "name": inst[1],
            "type": inst[2],
            "os": inst[3],
            "cpu": inst[4],
            "ram": inst[5],
            "disk": inst[6],
            "status": inst[7],
            "created_at": inst[8],
            "expires_at": inst[9],
            "ssh_port": inst[12]
        })
    return result

@app.post("/api/stop/{instance_id}")
async def stop_instance(instance_id: int):
    inst = db.get_instance_by_id(instance_id)
    
    if not inst:
        raise HTTPException(status_code=404, detail="Инстанс не найден")
    
    inst_type    = inst[2]
    status       = inst[7]
    pid          = inst[10]
    container_id = inst[11]

    if status != "running":
        raise HTTPException(status_code=400, detail=f"Инстанс уже имеет статус '{status}'")

    if inst_type == "container" and container_id:
        success = docker_mgr.stop_container(container_id)
    elif inst_type == "vm" and pid:
        success = qemu_mgr.stop_vm(pid)
    else:
        raise HTTPException(status_code=500, detail="Нет данных для остановки инстанса")

    if not success:
        raise HTTPException(status_code=500, detail="Не удалось остановить инстанс")

    db.update_instance_status(instance_id, "stopped")
    return {"status": "stopped"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
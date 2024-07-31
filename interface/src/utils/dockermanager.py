# utils/dockermanager.py

import docker
from typing import List, Dict, Any, Optional
import datetime
class DockerManager:
    def __init__(self):
        self.client = docker.from_env()


    # Container Operations
    def list_containers(self, all: bool = False, networks: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        container_list = self.client.containers.list(all=all)

        if networks:
            container_list = [c for c in container_list if any(n in c.attrs['NetworkSettings']['Networks'] for n in networks)]

        def get_ports(container):
            ports = container.attrs['NetworkSettings']['Ports']
            if ports:
                return [f"{host_config[0]['HostPort']}:{container_port.split('/')[0]}" 
                        for container_port, host_config in ports.items() 
                        if host_config]
            return []

        return [{'id': c.id, 
                'name': c.name, 
                'status': c.status, 
                'ports': get_ports(c)} for c in container_list]

    def get_container(self, container_id: str) -> Dict[str, Any]:
        container = self.client.containers.get(container_id)
        return {'id': container.id, 'name': container.name, 'status': container.status}

    def run_container(self, image: str, **kwargs) -> Dict[str, Any]:
        container = self.client.containers.run(image, **kwargs)
        return {'id': container.id, 'name': container.name}

    def stop_container(self, container_id: str) -> None:
        self.client.containers.get(container_id).stop()

    def remove_container(self, container_id: str) -> None:
        self.client.containers.get(container_id).remove()

    def pause_container(self, container_id: str) -> None:
        self.client.containers.get(container_id).pause()

    def unpause_container(self, container_id: str) -> None:
        self.client.containers.get(container_id).unpause()

    def restart_container(self, container_id: str) -> None:
        self.client.containers.get(container_id).restart()

    def get_container_logs(self, container_id: str, since: datetime = None, until: datetime = None) -> str:
        logs = self.client.containers.get(container_id).logs(
            timestamps=True,
            since=since if since else None,
            until=until if until else None
        )
        return logs
    
    def restart_container(self, container_id: str) -> None:
        self.client.containers.get(container_id).restart()


    def exec_run(self, container_id: str, cmd: str) -> tuple:
        return self.client.containers.get(container_id).exec_run(cmd)

    # Image Operations
    def list_images(self) -> List[Dict[str, Any]]:
        return [{'id': i.id, 'tags': i.tags} for i in self.client.images.list()]

    def get_image(self, image_id: str) -> Dict[str, Any]:
        image = self.client.images.get(image_id)
        return {'id': image.id, 'tags': image.tags}

    def build_image(self, path: str, tag: str) -> tuple:
        image, logs = self.client.images.build(path=path, tag=tag)
        return image.id, logs

    def pull_image(self, repository: str, tag: str = None) -> None:
        self.client.images.pull(repository, tag=tag)

    def push_image(self, repository: str, tag: str = None) -> None:
        self.client.images.push(repository, tag=tag)

    def remove_image(self, image: str) -> None:
        self.client.images.remove(image)

    def tag_image(self, image: str, repository: str, tag: str = None) -> None:
        self.client.images.get(image).tag(repository, tag=tag)

    # Utility methods
    def restart_container_by_name(self, container_name: str) -> None:
        containers = self.list_containers(all=True)
        for container in containers:
            if container['name'] == container_name:
                self.restart_container(container['id'])
                return
        raise ValueError(f"Container with name {container_name} not found")

    def get_container_id_by_name(self, container_name: str) -> Optional[str]:
        containers = self.list_containers(all=True)
        for container in containers:
            if container['name'] == container_name:
                return container['id']
        return None


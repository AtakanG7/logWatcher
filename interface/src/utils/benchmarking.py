# utils/benchmarking.py

import time
import asyncio
import aiohttp
from typing import Dict, Any
from utils.dockermanager import DockerManager
from utils.monitoring import get_container_metrics

docker_manager = DockerManager()

class ContainerBenchmark:
    def __init__(self, container_name: str):
        self.container_id = docker_manager.get_container_id_by_name(container_name)
        self.container = docker_manager.get_container(self.container_id)
        self.results = {}

    def cpu_benchmark(self, duration: int = 10) -> Dict[str, float]:
        start_time = time.time()
        cpu_stats = []
        
        while time.time() - start_time < duration:
            stats = get_container_metrics('application')
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
            cpu_stats.append(cpu_percent)
            time.sleep(1)
        
        self.results['cpu'] = {
            'average': sum(cpu_stats) / len(cpu_stats),
            'max': max(cpu_stats),
            'min': min(cpu_stats)
        }
        return self.results['cpu']

    def memory_benchmark(self, duration: int = 10) -> Dict[str, float]:
        start_time = time.time()
        memory_stats = []
        
        while time.time() - start_time < duration:
            stats = docker_manager.get_container_stats(self.container_id)
            memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)  # Convert to MB
            memory_stats.append(memory_usage)
            time.sleep(1)
        
        self.results['memory'] = {
            'average': sum(memory_stats) / len(memory_stats),
            'max': max(memory_stats),
            'min': min(memory_stats)
        }
        return self.results['memory']

    async def http_benchmark(self, url: str, num_requests: int = 100) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = [session.get(url) for _ in range(num_requests)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

        successful_requests = sum(1 for r in responses if isinstance(r, aiohttp.ClientResponse) and r.status == 200)
        total_time = end_time - start_time
        
        self.results['http'] = {
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
        }
        return self.results['http']

    def run_all_benchmarks(self, http_url: str, duration: int = 10, num_requests: int = 100) -> Dict[str, Any]:
        self.cpu_benchmark(duration)
        self.memory_benchmark(duration)
        asyncio.run(self.http_benchmark(http_url, num_requests))
        return self.results

    def get_results(self) -> Dict[str, Any]:
        return self.results

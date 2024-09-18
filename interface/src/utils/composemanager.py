import yaml
import subprocess
import re

class DockerComposeManager:
    def __init__(self, compose_path):
        self.compose_path = compose_path
        self.compose_data = self.load_compose_file()

    def load_compose_file(self):
        try:
            with open(self.compose_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception(f"Compose file not found: {self.compose_path}")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML file: {e}")

    def save_compose_file(self):
        try:
            with open(self.compose_path, 'w') as file:
                yaml.dump(self.compose_data, file, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Error saving compose file: {e}")

    def add_service(self, service_name, service_data):
        self.compose_data['services'][service_name] = service_data
        self.save_compose_file()

    def remove_service(self, service_name):
        if service_name in self.compose_data['services']:
            del self.compose_data['services'][service_name]
            self.save_compose_file()
        else:
            raise Exception(f"Service '{service_name}' not found in compose file")

    def update_service(self, service_name, new_service_data):
        if service_name in self.compose_data['services']:
            self.compose_data['services'][service_name].update(new_service_data)
            self.save_compose_file()
        else:
            raise Exception(f"Service '{service_name}' not found in compose file")

    def get_ports(self):
        ports = set()
        services = self.compose_data.get('services', {})
        for service in services.values():
            if 'ports' in service:
                for port in service['ports']:
                    # Extract port number from "hostPort:containerPort"
                    match = re.match(r'(\d+):\d+', port)
                    if match:
                        ports.add(int(match.group(1)))
        return ports

    def check_ports(self, ports):
        used_ports = set()
        for port in ports:
            result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True)
            if f':{port}' in result.stdout:
                used_ports.add(port)
        return used_ports

    def up(self):
        ports = self.get_ports()
        used_ports = self.check_ports(ports)
        if used_ports:
            print(f"Ports already in use: {', '.join(map(str, used_ports))}")
        else:
            try:
                subprocess.run(['docker-compose', 'up', '-d'], check=True)
                print("Docker Compose services started successfully.")
            except subprocess.CalledProcessError as e:
                raise Exception(f"Error running docker-compose up: {e}")

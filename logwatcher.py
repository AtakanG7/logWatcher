from interface.src.utils.composemanager import DockerComposeManager
import sys
import logging
import time
import os
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

NETWORKS = ['monitoring']
COMPOSE_IMAGE_NAME = 'application'
COMPOSE_FILE_PATH = 'docker-compose.yml'
ENV_FILE_PATH = "./config/application/.env"
STREAMLIT_ENTRY_POINT = "./interface/src/dashboard.py"

def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError("Incorrect number of arguments. Usage: script.py <image_name> <port>")

        image_name = sys.argv[1]
        port = sys.argv[2]

        if not port.isdigit() or int(port) < 1 or int(port) > 65535:
            raise ValueError(f"Invalid port number: {port}. Port must be between 1 and 65535.")

        if not os.path.exists(ENV_FILE_PATH):
            raise FileNotFoundError(f"Environment file not found: {ENV_FILE_PATH}")

        logger.info(f"Initializing DockerComposeManager with file: {COMPOSE_FILE_PATH}")
        compose_manager = DockerComposeManager(COMPOSE_FILE_PATH)

        logger.info(f"Adding service: {image_name}")
        compose_manager.add_service(COMPOSE_IMAGE_NAME, {
            'container_name': COMPOSE_IMAGE_NAME,
            'image': image_name,
            'ports': [
                f'{port}:{port}'
            ],
            'env_file': ENV_FILE_PATH,
            'networks': NETWORKS,
        })
        logger.info(f"Service {image_name} succesfully added!")
        time.sleep(1)
        logger.info("Starting Docker Compose services")
        compose_manager.up()
        time.sleep(1)
        logger.info("Docker Compose services started successfully")
        time.sleep(1)
        logger.info("Preparing to launch the interface...")
        subprocess.run(['streamlit', 'run', STREAMLIT_ENTRY_POINT])
    except ValueError as ve:
        logger.error(f"Value Error: {ve}")
        sys.exit(1)
    except FileNotFoundError as fnfe:
        logger.error(f"File Not Found Error: {fnfe}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
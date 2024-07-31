#!/bin/bash
echo "Hey mate $USER, welcome to Log Watcher!"
echo "Script started at $(date)"

if [ $# -ne 1 ]; then
    echo "[Error] An image name is expected from DockerHub"
    exit 1
fi

image="$1"
ports="$2"

# Validate image name
if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "[Error] Image '$image' does not exist locally. Attempting to pull..."
    if ! docker pull "$image"; then
        echo "[Error] Failed to pull image '$image'. Exiting."
        exit 1
    fi
    echo "[INFO] $image pulled at $(date)"
fi
# Inspect the Docker image and extract the exposed ports
ports=$(docker inspect "$image" | grep -i "ExposedPorts" -A 10 | grep -oP '\d+(?=\/tcp)')

if [ -z "$ports" ]; then
    echo "[INFO] No exposed ports found for image '$image'."
else
    echo "[INFO] $ports open ports detected at $(date)"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get package manager
if command_exists apt; then
    PACKAGE_MANAGER="apt"
elif command_exists yum; then
    PACKAGE_MANAGER="yum"
elif command_exists dnf; then
    PACKAGE_MANAGER="dnf"
elif command_exists zypper; then
    PACKAGE_MANAGER="zypper"
else
    echo "Unable to determine package manager. Please install required packages manually."
    exit 1
fi

if ! command_exists python3; then
    echo 'Installing python3...' >&2
    $PACKAGE_MANAGER install -y python3 python3-pip >/dev/null
fi
echo '[INFO] python3 exists.'

pip3 install -r requirements.txt >/dev/null
echo '[INFO] requirements installed.'


if ! command_exists docker; then
    echo 'Installing docker...' >&2
    case $PACKAGE_MANAGER in
        apt)
            $PACKAGE_MANAGER update >/dev/null
            $PACKAGE_MANAGER install -y docker.io >/dev/null
            ;;
        yum|dnf)
            $PACKAGE_MANAGER install -y yum-utils >/dev/null
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            $PACKAGE_MANAGER install -y docker-ce docker-ce-cli containerd.io >/dev/null
            ;;
        zypper)
            $PACKAGE_MANAGER install -y docker >/dev/null
            ;;
    esac
    systemctl start docker >/dev/null
    systemctl enable docker >/dev/null
    usermod -aG docker $USER
    echo "Please log out and log back in for Docker permissions to take effect."
fi
echo '[INFO] docker exists.'

if ! command_exists docker-compose; then
    echo 'Installing docker-compose...' >&2
    if command_exists pip3; then
        pip3 install docker-compose >/dev/null
    elif command_exists pip; then
        pip install docker-compose >/dev/null
    else
        echo "Unable to install docker-compose. Please install pip3 or pip first."
        exit 1
    fi
fi

echo '[INFO] docker-compose exists.'
echo '[INFO] Registering the image to the registry...'

python3 logwatcher.py $image $ports
echo "[INFO] Script ended at $(date)"
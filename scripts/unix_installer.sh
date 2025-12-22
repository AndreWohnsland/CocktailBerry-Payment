echo "~~ Starting CocktailBerry-Payment Unix installer... ~~"
echo "> Installing 'uv' via Astral.sh..."

if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://astral.sh/uv/install.sh | sh
else
    echo "Error: Neither curl nor wget is installed. Please install one of these tools to proceed."
    exit 1
fi

# refreshing shell
if [ -n "$ZSH_VERSION" ]; then
    source ~/.zshrc
elif [ -n "$BASH_VERSION" ]; then
    source ~/.bashrc
fi

echo "> installing git, docker and other dependencies..."
sudo apt-get update
sudo apt-get install -y pcscd libccid pcsc-tools swig libpcsclite-dev git docker.io
docker --version || echo "Docker installation failed :("
echo "> Adds current user to docker permissions"
sudo usermod -aG docker "$USER"
sudo systemctl enable --now pcscd

echo "> Installing Compose"
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p "$DOCKER_CONFIG/cli-plugins"
curl -SL "https://github.com/docker/compose/releases/download/v5.0.0/docker-compose-linux-aarch64" -o "$DOCKER_CONFIG/cli-plugins/docker-compose"
chmod +x "$DOCKER_CONFIG/cli-plugins/docker-compose"
docker compose version || echo "Compose installation failed :("

echo "> configuring pcscd to run without polkit, this is needed for NFC readers to work properly..."
if grep -Eq '^\s*#?\s*PCSCD_ARGS=' /etc/default/pcscd; then
  sudo sed -i 's|^\s*#\?\s*PCSCD_ARGS=.*|PCSCD_ARGS=--disable-polkit|' /etc/default/pcscd
else
  echo 'PCSCD_ARGS=--disable-polkit' | sudo tee -a /etc/default/pcscd >/dev/null
fi

echo "> Cloning CocktailBerry-Payment repository..."
git clone https://github.com/AndreWohnsland/CocktailBerry-Payment.git
cd CocktailBerry-Payment

echo "> Installing CocktailBerry-Payment dependencies..."
uv sync --all-extras --frozen

newgrp docker
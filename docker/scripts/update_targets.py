import json
import ipaddress


DEFAULT_IP = "aerospike-vector-search"
DEFAULT_PORT = 5040


def ensure_requests_installed():
    """
    Checks if the 'requests' library is installed. If not, it installs the library.
    """
    try:
        import requests
        print("The 'requests' library is already installed.")
    except ImportError:
        import subprocess
        import sys
        print("The 'requests' library is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("The 'requests' library has been installed successfully.")


def get_public_ip():
    """
    Fetches the public IP of the host using the external service ifconfig.me.
    """
    try:
        response = requests.get("https://ifconfig.me", timeout=5)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        return response.text.strip()
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return None


def update_targets_file(ip_address, file_path="config/targets.json"):
    targets = [
        {
            "targets": [f"{DEFAULT_IP}:{DEFAULT_PORT}"],
            "labels": {
                "instance": f"{ip_address}:{DEFAULT_PORT}",
            },
        }
    ]
    with open(file_path, "w") as f:
        json.dump(targets, f, indent=2)


if __name__ == "__main__":
    ensure_requests_installed()
    import requests
    ip = get_public_ip()
    try:
        ipaddress.ip_address(ip)
        print(f"Resolved external IP address: {ip}")
    except ValueError:
        print(f"Unable to resolve external IP address: {ip}")
        print(f"using default IP address instead: {DEFAULT_IP}")
        ip = DEFAULT_IP

    update_targets_file(ip)

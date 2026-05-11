# About gVisor (runsc)
gVisor is an open-source, user-space application kernel developed by Google that provides a secure, sandboxed environment for running containers.
By intercepting application system calls and handling them within a dedicated Sentry process, it acts as an intermediary layer between containers and the host Linux kernel, preventing container escapes and improving security.

**Pros**
- **Strong isolation**: One of the most robust isolation tools available, without the rigidity of full VMs.
- **Backed by Google**: Used extensively in Google Kubernetes Engine (GKE) so it's well-maintained and production-ready.
- **Flexible**: Works with Docker, containerd, and Kubernetes out of the box.

**Cons**
- **Linux-only**: It was designed to secure Linux containers by intercepting and reimplementing Linux system calls, so no Windows or macOS support.
- **Performance overhead**: Adds syscall interception overhead, which can slow down syscall-heavy workloads.
- **Compatibility issues**: Some applications that rely on specific kernel features may not work properly.
  For instance, it does not work with SELinux, which is a core security component on Fedora Linux. Hence, you must disable SELinux in the container, when running a Fedora-based docker image.


## 1. Install the runsc executable

### On Ubuntu

```bash
# Add the gVisor GPG key
curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg

# Add the repository to your sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list > /dev/null

# Update and install runsc
sudo apt-get update && sudo apt-get install -y runsc
```

### On Fedora
Download and install the latest runsc and shim binaries directly to /usr/local/bin:

```bash
# Set version (release or nightly)
ARCH=$(uname -m)
URL=https://storage.googleapis.com/gvisor/releases/release/latest/${ARCH}

# Download binary and sha512
wget ${URL}/runsc ${URL}/runsc.sha512

# Verify and install runsc
sha512sum -c runsc.sha512
chmod +x runsc
sudo mv runsc /usr/local/bin

# Restore default SELinux labels for the binary
sudo restorecon -v /usr/local/bin/runsc
```

## 2. Tell the container engine how to use the new runsc runtime

### For Docker
Use the built-in install command provided by runsc, which automatically updates your /etc/docker/daemon.json

```bash
sudo runsc install
sudo systemctl restart docker
```

### For Containerd (Kubernetes)
You need to manually edit `/etc/containerd/config.toml` to add the runsc handler under the runtimes section.

```toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
  runtime_type = "io.containerd.runsc.v1"
```

Then restart the service:

```bash
sudo systemctl restart containerd
```

## 3. Verify the Installation

### On Ubuntu

```bash
docker run --rm --runtime=runsc ubuntu dmesg | head -n 1
```

### On Fedora

```bash
# Disable SELinux, since it is not supported by runsc
docker run --rm --runtime=runsc --security-opt label=disable ubuntu dmesg | head -n 1
```

If successful, the above command should print

    [    0.000000] Starting gVisor...

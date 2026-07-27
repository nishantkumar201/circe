import os
import sys

conda_prefix = os.environ.get("CONDA_PREFIX", sys.prefix)
cublas_lib = os.path.join(
    conda_prefix,
    f"lib/python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages/nvidia/cublas/lib",
)
os.environ["LD_LIBRARY_PATH"] = cublas_lib + ":" + os.environ.get("LD_LIBRARY_PATH", "")

from api.comm_backbone import CommBackbone
from comms.tailscale import Tailscale
from fastapi.staticfiles import StaticFiles

jarvis = CommBackbone()
jarvis.mount("/dashboard", StaticFiles(directory="dashboard"), name="static")


if __name__ == "__main__":
    Tailscale().serve("http://0.0.0.0:8000")
    jarvis.run()
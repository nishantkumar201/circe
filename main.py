import os
os.environ["LD_LIBRARY_PATH"] = "/REDACTED/lib/python3.11/site-packages/nvidia/cublas/lib:" + os.environ.get("LD_LIBRARY_PATH", "")

from api.comm_backbone import CommBackbone
from comms.tailscale import Tailscale
from fastapi.staticfiles import StaticFiles

jarvis = CommBackbone()
jarvis.mount("/dashboard", StaticFiles(directory="dashboard"), name="static")


if __name__ == "__main__":
    Tailscale().serve("http://0.0.0.0:8000")
    jarvis.run()

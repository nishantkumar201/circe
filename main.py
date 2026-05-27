from api.comm_backbone import CommBackbone
from comms.tailscale import Tailscale
from fastapi.staticfiles import StaticFiles

jarvis = CommBackbone()
jarvis.mount("/dashboard", StaticFiles(directory="dashboard"), name="static")


if __name__ == "__main__":
    Tailscale().serve("http://0.0.0.0:8000")
    jarvis.run()
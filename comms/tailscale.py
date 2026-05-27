import subprocess


class Tailscale:
    def __init__(self):
        self._process = None
    
    def is_running(self):
        status =(subprocess.check_output(["tailscale", "status"])).decode("utf-8")
        status_list = status.strip().split("\n")
        for device in status_list:
            status_list_device = device.strip().split("  ")
            if status_list_device[3] == 'linux':
                if status_list_device[4] == '-':
                    print("Device is Connected")
                    return True
                else:
                    print("Device is not Connected")
                    return False
                break
    
    def start(self):
        if self.is_running():
            return
        else:
            subprocess.Popen(["tailscale", "up"])

    def stop(self):
        subprocess.Popen(["tailscale", "down"])

    def serve(self, target):
        subprocess.Popen(["tailscale", "serve", "--https=443", target])
        print("Server started")

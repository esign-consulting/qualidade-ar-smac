import docker
import logging
import socket


class SMAC:

    def __init__(self):
        self.client = docker.from_env()
        self.image = "esignbr/qualidade-ar-smac"

    def get_port(self, candidate_port=8080) -> int:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        max_candidate_port = candidate_port + 10
        while candidate_port <= max_candidate_port:
            try:
                sock.bind(('', candidate_port))
                sock.close()
                return candidate_port
            except OSError:
                candidate_port += 1
        raise IOError('no free ports')

    def build(self):
        if not self.client.images.list(name=self.image):
            logging.info(f"Building {self.image}...")
            self.client.images.build(tag=self.image, path=".")

    def already_running(self) -> bool:
        containers = self.client.containers.list(filters={"ancestor":self.image})
        if containers:
            self.container = containers[0]
            self.port = int(self.container.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"])
            self.to_stop = False
            return True
        return False

    def run(self) -> int:
        self.build()
        if not self.already_running():
            logging.info(f"Running {self.image}...")
            self.port = self.get_port()
            self.container = self.client.containers.run(image=self.image, name="smac", remove=True, detach=True, ports={"8080/tcp":self.port})
            self.to_stop = True
        return self.port

    def stop(self):
        if self.to_stop:
            self.container.stop()
            logging.info(f"{self.image} stopped.")
        del self.container
        del self.port
        del self.to_stop

import hydro._core # type: ignore

from typing import List, Optional
hydro_cli_rust = hydro._core

class Deployment(object):
    def __init__(self) -> None:
        self.underlying = hydro_cli_rust.PyDeployment()

    def Localhost(self) -> "Localhost":
        return Localhost(self)

    def GCPComputeEngineHost(self, project: str, machine_type: str, image: str, region: str) -> "GCPComputeEngineHost":
        return GCPComputeEngineHost(self, project, machine_type, image, region)

    def CustomService(self, on: "Host", external_ports: List[int]) -> "CustomService":
        return CustomService(self, on, external_ports)

    def HydroflowCrate(self, src: str, on: "Host", example: Optional[str] = None, features: Optional[List[str]] = None) -> "HydroflowCrate":
        return HydroflowCrate(self, src, on, example, features)

    def deploy(self):
        return self.underlying.deploy()

    def start(self):
        return self.underlying.start()

class Host(object):
    def __init__(self, underlying) -> None:
        self.underlying = underlying

class Localhost(Host):
    def __init__(self, deployment: Deployment):
        super().__init__(hydro_cli_rust.PyLocalhostHost(deployment.underlying))

class GCPComputeEngineHost(Host):
    def __init__(self, deployment: Deployment, project: str, machine_type: str, image: str, region: str):
        super().__init__(hydro_cli_rust.PyGCPComputeEngineHost(deployment.underlying, project, machine_type, image, region))

    @property
    def internal_ip(self) -> str:
        return self.underlying.internal_ip

    @property
    def external_ip(self) -> Optional[str]:
        return self.underlying.external_ip

    @property
    def ssh_key_path(self) -> str:
        return self.underlying.ssh_key_path

class Service(object):
    def __init__(self, underlying) -> None:
        self.underlying = underlying

class CustomService(Service):
    def __init__(self, deployment: Deployment, on: Host, external_ports: List[int]) -> None:
        super().__init__(hydro_cli_rust.PyCustomService(deployment.underlying, on.underlying, external_ports))

class HydroflowPort(object):
    def __init__(self, underlying, name) -> None:
        self.underlying = underlying
        self.name = name

    def send_to(self, other: "HydroflowPort"):
        hydro_cli_rust.create_connection(
            self.underlying,
            self.name,
            other.underlying,
            other.name
        )

class HydroflowCratePorts(object):
    def __init__(self, underlying) -> None:
        self.__underlying = underlying

    def __getattribute__(self, __name: str) -> HydroflowPort:
        if __name == "_HydroflowCratePorts__underlying":
            return object.__getattribute__(self, __name)
        return HydroflowPort(self.__underlying, __name)

async def pyreceiver_to_async_generator(pyreceiver):
    while True:
        res = await pyreceiver.next()
        if res is None:
            break
        else:
            yield res

class HydroflowCrate(Service):
    def __init__(self, deployment: Deployment, src: str, on: Host, example: Optional[str], features: Optional[List[str]]) -> None:
        super().__init__(hydro_cli_rust.PyHydroflowCrate(deployment.underlying, src, on.underlying, example, features))

    @property
    def ports(self) -> HydroflowCratePorts:
        return HydroflowCratePorts(self.underlying)

    async def stdout(self):
        return pyreceiver_to_async_generator(await self.underlying.stdout())

    async def stderr(self):
        return pyreceiver_to_async_generator(await self.underlying.stderr())

    def exit_code(self):
        return self.underlying.exit_code();
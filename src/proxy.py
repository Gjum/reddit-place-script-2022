import os
import random
import subprocess
import time
from stem import Signal, InvalidArguments, SocketError, ProtocolError
from stem.control import Controller


def Init(self):
    self.proxies = (
        get_proxies(self.json_data["proxies"])
        if "proxies" in self.json_data and self.json_data["proxies"] is not None
        else None
    )
    if self.proxies is None and os.path.exists(
        os.path.join(os.getcwd(), "proxies.txt")
    ):
        self.proxies = get_proxies_text()
    self.compactlogging = (
        self.json_data["compact_logging"]
        if "compact_logging" in self.json_data
        and self.json_data["compact_logging"] is not None
        else True
    )
    self.using_tor = (
        self.json_data["using_tor"]
        if "using_tor" in self.json_data and self.json_data["using_tor"] is not None
        else False
    )
    self.tor_password = (
        self.json_data["tor_password"]
        if "tor_password" in self.json_data
        and self.json_data["tor_password"] is not None
        else "Passwort"  # this is intentional, as I don't really want to mess around with the torrc again
    )
    self.tor_delay = (
        self.json_data["tor_delay"]
        if "tor_delay" in self.json_data and self.json_data["tor_delay"] is not None
        else 10
    )
    self.use_builtin_tor = (
        self.json_data["use_builtin_tor"]
        if "use_builtin_tor" in self.json_data
        and self.json_data["use_builtin_tor"] is not None
        else True
    )
    self.tor_port = (
        self.json_data["tor_port"]
        if "tor_port" in self.json_data and self.json_data["tor_port"] is not None
        else 1881
    )
    self.tor_control_port = (
        self.json_data["tor_control_port"]
        if "tor_port" in self.json_data
        and self.json_data["tor_control_port"] is not None
        else 9051
    )


def get_proxies_text(self):
    path_proxies = os.path.join(os.getcwd(), "proxies.txt")
    f = open(path_proxies)
    file = f.read()
    f.close()
    proxies_list = file.splitlines()
    self.proxies = []
    for i in proxies_list:
        self.proxies.append({"https": i, "http": i})
        self.logger.debug("loaded proxies {} from file {}", i, path_proxies)


def get_proxies(self, proxies):
    proxies_list = []
    for i in proxies:
        proxies_list.append({"https": i, "http": i})

        self.logger.debug("Loaded proxies: {}", str(proxies_list))
        return proxies_list
    return proxies_list


def get_random_proxy(self):
    if not self.using_tor:
        random_proxy = None
        if self.proxies is not None:
            random_proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
            self.logger.debug("Using proxy: {}", str(random_proxy))
            return random_proxy
        return random_proxy
    else:
        tor_reconnect(self)
        self.logger.debug("Using Tor. Selecting first proxy: {}.", str(self.proxies[0]))
        return self.proxies[0]


def tor_reconnect(self):
    if self.using_tor:
        try:
            self.tor_controller.signal(Signal.NEWNYM)
            self.logger.info("New Tor connection processing")
            time.sleep(self.tor_delay)
        except (InvalidArguments, ProtocolError):
            self.logger.error("couldn't establish new tor connection, disabling tor")
            self.using_tor = False

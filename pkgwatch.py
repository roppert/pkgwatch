#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A small program to check a list of packages to see if they need
updating and send mail with result.
"""
import apt
import configparser
import os
import platform
import smtplib

from email.mime.text import MIMEText


class PacketWatch:
    def __init__(self, configfile):
        if not os.path.exists(configfile):
            configfile = "pkgwatch.ini"
        if not os.path.exists(configfile):
            print("No config file found")
            exit(1)
        config = configparser.ConfigParser()
        config.read(configfile)
        node = platform.node()
        if node in config.sections():
            conf = config[node]
        else:
            conf = config["DEFAULT"]

        self.node = node
        self.pkglist = conf.get("pkglist").split()
        self.always_send = conf.getboolean("always_send")
        self.use_ssl = conf.getboolean("use_ssl")
        self.recipients = conf["recipients"].split()
        self.sender = conf["sender"]
        self.host = conf["host"]
        self.port = conf.getint("port")
        self.user = conf["user"]
        self.password = conf["password"]

    def run(self):
        cache = apt.cache.Cache()
        upgradeable_pkgs = []
        uptodate_pkgs = []
        for pkg_name in self.pkglist:
            if pkg_name not in cache:
                continue
            pkg = cache[pkg_name]
            if pkg.is_installed and pkg.is_upgradable:
                upgradeable_pkgs.append(pkg_name)
            else:
                uptodate_pkgs.append(pkg_name)
        if self.always_send or len(upgradeable_pkgs) > 0:
            body = "Checking for packages: {}\n\n".format(", ".join(self.pkglist))
            if upgradeable_pkgs:
                body += "Can be upgraded:\n"
                for pkg in upgradeable_pkgs:
                    body += "{}\n".format(pkg)
            else:
                body += "No packages to be upgraded\n"
            if uptodate_pkgs:
                body += "\nInstalled and up to date:\n"
                for pkg in uptodate_pkgs:
                    body += "{}\n".format(pkg)
            else:
                body += "\n"
            self.send_mail(body)

    def send_mail(self, body):
            msg = MIMEText(body)
            msg["Subject"] = "package watch on {}".format(self.node)
            msg["From"] = self.sender
            msg["To"] = ", ".join(self.recipients)
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.host, self.port)
                smtp.login(self.user, self.password)
            else:
                smtp = smtplib.SMTP(self.host, self.port)
            smtp.sendmail(self.sender, self.recipients, msg.as_string())
            smtp.quit()


if __name__ == "__main__":
    configfile = os.path.expanduser("~/pkgwatch.ini")
    pkgw = PacketWatch(configfile)
    pkgw.run()


# vi: set fileencoding=utf-8 :

#!/usr/bin/python
# coding: UTF-8

import json
import re

from fabric.api import local


def update():
    stopServer()
    repository_url = "https://api.github.com/repos/gitbucket/gitbucket"
    api_url = repository_url + "/releases/latest"
    result = local("curl " + api_url, capture=True)
    meta = json.loads(result)
    version = meta["tag_name"]
    if not checkVersion(version):
        print("Product is already latest version")
        return 0

    product_url = meta["assets"][0]["browser_download_url"]
    getWar(product_url, version)

    checksum_url = meta["assets"][1]["browser_download_url"]
    if checkMD5(checksum_url, version):
        print("Download product Complete!!")
        deploy()
        startServer()
    else:
        print("Download Failed!!: download file is crashed.")
        return -1


def getWar(wget_url, version):
    local("mv gitbucket*.war old/")
    local("mv gitbucket*.war.md5 old/")
    local("wget " + wget_url + " -O gitbucket." + version + ".war")


def checkVersion(version):
    version = float(version)
    pattern = r"gitbucket.(.*).war"
    f = local("ls gitbucket*", capture=True)
    now_version = float(re.match(pattern, f).group(1))

    return version > now_version


def checkMD5(url, version):
    product_file_name = "gitbucket." + version + ".war"
    file_name = product_file_name + ".md5"
    local("wget " + url + " -O " + file_name)
    f = open(file_name)
    md5 = f.read()
    f.close()
    check_sum_command = "md5sum " + product_file_name + " | awk '{print $1}'"
    file_sum = local(check_sum_command, capture=True)
    return md5 == file_sum


def deploy():
    deploy_path = "/var/lib/tomcat8/webapps/"
    local("sudo cp -f gitbucket*.war " + deploy_path + "gitbucket.war")


def startServer():
    local("sudo service tomcat8 start")


def stopServer():
    local("sudo service tomcat8 stop")

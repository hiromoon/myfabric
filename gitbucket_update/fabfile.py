#!/usr/bin/python
# coding: UTF-8

from fabric.api import local, sudo
import json
import re

def update():
    stopServer()
    api_url = "https://api.github.com/repos/gitbucket/gitbucket/releases/latest"
    result = local("curl " + api_url, capture=True)
    meta  = json.loads(result)
    version = meta["tag_name"]
    if checkVersion(version):
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
    else :
      print("Product is already latest version")

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
    file_name = "gitbucket." + version + ".war.md5"
    local("wget " + url + " -O " + file_name)
    f = open(file_name)
    md5 = f.read()
    f.close()
    print(md5)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    file_sum = local("md5sum gitbucket." + version + ".war | awk '{print $1}'", capture=True) 
    print(file_sum)
    return md5 == file_sum

def deploy():
    deploy_path = "/var/lib/tomcat8/webapps/"
    local("sudo cp -f gitbucket*.war " + deploy_path + "gitbucket.war")

def startServer():
    local("sudo service tomcat8 start")

def stopServer():
    local("sudo service tomcat8 stop")

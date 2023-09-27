#!/usr/bin/python3

import requests, os, sys, json, hashlib, smtplib
from datetime import date
from email.message import EmailMessage

URL = ""
jsonFile = ""
message = ""
site = ""
req = ""

def jsonExists():
    files = os.listdir(".")
    if "siteList.json" in files:
        print(files)
        return True
    else:
        return False

#we check every website

if len(sys.argv) <= 1:
    changedList = ["test haha"]
    if not jsonExists():
        print("Usage: watcher.py [URL in full format]")
        exit()
    jsonFile = open("siteList.json", "r+")
    sites = json.load(jsonFile)
    for i in range(len(sites)):
        URL = sites[i]["url"]
        print("Checking " + URL)
        req = requests.get(URL)
        content = req.content
        siteCheck = {"url": URL, "signature": str(hashlib.md5(content).hexdigest()), "date": str(date.today())}
        if sites[i]["signature"] != siteCheck["signature"]:
            sites[i]["signature"] = siteCheck["signature"]
            sites[i]["date"] = str(date.today())
            changedList.append(URL)
            message = "The URL {} has received an update !!".format(URL)
    
    emailContent = "The URLs that changed: \n"
    for e in changedList:
        emailContent += "\t" + e + "\n"

    print(emailContent)
    msg = EmailMessage()
    msg.set_content(emailContent)
    msg['Subject'] = "Some URLs changed"
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = os.getenv('RECEIVER_EMAIL')
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.getenv('SENDER_EMAIL'), os.getenv('GPASSWORD'))
    server.send_message(msg)  
else:       
    URL = sys.argv[1]
    print("sending request...")

    try:
        req = requests.get(URL)
    except(Exception):
        print("Write the URL in full format")
        exit()

    if req.status_code == 404:
        print("Webpage not found")
        exit()

    content = req.content
    sitedict = {"url": URL, "signature": str(hashlib.md5(content).hexdigest()), "date": str(date.today())}

    message = "Webpage did not change since your last request ({})".format(sitedict["date"])

    if jsonExists():
        jsonFile = open("siteList.json", "r+")
        try:
            sites = json.load(jsonFile)
        except(Exception):
            print("Invalid json file")
            exit()


        urlInFile = False
        for i in range(len(sites)):
            if sites[i]["url"] == sitedict["url"]:
                urlInFile = True
                if sites[i]["signature"] != sitedict["signature"]:
                    sites[i]["signature"] = sitedict["signature"]
                    sites[i]["date"] = str(date.today())
                    message = "Webpage received an update !!"

        if not urlInFile:
            message = "Adding URL to JSON file"
            sites.append(sitedict)
    else:
        jsonFile = open("siteList.json", "w+")
        message = "Adding URL to JSON file"
        sites = [sitedict]

print(message)



jsonFile.seek(0, 0)
jsonFile.truncate(0)


sitesJSON = json.dumps(sites)
jsonFile.write(sitesJSON)

jsonFile.close()

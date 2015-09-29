### Slack JSON Processing
### v0.0.1

import json
import os
import datetime
import glob

settings = {
    "source"            : "",
    "users"             : "",
    "output"            : "",
    "title"             : "Example Title",
    "keepChannelJoins"  : False
}

class User(object):
    ''' User object used for lookup purposes '''
    def __init__(self, name=None, id=None, avatar=None):
        self.name=name
        self.id=id
        self.avatar=avatar

def returnUsers(file=None):
    ''' Returns a dictionary of user, id, avatar from the json users file '''
    users = {}

    jsonData = returnJSONObj(file=file)
    
    for item in jsonData:
        users[item["id"]] = User(name=item["name"], id=item["id"], avatar=item["profile"]["image_24"])

    return users

def returnJSONObj(file=None):
    '''  Returns a JSON object from a file '''

    with open(name=file, mode="r") as dataFile:
        jsonData = json.load(dataFile)

    return jsonData

def returnTimestamp(float=None):
    ''' Returns a locale-en/US style date format string '''
    timestamp = datetime.datetime.utcfromtimestamp(float)
    timestamp = timestamp.strftime("%m/%d/%Y %H:%M:%S")
    
    return timestamp

def main():

    print("Processing Users")
    users = returnUsers(settings["users"])

    print("Gathering files")
    target = os.path.join(settings["source"], "*.json")
    files = glob.glob(target)

    print("Opening output")
    
    with open(name=settings["output"], mode="w") as output:
        channel = os.path.basename(settings["source"])
        titleblock = settings["title"]
        bO, bC = "{", "}"
        header = """
<!DOCTYPE html>
<html>
<head>
    <title>{titleblock}</title>
    <style>
        @import url(https://fonts.googleapis.com/css?family=Open+Sans);
        html, body {bO}
            font-family: \"Open Sans\", Arial, Sans-Serif;
            font-size: 10pt;
            color: #000;

        {bC}
        .avatar {bO}
            border-radius: 50%;
            padding: 3px;
            float: left;
        {bC}
        .timestamp {bO}
            font-size: 10pt;
            color: DarkGrey;
        {bC}
        .user {bO}
            color: #708090;
            font-weight: bold;
        {bC}
        .msgblock {bO}
            padding-bottom: 3px
        {bC}
        .message {bO}
            float: clear;    
            width: 98%;
            margin-left: auto;
            margin-right: auto;
        {bC}


    </style>
</head>
<body>
<h1>{titleblock}</h1>
<hr>\n""".format(titleblock=titleblock, bO=bO, bC=bC)
        footer = """\n\t</body>\n</html>"""
        output.write(header)

        for file in files:
            data = returnJSONObj(file)
            for item in data:
                timestamp = "<span class=\"timestamp\">{timestamp}</span>".format(timestamp=returnTimestamp(float(str(item["ts"]))))
                username = "<span class=\"user\">{username}</span> {timestamp}".format(username=users[item["user"]].name, timestamp=timestamp)
                avatar = "<img src=\"{avatar}\" class=\"avatar\">".format(avatar=users[item["user"]].avatar)
                
                if "subtype" in item:
                    type = str(item["subtype"])
                else:
                    type = "msg"
                
                event = None

                if type == "msg":
                    text = item["text"]
                    text=text.strip()
                    link = ""

                    if "<@" in text:
                        while "<@" in text:
                            mentionID = text.split("<@")[1][:9]
                            mentionName = users[mentionID].name
                            old="<@{mentionID}>".format(mentionID=mentionID)
                            new="<b><i>@{mentionName}</b></i>".format(mentionName=mentionName)
                            text = text.replace(old, new)
                            

                    if "attachments" in item and "from_url" in item["attachments"][0]:
                        link = " (<a href=\"{url}\">{url}</a>)".format(url=item["attachments"][0]["from_url"])

                    text = text.encode('ascii', errors='xmlcharrefreplace')
                    text += link
                    event = "{avatar} {username}<br> <div class=\"message\">{text}</div><br>".format(avatar=avatar, username=username, text=text)

                elif type == "channel_join" and settings["keepChannelJoins"] == True:
                    event = "{avatar} {username}<br> has joined the channel: {channel}<br>".format(avatar=avatar, username=username, channel=channel)
                elif type == "channel_leave" and settings["keepChannelJoins"] == True:
                    event = "{avatar} {username}<br> has left the channel: {channel}<br>".format(avatar=avatar, username=username, channel=channel)
                elif type == "channel_purpose":
                    event = "{avatar} {username}<br> <div class=\"message\">has set the channel purpose: <b>{purpose}</b></div><br>".format(avatar=avatar, username=username, purpose=item["purpose"])
                
                if not event == None:
                    output.write("<div class=\"msgblock\">{event}</div>\n\n".format(timestamp=timestamp, event=event))

        output.write(footer)


if __name__ == "__main__":
    main()
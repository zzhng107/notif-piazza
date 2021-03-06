from piazza_api import Piazza
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import re, smtplib, sys, time

'''
    To receive email notifications, please correctly fill in your credentials below, and notice:
    1) Do not use illinois.edu email account
    2) Ensure 2-Step Verification is turned OFF
    3) Go to https://myaccount.google.com/lesssecureapps, and turn on the option to "Allow less secure apps"
'''
sender = ""
receiver = ""
password = ""

# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
def cleanHtml(raw_text):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_text)

    return cleantext

def sendEmail(course, cid):
    
    url = "https://piazza.com/class/" + course + "?cid=" + cid
    body = "We've found the following topic(s) that you might be interested in: " + url
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Piazza Notification Tool - New Topic Posted"
        msg['From'] = sender
        msg['To'] = receiver
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender,password)
        server.sendmail(sender, receiver, msg.as_string())

        server.close()
        log_msg = time.strftime("%c") + "-   " + url + "\n\n"
        with open("log.txt", "a") as f:
            f.write(log_msg)
            f.close()
        #print "email sent!"

    except:
        # something went wrong, write error to log
        print "ERROR: email delivery failed"
        log_msg = time.strftime("%c") + "   -   ERROR: email delivery failed\n\n"
        with open("log.txt", "a") as f:
            f.write(log_msg)
            f.close()
        sys.exit()

'''
    TODO: complete the following function to check whether the current post 
          is relevant to the current topic
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    text_vector - an array of strings representing current post
                  text_vector[0] = title of the post
                  text_vector[1] = main content of the post 
                  text_vector[2:] = the students' answer, the instructors' answer, all other comments
    return value: True if relevant, False otherwise
'''
def isRelevant(topic, text_vector):
    return True


if __name__ == "__main__":
    print "starting...\n"
    p = Piazza()
    p.user_login()

    #cs410 = "iy0x6bnqsx33fe"

    target_course, last_cid = "", 0
    data = list()
    topics = list()

    # read in course url and last post id that we've checked 
    with open("prepare.txt", "r") as f1:
        with open("log.txt", "a") as f2:
            data = f1.readlines()
            if len(data) != 3 or not data[0] or not data[1] or not data[2]:
                info = "ERROR: please make sure you've provided the correct info in correct format in prepare.txt"
                print info
                f2.write(time.strftime("%c") + "   -   " + info + "\n\n")
                sys.exit()
            topics = data[0].split(',')
            for topic in topics:
                topic = topic.strip()
            target_course = str(data[1].strip())
            last_cid = int(data[2].strip())

            f2.close()
            f1.close()

    course = p.network(target_course)

    with open("test.txt", "w") as f:
        max_cid = 0

        # https://piazza.com/class/ixushgjhlwy59l?cid=772
        post = course.get_post(772)
        
        # uncomment the next line to see what the raw data looks like (in text.txt)
        # f.write(str(post))

        cid = str(post["nr"])
        #max_cid = max(max_cid, int(cid))
        #if int(cid) == last_cid:
        #    break
        
        print "cid: " + cid + "\n"    
        
        text_vector = list()
        content = post["history"]
        title = (content[0]["subject"])
        content = content[0]["content"]
        main_text = cleanHtml(content).encode("utf-8")
        
        f.write(title+"\n")
        f.write(main_text+"\n")

        text_vector.append(title.strip())
        text_vector.append(main_text.strip())

        for child in post["children"]:
            if child.has_key("history"):
                tmp = child["history"][0]
                if tmp.has_key("content"):
                    text = tmp["content"].encode("utf-8")
                    text = cleanHtml(text)
                    text_vector.append(text.strip())
                    f.write(text+ "\n")

            if child.has_key("subject"):
                text = child["subject"].encode("utf-8")
                text = cleanHtml(text)
                text_vector.append(text.strip())
                f.write(text+"\n")

            if child.has_key("children"):
                for c in child["children"]:
                    text = c["subject"].encode("utf-8")
                    text = cleanHtml(text)
                    text_vector.append(text.strip())
                    f.write(text + "\n")                   

        '''
        for topic in topics:
            if isRelevant(topic, text_vector):
                pass
        '''        


    f.close()  
    '''      
    data[2] = max_cid        
    with open("prepare.txt", "w") as f:
        f.write(data[0])
        f.write(data[1])
        f.write(str(data[2]))
        f.close() 
    '''    
        
    print "done!\n"

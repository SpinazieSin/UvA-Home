#!/usr/bin/env python

import qi
import threading
import SimpleHTTPServer
import SocketServer
import time
import os
from random import randint

def showpage(PORT=9124):
    """
    Script to show a local website on the Pepper robot.

    Author: Sammy Pfeiffer <Sammy.Pfeiffer at student.uts.edu.au>
    """

    # Setup a webserver to serve the page we need later
    # PORT = 9124 # random between 1000 and 9000
    PEPPER_IP = "192.168.131.16"
    THIS_MACHINE_IP = "192.168.131.15"
    YOURHTMLFILE = "index.html"

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = SocketServer.TCPServer(("", PORT), Handler)

    print "Serving at port", PORT

    cwd = os.getcwd()

    print "Serving (briefly) path: " + cwd

    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()

    print "Web server thread started."

    # Use qi stuff to show the image on the tablet
    session = qi.Session()
    session.connect("tcp://" + PEPPER_IP + ":9559")
    tabletService = session.service("ALTabletService")

    print "Showing web..."
    # Using internal IP that never changes
    # tabletService.hideWebview()
    tabletService.showWebview("http://" + THIS_MACHINE_IP + ":" + str(PORT) + "/" + YOURHTMLFILE)

    time.sleep(3.0)

    # Clean up
    print "Cleaning up..."
    httpd.shutdown()
    thread.join()

    print "Done"


def index_changer(newtitle, newtext):
    f = open('index.html', 'r')
    content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    res = soup.findAll("p", {"name" : "newstext"})
    res2 = soup.findAll("h1", {"name" : "newstitle"})

    res[0].string = newtext
    res2[0].string = newtitle

    with open("output1.html", "w") as outfile:
        outfile.write(str(soup))


if __name__ == '__main__':
    randport = randint(1001, 8999)
    showpage(PORT=randport)

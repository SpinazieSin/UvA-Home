from naoqi import ALProxy
from naoqi import qi
import os


def display_html(IP, PORT):
    tabletservice = ALProxy("ALTabletService", IP, PORT)
    # print os.getcwd()
    # print os.listdir(".")
    val1 = tabletservice.showWebview("http://198.18.0.1/index.html")
    # val2 = tabletservice.showWebview("")
    # val2 = tabletservice.showWebview("./testpage.html")
    # val3 = tabletservice.showImage("uvahome.png")
    # ALTabletService.showImage("https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg")
    # print("1: " + str(val1))
    print("2: " + str(val2))
    # print("3: " + str(val3))
    # tabletservice.hideWebview()
    # tabletservice.hide()
    # tabletservice.hideWebview()

# def altmethod(IP, PORT):
#     app = qi.Application()
#
#     uid = app.session.packageUid()
#     app.Session.service('ALTabletService').loadApplication(uid)
#
#     # method2: use loadUrl
#
#     # ip = app.session().service('ALTabletService').getRobotIp()
#     url = 'http://' + IP + '/apps/' + uid + '/index.html'
#     app.session.service('ALTabletService').loadUrl(url)
#
#     # at this point, the page is still hidden by default tablet screen
#     app.session.service('ALTabletService').showWebview()


if __name__ == '__main__':
    # display_html("198.18.0.1", 9559)
    # display_html("127.0.0.1", 9559)
    tabletservice = ALProxy("ALTabletService", "pepper.local", 9559)
    boolvar = tabletService.configureWifi("wpa","p-athome-sspl-uva", "baa3cc3b")
    print boolvar
    # display_html("pepper.local", 9559)
    # altmethod("pepper.local", 9559)

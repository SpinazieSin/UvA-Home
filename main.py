import alproxy

class Main:
    def __init__(self):
        self.ALProxy = None

    def main(self):
        self.ALProxy = alproxy.ALProxy("146.50.60.19")
        self.ALProxy.test_all()


# Use the main function
if __name__ == "__main__":
    main = Main()
    main.main()
    print("Done...")
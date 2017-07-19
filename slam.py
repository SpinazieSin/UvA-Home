# Thomas Groot

# Use the script like so:
# localizer = slam.Localization()
# localizer.explore(1.0)
# time.sleep(5)
# localizer.stop_exploration()
# localizer.start_localization()
# print(localizer.get_robot_position())
# localizer.stop_localization()

from naoqi import ALProxy

class Localization(object):
    def __init__(self, Navigation=None):
        if Navigation:
            self.proxy = Navigation
        else:
            self.proxy = ALProxy("ALNavigation", "127.0.0.1", 9559)
        # map_path contains the path to the recently saved map
        self.map_path = None
        # map contains the map object, structure is described in get_map()
        self.map = None
        # this is where the robot thinks he is
        self.estimate_location = [0., 0.]

    # save the map and return the path where it is saved
    def save_exploration(self):
        self.map_path = self.proxy.saveExploration()

    # get the most recent version of the map.
    # the map has the format [mpp, width, height, [originOffsetX, originOffsetY], [pxlVal, ...]]
    # Where mpp is the resolution of the map in meters per pixel,
    # width and height are the size of the image in pixels,
    # originOffset is the metrical offset of the pixel (0, 0) of the map,
    # and [pxlVal, ...] is the buffer of pixel floating point values between 0 (occupied space) and 100 (free space).
    def get_map(self):
        self.map = self.proxy.getMetricalMap()

    # load a map from a given path
    def load_exploration(self, path):
        self.map = self.proxy.loadExploration(path)

    # radius is the size of the exploration area in meters
    def explore(self, radius):
        self.proxy.explore(radius)

    # stop explore()
    def stop_exploration(self):
        self.proxy.stopExploration()
        self.save_exploration()

    # target is of format [x, y]
    def move_to(self, target):
        self.proxy.navigateToInMap(target)
        self.estimate_location = target

    # return an estimate of the current robot position. LOCALIZATION HAS TO BE RUN FIRST
    def get_robot_position(self):
        self.estimate_location =  self.proxy.getRobotPositionInMap()[0]
        return self.estimate_location

    # start localization loop so the robot can estimate its own position. a map has to be loaded
    def start_localization(self):
        self.proxy.startLocalization()

    # stop the localization loop
    def stop_localization(self):
        self.proxy.stopLocatization()

    # estimate target is an estimate of the current position of the robot
    # relocalize in map returns [[x,y], uncertainty]
    def relocalize(self, estimate_target):
        self.estimate_location = self.proxy.relocalizeInMap(estimate_target)[0]


# GETTING A MAP
# Localization_instance.get_map()
# result_map = Localization_instance.map
# map_width = result_map[1]
# map_height = result_map[2]
# img = numpy.array(result_map[4]).reshape(map_width, map_height)
# img = (100 - img) * 2.55 # from 0..100 to 255..0
# img = numpy.array(img, numpy.uint8)
# Image.frombuffer('L',  (map_width, map_height), img, 'raw', 'L', 0, 1).show()

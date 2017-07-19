import headmotions

def track_face_with_head(x, y, w, h, imageWidth, imageHeight, motionProxy):
    headmotions.move_head(x+(w/2), y+(h/2), imageWidth, imageHeight, motionProxy)

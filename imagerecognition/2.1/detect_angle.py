import cv2
import numpy as np

# This script will display video from a live feed,
# then it will find the angle between the vertical
# and a blue line displayed on screen.


def course_correct(frame, tol):
    angle = find_angle(frame, False)

    if angle < 0 - tol:
        # rotate rov counterclockwise
        pass
    elif angle > tol:
        # rotate rov clockwise
        pass


def find_angle(frame, deg):
    width, height, _ = frame.shape

    # convert rgb image to hsv for color isolation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Set bounds for what shades of blue we want
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    # Isolate blue, draw lines on edges
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Isolate lines
    edges = cv2.Canny(mask, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, maxLineGap=50)

    if lines is not None:
        max_len = 0
        max_line = None
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calculate line distances and put them in array
            lineDistance = np.sqrt((x2 - x1) ^ 2 + (y2 - y1) ^ 2)
            if lineDistance > max_len:
                max_line = line

        # find and draw longest line
        x1, y1, x2, y2 = max_line[0]

        dy = y2 - y1
        dx = x2 - x1

        # Angle from vertical (clockwise -> positive angle)
        angle_rad = np.arctan(dx/dy)
        return angle_rad * 180 / np.pi if deg else angle_rad


def main():
    # Grab video feed from source
    # cap = cv2.VideoCapture('http://10.19.52.3:8080/video/mjpeg')
    cap = cv2.VideoCapture(1)
    height, width, _ = cap.read()[1].shape

    while True:
        _, frame = cap.read()

        # convert rgb image to hsv for color isolation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Set bounds for what shades of blue we want
        lower_blue = np.array([100, 150, 0])
        upper_blue = np.array([140, 255, 255])

        # Isolate blue, draw lines on edges
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # ~~~~~~~~~~~~~~~~~~~~~~~ Rectangle Approach ~~~~~~~~~~~~~~~~~~~~~~~~~~
        # bluecnts = cv2.findContours(mask.copy(),
        #                     cv2.RETR_EXTERNAL,
        #                     cv2.CHAIN_APPROX_SIMPLE)[-2]
        # if len(bluecnts) > 0:
        #     blue_area = max(bluecnts, key=cv2.contourArea)
        #     x, y, w, h = cv2.boundingRect(blue_area)
        #     cv2.line(frame, (x, y+h//2), (x+w, y+h//2), (0,255,0), 2)
        #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~ Line approach ~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Isolate lines
        edges = cv2.Canny(mask, 75, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, maxLineGap=50)
        llines = []  # Length of lines array

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

                # Calculate line distances and put them in array
                lineDistance = np.sqrt((x2 - x1) ^ 2 + (y2 - y1) ^ 2)
                llines.append(lineDistance)

            # find and draw longest line
            i_max = llines.index(max(llines))
            x1, y1, x2, y2 = lines[i_max][0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 5)

            dy = y2 - y1
            dx = x2 - x1

            # Angle from vertical (clockwise - positive angle)
            angle = np.arctan(dx/dy) * 180 / np.pi  # output in degrees
            cv2.putText(frame, str(angle), (5, height), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 4, cv2.LINE_AA)

        # draw central vertical
        cv2.line(frame, (width//2, 0), (width//2, height), (0, 0, 255), 5)

        # Show camera image with line
        cv2.imshow('feed', frame)
        # cv2.imshow('mask', mask)

        # Kill on escape key press
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()

    cap.release()


if __name__ == '__main__':
    main()

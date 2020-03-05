import cv2
import numpy as np


# Hello, currently this script will :
# -- Isolate and draw Pink Lines
# -- Identify what kind of lines a pink line is (vertical vs horizontal)
# -- Define what we want the increment barrier to be

def main():
    # process_vid()
    process_img('section.png')


def process_vid(src):
    cam = cv2.VideoCapture(src)

    while(True):
        ret, img = cam.read()

        # Using this requries some slight modification in process_img
        process_img(img)

        cv2.imshow('frame', img)

        if cv2.waitKey(27) == 1:
            break

    # === Free resources ===
    cam.release()
    cv2.destroyAllWindows()


def process_img(filename='raw_grid.png'):
    img = cv2.imread(filename)
    height, width, _ = img.shape
    tol = 0.01
    top = find_grid(img[0:height//2, 0:width], tol)
    bot = find_grid(img[height//2:height, 0:width], tol, height//2)

    # put lines on the image (for visual confirmation)
    draw_lines(top + bot, img, (0, 0, 255))

    # TODO: Find good way to deterimine what the boundaries should be
    expected = height//6
    tol = [0, 10]

    top_at_bound = check_bound(top, expected, 0, tol)
    bot_at_bound = check_bound(top, expected, height, tol)

    # if both are in bound, then we are looking at a new row of cells
    if top_at_bound and bot_at_bound:
        # Update row count and representation
        pass

    # Display image
    cv2.imshow('hough.jpg', img)

    # === Keep image until we want to get rid of it ===
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Draws all polar lines in a given collection onto
# a given image, using a given color and width
def draw_lines(lines, img, color, width=2):
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        cv2.line(img, (x1, y1), (x2, y2), color, width)


# returns a list of the pink mason lines found in the given image/frame
def find_grid(img, tol, offset=0):
    # convert rgb image to hsv for color isolation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Set bounds for what shades of pink we want
    lower_pink = np.array([130, 25, 160])
    upper_pink = np.array([170, 255, 255])

    # Isolate blue, draw lines on edges
    mask = cv2.inRange(hsv, lower_pink, upper_pink)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Isolate lines
    edges = cv2.Canny(mask, 75, 150)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 100)

    if lines is not None:
        rho_threshold = 20
        theta_threshold = 2

        # how many lines are similar to a given one
        similar_lines = {i: [] for i in range(len(lines))}
        for i in range(len(lines)):
            for j in range(len(lines)):
                if i == j:
                    continue

                rho_i, theta_i = lines[i][0]
                rho_j, theta_j = lines[j][0]
                if abs(rho_i - rho_j) < rho_threshold and \
                   abs(theta_i - theta_j) < theta_threshold:
                    similar_lines[i].append(j)

        # ordering the INDECES of the lines by how many are similar to them
        indices = [i for i in range(len(lines))]
        indices.sort(key=lambda x: len(similar_lines[x]))

        # line flags is the base for the filtering
        line_flags = len(lines)*[True]
        for i in range(len(lines) - 1):
            # if we already disregarded the ith element in
            # the ordered list then we don't care
            # (we will not delete anything based on it and
            # we will never reconsider using this line again)
            if not line_flags[indices[i]]:
                continue

            # filter lines which are too similar to each other
            for j in range(i + 1, len(lines)):
                if not line_flags[indices[j]]:
                    continue

                rho_i, theta_i = lines[indices[i]][0]
                rho_j, theta_j = lines[indices[j]][0]
                if abs(rho_i - rho_j) < rho_threshold and \
                   abs(theta_i - theta_j) < theta_threshold:
                    # if it is similar and has not yet been dropped
                    line_flags[indices[j]] = False

        # print('number of Hough lines:', len(lines))

        filtered_lines = []

        # Filter lines which are horizontal out, return these
        for i in range(len(lines)):
            the = lines[i][0][1]
            if line_flags[i] and abs(np.pi/2 - the) <= tol:
                # ensure lines are at correct height
                # relative to original image before packing
                lines[i][0][0] += offset
                filtered_lines.append(lines[i])

        # print('Number of filtered lines:', len(filtered_lines))

        return filtered_lines


# returns a boolean if one line in a given collection is
# an expected distance away from a specified y-coordinate,
# within a given tolerance
def check_bound(lines, expected, frame_end, tol=[0, 10]):
    for line in lines:
        rho, _ = line[0]
        actual = abs(rho - frame_end)

        diff = abs(actual - expected)
        if diff >= tol[0] and diff <= tol[1]:
            return True

    # if we haven't found anything in bounds, report it
    return False


if __name__ == '__main__':
    main()

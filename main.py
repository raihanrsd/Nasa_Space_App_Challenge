from simpleimage import SimpleImage
import PIL
from PIL import Image
import requests
import math

prompt = input("Is it a nasa provided image or raw area footage?(input y if it's a nasa provided image)")
if prompt == "y" or prompt =="Y":
    INTENSITY_THRESHOLD = 2.0
else:
    INTENSITY_THRESHOLD = 1.2
DEFAULT_FILE = 'random-fire.jpeg'

ANALYSED_AREA = {
    "California": ["California", 36.66, 36.42, -118.98, -118.57, 36.543243, -118.6897886, 959.97, "north-east", 382.765, 52.34],
    "Brazil": ["Brazil", -19.77, -19.52, -57.79, -57.33, -19.5665646, -57.6757788, 1454.45, "north_west", 874.891, 92.75],
    "Botswana": ["Botswana", -23.643, -23.106, 23.281, 22.358, -23.4556454, 22.9898493, 5655.85, "south", 984.252, 58.84],
    "Australia": ["Australia", -17.173, -16.957, 145.08, 144.682, -16.9898988, 144.784783984, 1013.16, "south", 492.126, 39.67],
    "Saskatchewan": ["Saskatchewan", 53.424, 53.097, -103.045, -102.489, 53.2343432, -102.987878, 1344.37, "north-west", 929.571, 39.23]
}



def main():
    # Get file and load image
    filename = get_file()
    image = SimpleImage(filename[0])

    distance = get_distance(filename[1])

    # Show the original fire
    original_fire = SimpleImage(filename[0])

    # Show the highlighted fire
    highlighted_fire = find_flames(filename[0])

    image_list = [highlighted_fire]

    # identifies the direction of fire propagation
    direction = determine_direction(filename[1])

    # mark the danger zone
    marked_image = mark_image(highlighted_fire, direction, image_list, distance)

    highest_lat = get_highest_lat(filename[1])

    highest_lon = get_highest_lon(filename[1])

    lowest_lat = get_lowest_lat(filename[1])

    lowest_lon = get_lowest_lon(filename[1])

    lat = get_lat(filename[1])

    lon = get_lon(filename[1])

    locate_the_user = locate_user(marked_image, lat, lon, highest_lat, highest_lon, lowest_lat, lowest_lon,
                                  image_list, distance)
    print(len(image_list))

    x = longitude_to_x(highest_lon, lowest_lon, lon, locate_the_user)
    y = latitude_to_y(highest_lat, lowest_lat, lat, locate_the_user)

    danger_prompt = user_danger_tracking(locate_the_user, x, y, image_list)

    locate_the_user.show()
    if ANALYSED_AREA.get(filename[1]) is not None:
        locate_the_user.save(filename[1] + ".png")
    else:
        locate_the_user.save("img1.png")

    print(danger_prompt)

    area_burned = area_determiner(locate_the_user, image_list, filename[1])

    print('The total area burning is ' + str(area_burned[0]) + " square kilometers.")
    print('The total area that may burn is ' + str(area_burned[1]) + " square kilometers.")


def get_distance(filename):
    velocity = input('Enter the wind velocity in feet per second(or press enter for default): ')
    hours = input("Input the required hour of which you want to see the prediction(click enter for one day.")
    if hours == "":
        hours = 24
    if velocity == '' and ANALYSED_AREA.get(filename) is None:
        velocity = 500
    elif velocity == '' and ANALYSED_AREA.get(filename) is not None:
        velocity = ANALYSED_AREA[filename][9]
    spread_per_minute = (3.14 * (10 ** -3)) * (float(velocity) ** 1.37) * (1.12 ** -0.398)
    print(spread_per_minute)
    distance = spread_per_minute * 60 * float(hours) / 3280.84
    distance_pix = round((distance / ANALYSED_AREA[filename][10]) * 1280)
    print(distance)
    print(distance_pix)
    return distance_pix


def mark_image(image, direction, image_list, distance):
    if direction == "south-east":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x + 1 < image.width:
                    pixel2 = image.get_pixel(x + 1, y)
                if pixel.red == 255:
                    for i in range(distance):
                        if x + 1 + i < image.width and pixel2.red != 255:
                            image.set_pixel(x + i, y, pixel1)
                        if x + i + 1 < image.width:
                            pixel2 = image.get_pixel(x + i + 1, y)
                        if x + 1 + i < image.width:
                            pixel1 = yellow_img.get_pixel(x + 1 + i, y)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height and y - 1 > 0:
                    pixel2 = image2.get_pixel(x, y + 1)
                    pixel3 = image2.get_pixel(x, y - 1)
                    pixel4 = yellow_img.get_pixel(x, y + 1)
                    pixel5 = yellow_img.get_pixel(x, y - 1)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance):
                        if pixel2.red != 255 and y + i < image.height:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i < image.height and y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)
                            pixel4 = yellow_img.get_pixel(x, y + 1 + i)
                            pixel = image2.get_pixel(x, y + i)
                            pixel1 = yellow_img.get_pixel(x, y + i)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height:
                    pixel2 = image.get_pixel(x, y + 1)
                if pixel.red == 255:
                    for i in range(distance):
                        if y + 1 + i < image.height and pixel2.red != 255:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i + 1 < image.height:
                            pixel2 = image.get_pixel(x, y + i + 1)
                        if y + 1 + i < image.height:
                            pixel1 = yellow_img.get_pixel(x, y + 1 + i)
        return image




    elif direction == "north-east":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x + 1 < image.width:
                    pixel2 = image.get_pixel(x + 1, y)
                if pixel.red == 255:
                    for i in range(distance):
                        if x + 1 + i < image.width and pixel2.red != 255:
                            image.set_pixel(x + i, y, pixel1)
                        if x + i + 1 < image.width:
                            pixel2 = image.get_pixel(x + i + 1, y)
                        if x + 1 + i < image.width:
                            pixel1 = yellow_img.get_pixel(x + 1 + i, y)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height and y - 1 > 0:
                    pixel2 = image2.get_pixel(x, y + 1)
                    pixel3 = image2.get_pixel(x, y - 1)
                    pixel4 = yellow_img.get_pixel(x, y + 1)
                    pixel5 = yellow_img.get_pixel(x, y - 1)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance):
                        if pixel2.red != 255 and y - i > 0:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)
                            pixel5 = yellow_img.get_pixel(x, y - 1 - i)
                            pixel = image2.get_pixel(x, y - i)
                            pixel1 = yellow_img.get_pixel(x, y - i)
                        if y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y - 1 > 0:
                    pixel2 = image.get_pixel(x, y - 1)
                if pixel.red == 255:
                    for i in range(distance):
                        if y - 1 - i > 0 and pixel2.red != 255:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i - 1 > 0:
                            pixel2 = image.get_pixel(x, y - i - 1)
                            pixel1 = yellow_img.get_pixel(x, y - 1 - i)
        return image


    # for eastern direction
    elif direction == "east":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x + 1 < image.width:
                    pixel2 = image.get_pixel(x + 1, y)
                if pixel.red == 255:
                    for i in range(distance):
                        if x + 1 + i < image.width and pixel2.red != 255:
                            image.set_pixel(x + i, y, pixel1)
                        if x + i + 1 < image.width:
                            pixel2 = image.get_pixel(x + i + 1, y)
                        if x + 1 + i < image.width:
                            pixel1 = yellow_img.get_pixel(x + 1 + i, y)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height and y - 1 > 0:
                    pixel2 = image2.get_pixel(x, y + 1)
                    pixel3 = image2.get_pixel(x, y - 1)
                    pixel4 = yellow_img.get_pixel(x, y + 1)
                    pixel5 = yellow_img.get_pixel(x, y - 1)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and y - i > 0:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)
                            pixel5 = yellow_img.get_pixel(x, y - 1 - i)
                            pixel = image2.get_pixel(x, y - i)
                            pixel1 = yellow_img.get_pixel(x, y - i)
                        if y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and y + i < image.height:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i < image.height and y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)
                            pixel4 = yellow_img.get_pixel(x, y + 1 + i)
                            pixel = image2.get_pixel(x, y + i)
                            pixel1 = yellow_img.get_pixel(x, y + i)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)

        return image


    # for propagation of fire at the west direction

    elif direction == "west":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x - 1 > 0:
                    pixel2 = image.get_pixel(x - 1, y)
                if pixel.red == 255:
                    for i in range(distance):
                        if x - 1 - i > 0 and pixel2.red != 255:
                            image.set_pixel(x - i, y, pixel1)
                        if x - i - 1 > 0:
                            pixel2 = image.get_pixel(x - i - 1, y)
                        if x - 1 - i > 0:
                            pixel1 = yellow_img.get_pixel(x - 1 - i, y)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height and y - 1 > 0:
                    pixel2 = image2.get_pixel(x, y + 1)
                    pixel3 = image2.get_pixel(x, y - 1)
                    pixel4 = yellow_img.get_pixel(x, y + 1)
                    pixel5 = yellow_img.get_pixel(x, y - 1)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and y - i > 0:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)
                            pixel5 = yellow_img.get_pixel(x, y - 1 - i)
                            pixel = image2.get_pixel(x, y - i)
                            pixel1 = yellow_img.get_pixel(x, y - i)
                        if y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and y + i < image.height:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i < image.height and y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)
                            pixel4 = yellow_img.get_pixel(x, y + 1 + i)
                            pixel = image2.get_pixel(x, y + i)
                            pixel1 = yellow_img.get_pixel(x, y + i)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)

        return image

    # for propagation of fire at the south-west direction

    elif direction == "south-west":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        yellow_img.show()

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x - 1 > 0:
                    pixel2 = image.get_pixel(x - 1, y)
                if pixel.red == 255:
                    for i in range(distance):
                        if x - 1 - i > 0 and pixel2.red != 255:
                            image.set_pixel(x - i, y, pixel1)
                        if x - i - 1 > 0:
                            pixel2 = image.get_pixel(x - i - 1, y)
                        if x - 1 - i > 0:
                            pixel1 = yellow_img.get_pixel(x - 1 - i, y)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height and y - 1 > 0:
                    pixel2 = image2.get_pixel(x, y + 1)
                    pixel3 = image2.get_pixel(x, y - 1)
                    pixel4 = yellow_img.get_pixel(x, y + 1)
                    pixel5 = yellow_img.get_pixel(x, y - 1)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance):
                        if pixel2.red != 255 and y + i < image.height:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i < image.height and y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)
                            pixel4 = yellow_img.get_pixel(x, y + 1 + i)
                            pixel = image2.get_pixel(x, y + i)
                            pixel1 = yellow_img.get_pixel(x, y + i)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height:
                    pixel2 = image.get_pixel(x, y + 1)
                if pixel.red == 255:
                    for i in range(distance):
                        if y + 1 + i < image.height and pixel2.red != 255:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i + 1 < image.height:
                            pixel2 = image.get_pixel(x, y + i + 1)
                        if y + 1 + i < image.height:
                            pixel1 = yellow_img.get_pixel(x, y + 1 + i)
        return image


    # for propagation of fire at the north-west direction

    elif direction == "north-west":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x - 1 > 0:
                    pixel2 = image.get_pixel(x - 1, y)
                if pixel.red == 255:
                    for i in range(distance):
                        if x - 1 - i > 0 and pixel2.red != 255:
                            image.set_pixel(x - i, y, pixel1)
                        if x - i - 1 > 0:
                            pixel2 = image.get_pixel(x - i - 1, y)
                        if x - 1 - i > 0:
                            pixel1 = yellow_img.get_pixel(x - 1 - i, y)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height and y - 1 > 0:
                    pixel2 = image2.get_pixel(x, y + 1)
                    pixel3 = image2.get_pixel(x, y - 1)
                    pixel4 = yellow_img.get_pixel(x, y + 1)
                    pixel5 = yellow_img.get_pixel(x, y - 1)
                if pixel.green == pixel1.green and pixel.red != 255 and y + 1 < image.height and y - 1 > 0:
                    for i in range(distance):
                        if pixel2.red != 255 and y - i > 0:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i > 0 and y - 1 - i > 0:
                            pixel3 = image2.get_pixel(x, y - 1 - i)
                            pixel5 = yellow_img.get_pixel(x, y - 1 - i)
                            pixel = image2.get_pixel(x, y - i)
                            pixel1 = yellow_img.get_pixel(x, y - i)
                        if y + 1 + i < image.height:
                            pixel2 = image2.get_pixel(x, y + 1 + i)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y - 1 > 0:
                    pixel2 = image.get_pixel(x, y - 1)
                if pixel.red == 255:
                    for i in range(distance):
                        if y - 1 - i > 0 and pixel2.red != 255:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i - 1 > 0:
                            pixel2 = image.get_pixel(x, y - i - 1)
                            pixel1 = yellow_img.get_pixel(x, y - 1 - i)
        return image



    # propagation of fire towards the north direction

    elif direction == "north":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y - 1 > 0:
                    pixel2 = image.get_pixel(x, y - 1)
                if pixel.red == 255:
                    for i in range(distance):
                        if y - 1 - i > 0 and pixel2.red != 255:
                            image.set_pixel(x, y - i, pixel1)
                        if y - i - 1 > 0:
                            pixel2 = image.get_pixel(x, y - i - 1)
                            pixel1 = yellow_img.get_pixel(x, y - 1 - i)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x + 1 < image.width and x - 1 > 0:
                    pixel2 = image2.get_pixel(x + 1, y)
                    pixel3 = image2.get_pixel(x - 1, y)
                    pixel4 = yellow_img.get_pixel(x + 1, y)
                    pixel5 = yellow_img.get_pixel(x - 1, y)
                if pixel.green == pixel1.green and pixel.red != 255 and x + 1 < image.width and x - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and x - i > 0:
                            image.set_pixel(x - i, y, pixel1)
                        if x - i > 0 and x - 1 - i > 0:
                            pixel3 = image2.get_pixel(x - 1 - i, y)
                            pixel5 = yellow_img.get_pixel(x - 1 - i, y)
                            pixel = image2.get_pixel(x - i, y)
                            pixel1 = yellow_img.get_pixel(x - i, y)
                        if x + 1 + i < image.width:
                            pixel2 = image2.get_pixel(x + 1 + i, y)
                if pixel.green == pixel1.green and pixel.red != 255 and x + 1 < image.width and x - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and y + i < image.height:
                            image.set_pixel(x + i, y, pixel1)
                        if x + i < image.width and x + 1 + i < image.width:
                            pixel2 = image2.get_pixel(x + 1 + i, y)
                            pixel4 = yellow_img.get_pixel(x + 1 + i, y)
                            pixel = image2.get_pixel(x + i, y)
                            pixel1 = yellow_img.get_pixel(x + i, y)
                        if x - i > 0 and x - 1 - i > 0:
                            pixel3 = image2.get_pixel(x + 1 + i, y)

        return image


    # propagation of fire towards the north direction

    elif direction == "south":
        yellow_img = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                yellow_img.set_pixel(x, y, pixel)

        for pixel in yellow_img:
            if pixel.red * 3 < 255:
                pixel.red = pixel.red * 3
            else:
                pixel.red = 254
            if pixel.green * 2 < 255:
                pixel.green = pixel.green * 2
            else:
                pixel.green = 255
        image_list.append(yellow_img)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if y + 1 < image.height:
                    pixel2 = image.get_pixel(x, y + 1)
                if pixel.red == 255:
                    for i in range(distance):
                        if y + 1 + i < image.height and pixel2.red != 255:
                            image.set_pixel(x, y + i, pixel1)
                        if y + i + 1 < image.height:
                            pixel2 = image.get_pixel(x, y + i + 1)
                            pixel1 = yellow_img.get_pixel(x, y + 1 + i)

        image2 = SimpleImage.blank(image.width, image.height)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.get_pixel(x, y)
                image2.set_pixel(x, y, pixel)
        image_list.append(image2)

        for x in range(image.width):
            for y in range(image.height):
                pixel = image2.get_pixel(x, y)
                pixel1 = yellow_img.get_pixel(x, y)
                if x + 1 < image.width and x - 1 > 0:
                    pixel2 = image2.get_pixel(x + 1, y)
                    pixel3 = image2.get_pixel(x - 1, y)
                    pixel4 = yellow_img.get_pixel(x + 1, y)
                    pixel5 = yellow_img.get_pixel(x - 1, y)
                if pixel.green == pixel1.green and pixel.red != 255 and x + 1 < image.width and x - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and x - i > 0:
                            image.set_pixel(x - i, y, pixel1)
                        if x - i > 0 and x - 1 - i > 0:
                            pixel3 = image2.get_pixel(x - 1 - i, y)
                            pixel5 = yellow_img.get_pixel(x - 1 - i, y)
                            pixel = image2.get_pixel(x - i, y)
                            pixel1 = yellow_img.get_pixel(x - i, y)
                        if x + 1 + i < image.width:
                            pixel2 = image2.get_pixel(x + 1 + i, y)
                if pixel.green == pixel1.green and pixel.red != 255 and x + 1 < image.width and x - 1 > 0:
                    for i in range(distance // 4):
                        if pixel2.red != 255 and y + i < image.height:
                            image.set_pixel(x + i, y, pixel1)
                        if x + i < image.width and x + 1 + i < image.width:
                            pixel2 = image2.get_pixel(x + 1 + i, y)
                            pixel4 = yellow_img.get_pixel(x + 1 + i, y)
                            pixel = image2.get_pixel(x + i, y)
                            pixel1 = yellow_img.get_pixel(x + i, y)
                        if x - i > 0 and x - 1 - i > 0:
                            pixel3 = image2.get_pixel(x + 1 + i, y)

        return image


def find_flames(filename):
    """
    This function should highlight the "sufficiently red" pixels
    in the image and grayscale all other pixels in the image
    in order to highlight areas of wildfires.
    """
    image = SimpleImage(filename)
    for pixel in image:
        average = (pixel.red + pixel.green + pixel.blue) // 3
        if pixel.red >= average * INTENSITY_THRESHOLD:
            pixel.red = 255
            pixel.green = 0
            pixel.blue = 0
        else:
            pixel.red = average
            pixel.blue = average
            pixel.green = average
    return image


def get_file():
    # Read image file path from user, or use the default file
    filename = input('Enter image file (or press enter for default): ')
    if ANALYSED_AREA.get(filename) is not None:
        return ["images/" + ANALYSED_AREA[filename][0] + ".jpg", filename]
    elif filename == '':
        filename = DEFAULT_FILE


    return ["images/" + filename, filename]


def determine_direction(filename):
    # Read image file path from user, or use the default file
    direction = input('Enter the direction for fire propagation(or press enter for default): ')
    if direction == '' and ANALYSED_AREA.get(filename) is None:
        direction = "south-east"
    elif direction == '' and ANALYSED_AREA.get(filename) is not None:
        direction = ANALYSED_AREA[filename][8]
    return direction


def get_highest_lat(filename):
    value = input("Provide the highest latitude of the visualised area: ")
    if value == "" and ANALYSED_AREA.get(filename) is None:
        value = 36.27
    if value == "" and ANALYSED_AREA.get(filename) is not None:
        value = ANALYSED_AREA[filename][1]
    if float(value) < 0:
        value = 0 - float(value)
    print(value)
    return float(value)


def get_highest_lon(filename):
    value = input("Provide the highest longitude of the visualised area: ")
    if value == "" and ANALYSED_AREA.get(filename) is None:
        value = 94.43
    if value == "" and ANALYSED_AREA.get(filename) is not None:
        value = ANALYSED_AREA[filename][3]
    if float(value) < 0:
        value = 0 - float(value)
    print(value)
    return float(value)


def get_lowest_lat(filename):
    value = input("Provide the lowest latitude of the visualised area: ")
    if value == "" and ANALYSED_AREA.get(filename) is None:
        value = 33
    if value == "" and ANALYSED_AREA.get(filename) is not None:
        value = ANALYSED_AREA[filename][2]
    if float(value) < 0:
        value = 0 - float(value)
    print(value)
    return float(value)


def get_lowest_lon(filename):
    value = input("Provide the lowest longitude of the visualised area: ")
    if value == "" and ANALYSED_AREA.get(filename) is None:
        value = 90.27
    if value == "" and ANALYSED_AREA.get(filename) is not None:
        value = ANALYSED_AREA[filename][4]
    if float(value) < 0:
        value = 0 - float(value)
    print(value)
    return float(value)


def get_lat(filename):
    value = input("Provide the user latitude of the visualised area: ")
    if value == "" and ANALYSED_AREA.get(filename) is None:
        value = 33.4
    if value == "" and ANALYSED_AREA.get(filename) is not None:
        value = ANALYSED_AREA[filename][5]
    if float(value) < 0:
        value = 0 - float(value)
    print(value)
    return float(value)


def get_lon(filename):
    value = input("Provide the user longitude of the visualised area: ")
    if value == "" and ANALYSED_AREA.get(filename) is None:
        value = 93
    if value == "" and ANALYSED_AREA.get(filename) is not None:
        value = ANALYSED_AREA[filename][6]
    if float(value) < 0:
        value = 0 - float(value)
    print(value)
    return float(value)


def locate_user(image, lat, lon, highest_lat, highest_lon, lowest_lat, lowest_lon, lst, distance):
    x = longitude_to_x(highest_lon, lowest_lon, lon, image)
    y = latitude_to_y(highest_lat, lowest_lat, lat, image)
    # if the pixel is in bounds of the window we specified through constants,
    # plot it
    if 0<x<image.width and 0<y<image.height:
        plot_pixel(image, x, y, lst)
    return image


def longitude_to_x(highest_lon, lowest_lon, lon, image):
    """
    Scales a longitude coordinate to a coordinate in the visualization email
    """
    return image.width * ((lon - lowest_lon) / (highest_lon - lowest_lon))


def latitude_to_y(highest_lat, lowest_lat, lat, image):
    """
    Scales a latitude coordinate to a coordinate in the visualization email
    """
    return image.height * (1 - (lat - lowest_lat) / (highest_lat - lowest_lat))


def plot_pixel(image, a, b, lst):
    """
    Set a pixel at a particular coordinate to be blue.

    Note that we don't return anything in this function because the Pixel is
    'mutated' in place

    Parameters:
        - `visualization` is the SimpleImage that will eventually be
          shown to the user
        - `x` is the x coordinate of the pixel that we are turning blue
        - `y` is the y coordinate of the pixel that we are turning blue
    """
    pixel = image.get_pixel(a, b)
    pixel.red = 0
    pixel.green = 0
    pixel.blue = 255

    image1 = SimpleImage.blank(image.width, image.height)
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.get_pixel(x, y)
            image1.set_pixel(x, y, pixel)
    for i in range(10):
        if a + i < image.width:
            pixel = image.get_pixel(a + i, b)
            pixel.red = 0
            pixel.green = 0
            pixel.blue = 255
        if a - i > 0:
            pixel = image.get_pixel(a - i, b)
            pixel.red = 0
            pixel.green = 0
            pixel.blue = 255

    image1 = SimpleImage.blank(image.width, image.height)
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.get_pixel(x, y)
            image1.set_pixel(x, y, pixel)

    for x in range(image.width):
        for y in range(image.height):
            pixel = image1.get_pixel(x, y)
            pixel1 = image.get_pixel(x, y)
            if pixel.blue == 255 and pixel.red == 0:
                for i in range(10):
                    if y + i < image.height:
                        pixel = image.get_pixel(x, y + i)
                        pixel.red = 0
                        pixel.green = 0
                        pixel.blue = 255
                    if y - i > 0:
                        pixel = image.get_pixel(x, y - i)
                        pixel.red = 0
                        pixel.green = 0
                        pixel.blue = 255
    image1.show()
    lst.append(image1)
    lst.append(image1)
    print(len(lst))


def user_danger_tracking(image, a, b, lst):
    prompt = ''
    for i in range(25):
        pixel = image.get_pixel(a, b)
        pixel1 = lst[1].get_pixel(a, b)
        pixel2 = lst[3].get_pixel(a, b)
        if a + i < image.width:
            pixel = image.get_pixel(a + i, b)
            pixel1 = lst[1].get_pixel(a + i, b)
            pixel2 = lst[3].get_pixel(a + i, b)
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if a - i > 0:
            pixel = image.get_pixel(a - i, b)
            pixel1 = lst[1].get_pixel(a - i, b)
            pixel2 = lst[3].get_pixel(a - i, b)
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if b + i < image.height:
            pixel = image.get_pixel(a, b + i)
            pixel1 = lst[1].get_pixel(a, b + i)
            pixel2 = lst[3].get_pixel(a, b + i)
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if b - i > 0:
            pixel = image.get_pixel(a, b - i)
            pixel1 = lst[1].get_pixel(a, b - i)
            pixel2 = lst[3].get_pixel(a, b - i)
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if a + (i // 1.5) < image.width and b + (i // 1.5) < image.height:
            pixel = image.get_pixel(a + (i // 1.5), b + (i // 1.5))
            pixel1 = lst[1].get_pixel(a + (i // 1.5), b + (i // 1.5))
            pixel2 = lst[3].get_pixel(a + (i // 1.5), b + (i // 1.5))
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if a - (i // 1.5) > 0 and b + (i // 1.5) < image.height:
            pixel = image.get_pixel(a - (i // 1.5), b + (i // 1.5))
            pixel1 = lst[1].get_pixel(a - (i // 1.5), b + (i // 1.5))
            pixel2 = lst[3].get_pixel(a - (i // 1.5), b + (i // 1.5))
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if b - (i // 1.5) > 0 and a + (i // 1.5) < image.width:
            pixel = image.get_pixel(a + (i // 1.5), b - (i // 1.5))
            pixel1 = lst[1].get_pixel(a + (i // 1.5), b - (i // 1.5))
            pixel2 = lst[3].get_pixel(a + (i // 1.5), b - (i // 1.5))
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"
        if b - (i // 1.5) > 0 and a - (i // 1.5) > 0:
            pixel = image.get_pixel(a - (i // 1.5), b - (i // 1.5))
            pixel1 = lst[1].get_pixel(a - (i // 1.5), b - (i // 1.5))
            pixel2 = lst[3].get_pixel(a - (i // 1.5), b - (i // 1.5))
            pixel.green = 255
            pixel.red = 0
            pixel.blue = 0
            if pixel1.red == pixel2.red:
                prompt = "You are in the immediate danger zone."
            if pixel2 == 255:
                prompt = "You are burning. Runnn!!!"

    if prompt == '':
        prompt = "You are in the Safe Zone."
    return prompt


def area_determiner(image, image_list, filename):
    burn_list = []
    red_pixels = 0
    total_pixels = 0
    yel_pix = 0
    for pixel in image:
        average = (pixel.red + pixel.green + pixel.blue) // 3
        if pixel.red >= average * INTENSITY_THRESHOLD:
            red_pixels += 1
        total_pixels += 1
    total_area_burning = (red_pixels / total_pixels) * ANALYSED_AREA[filename][7]
    burn_list.append(total_area_burning)

    for x in range(image.width):
        for y in range(image.height):
            pixel = image.get_pixel(x, y)
            pixel1 = image_list[1].get_pixel(x, y)
            if pixel.red == pixel1.red and pixel.green == pixel1.green:
                yel_pix += 1
    area_to_be_burned = (yel_pix / total_pixels) * ANALYSED_AREA[filename][7]
    burn_list.append(area_to_be_burned)
    return burn_list


if __name__ == '__main__':
    main()

# ----------------------------------------------------------------------
# Name:        matchit.py
# Purpose:     Implement a single player matching game
#
# Author(s): Tri Le & Derian Lemus
# ----------------------------------------------------------------------
"""
A single player matching game.

usage: matchit.py [-h] [-f] {blue,green,magenta} image_folder
positional arguments:
  {blue,green,magenta}  What color would you like for the player?
  image_folder          What folder contains the game images?

optional arguments:
  -h, --help            show this help message and exit
  -f, --fast            Fast or slow game?
"""
import sys
import tkinter
import os
import random
import argparse


def directory_type(entered_image_folder):
    """
    This function validates that folder selected contains 8 images
    :param entered_image_folder: (string) name of the folder entered by user
    :return: image_folder (string) only if it is valid
    """
    image_folder = os.path.join(os.curdir, entered_image_folder)
    if os.path.exists(image_folder):
        file = os.listdir(image_folder)
        count = 0
        for file_name in file:
            if os.path.splitext(file_name)[1] == '.gif':
                count += 1

        if count >= 8:
            return image_folder
        else:
            print(f'COUNT: {count}')
            raise argparse.ArgumentTypeError(
                f'{entered_image_folder} must contain at least 8 gif images')
    else:
        raise argparse.ArgumentTypeError(f'{entered_image_folder}'
                                         f' is not a valid folder')


def get_arguments():
    """
    This function gets and validates the parameters for the game
    :return: The parameters for the game (int) fast, (string) color,
    and (string) image_folder.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('color',
                        help='What color would you like for the player?',
                        choices=['blue', 'green', 'magenta'])

    parser.add_argument('-f', '--fast',
                        help='Fast or slow game?',
                        action='store_true')

    parser.add_argument('image_folder',
                        help='What folder contains the game images?',
                        type=directory_type)

    arguments = parser.parse_args()
    fast = arguments.fast
    color = arguments.color
    image_folder = arguments.image_folder
    return fast, color, image_folder


class MatchGame(object):
    """
    GUI Game class for a matching game.

    Arguments:
    parent: the root window object
    player_color (string): the color to be used for the matched tiles
    folder (string) the folder containing the images for the game
    delay (integer) how many milliseconds to wait before flipping a tile

    Attributes:
    score (int): number of points the user has throughout the game
    color (string): the color to be used for the matched tiles
    timer (int): time it takes to update score
    count (int): number of pair flips the user has done
    image_list (list): contains 8 images from given directory
    image_dict (dictionary): contains an image with an assigned id
    image_to_compare(list): used to compare two selected images

    """

    def __init__(self, parent, player_color, folder, delay):
        parent.title('Match it!')
        self.score = 100
        self.color = player_color
        self.timer = delay * 1000
        self.count = 0
        os.chdir(folder)
        self.image_list = []
        self.image_dict = {}
        self.image_to_compare = []
        # generate a random list of 16 images with 8 duplicate pairs
        for file_name in os.listdir():
            if file_name.endswith('.gif'):
                image = tkinter.PhotoImage(file=file_name)
                self.image_dict.update({file_name: image})
                self.image_list.append(image)
        self.folder_images = 2 * self.image_list
        random.shuffle(self.folder_images)
        # Create the restart button widget
        restart_button = tkinter.Button(parent, text='RESTART', width=30,
                                        command=self.restart)
        restart_button.grid()
        # Create a canvas widget
        self.canvas = tkinter.Canvas(parent, width=502, height=502,
                                     background='black')
        # Create the 4x4 matrix grid for the game
        for x in range(0, 500, 125):
            for y in range(0, 500, 125):
                self.canvas.create_rectangle(5 + x, 5 + y, 125 + x, 125 + y,
                                             outline=self.color, width=5,
                                             fill='yellow', tag="box current")
        # Detect mouse left click
        self.canvas.bind("<Button-1>", self.play)

        self.canvas.grid()
        self.scoreboard = tkinter.Label(parent, text=f'Score: {self.score}',
                                        fg="blue", font=("Helvetica", 32),
                                        height=2)

        self.scoreboard.grid()

    def restart(self):
        """
        This method is invoked when player clicks on the RESTART button.
        It shuffles and reassigns the images and resets the GUI and the
        score.
        :return: None
        """
        self.score = 100
        self.count = 0
        self.scoreboard.configure(fg="blue",
                                  font=("Helvetica", 32),
                                  height=2)
        self.score_update()
        random.shuffle(self.folder_images)
        self.canvas.itemconfigure("done", fill='yellow', tag="box current")

    def play(self, event):
        """
        This method is invoked when the user clicks on a square.
        It implements the basic controls of the game.
        :param event: event (Event object) describing the click event
        :return: None
        """
        square_clicked = self.canvas.find_closest(event.x, event.y)
        item_id = square_clicked[0]
        # Max 2 square are selected at a time
        if len(self.image_to_compare) <= 1:
            if self.canvas.itemcget(square_clicked, "tag") == "box current":
                if self.canvas.itemcget(item_id, "fill") == 'yellow':
                    self.canvas.itemconfigure(item_id, tag="selected")
                    x1, y1, x2, y2 = self.canvas.coords(item_id)
                    x = (x2 - x1) / 2
                    y = (y2 - y1) / 2
                    get_image = self.folder_images[item_id - 1]
                    self.canvas.create_image(x1 + x, y1 + y, image=get_image,
                                             tag="image")
                    self.image_to_compare.append(
                        self.folder_images[item_id - 1])
            self.match_check()

        if len(self.canvas.find_withtag("done")) == 16:
            print("done")
            self.game_over()

    def match_check(self):
        """
        Handles whether the two cards selected match and updates score
        :return: none
        """
        image_match = False
        if len(self.image_to_compare) == 2:
            self.count += 1
            if self.image_to_compare[0] == self.image_to_compare[1]:
                image_match = True

            if image_match:
                self.canvas.itemconfigure("selected", fill=self.color,
                                          tag="done")

            if self.count > 13:
                self.score = self.score - 10
                self.score_update()
            self.canvas.after(self.timer, self.disappear)

    def disappear(self):
        """
        This method deletes a the selected matching cards from the canvas.
        :return: none
        """
        self.canvas.delete('image')
        self.image_to_compare.clear()
        self.canvas.itemconfigure("selected", tag="box current")

    def score_update(self):
        """
        This method handles updating the score
        :return:none
        """
        self.scoreboard.configure(text=f'Score: {self.score}')
        self.scoreboard.update()

    def game_over(self):
        """
        This method handles the results once the game is over
        :return:none
        """
        self.scoreboard.configure(text=f'Game Over!\n'
                                       f'Score: {self.score}\n'
                                       f'Number of tries: {self.count}',
                                  fg="red",
                                  font=("Helvetica", 16),
                                  height=4)
        self.scoreboard.update()


def main():
    # Retrieve and validate the command line arguments using argparse
    fast, color, image_folder = get_arguments()
    speed = 3
    if fast:
        speed = 1
    # Instantiate a root window
    root = tkinter.Tk()
    # Instantiate a MatchGame object with the correct arguments
    game = MatchGame(root, color, image_folder, speed)
    # Enter the main event loop
    root.mainloop()


if __name__ == '__main__':
    main()

# Map-fun - version 1
import copy
import os
import string
import time

class Location(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "[" + str(self.x) + "/" + str(self.y) + "]"

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

class TrackingPoint(Location):
    def __init__(self, location, path_covered, choices, map_snapshot):
        self.x = location.getX()
        self.y = location.getY()
        self.path_covered = path_covered
        self.choices = choices
        #self.map_snapshot = copy.deepcopy(map_snapshot)
        self.map_snapshot = map_snapshot

    def __str__(self):
        return "Location: " + str(self.x) + "/" + \
                str(self.y) + "\n" + \
                "Directions: " + str(self.choices) + "\n"

    def get_location(self):
        return(Location(self.x, self.y))

    def get_path_covered(self):
        return self.path_covered

    def get_choices(self):
        return self.choices

    def get_map_snapshot(self):
        return copy.deepcopy(self.map_snapshot)
        #return self.map_snapshot

    def remove_choices(self, choice):
        self.choices = self.choices.replace(choice, '')

class Map(object):
    def __init__(self, map_array):
        self.array = map_array
        self.start = Location(1, 1)
        self.goal = Location(10, 10)
        self.update_field_value(self.start, 'A')
        self.update_field_value(self.goal, 'B')

    def __str__(self):
        return str(self.array)

    def show(self):
        for row in self.array:
            for field in row:
                if field == 1:
                    print "X",
                if field == 'A':
                    print "A",
                if field == 'B':
                    print "B",
                elif field == 'X':
                    print ".",
                elif field == 0:
                    print " ",
            print

    def get_goal(self):
        return self.goal

    def get_field_value(self, loc):
        return self.array[loc.getX()][loc.getY()]

    def snapshot(self):
        return copy.deepcopy(self.array)

    def update_field_value(self, loc, value):
        self.array[loc.getX()][loc.getY()] = str(value)

    def update_array(self, array):
        self.array = array

    def get_neighbours(self, loc):
        row = loc.getX()
        col = loc.getY()

        neighbours = [Location(row - 1, col),
                       Location(row, col - 1),
                       Location(row, col + 1),
                       Location(row + 1, col)]
        return [neighbour for neighbour in neighbours]

    def get_possible_ways(self, loc):
        possibilities = ""
        for i, neighbour in enumerate(self.get_neighbours(loc)):
            if (self.get_field_value(neighbour) ==  0  or
                self.get_field_value(neighbour) == "B"):
                    if i == 0: possibilities += "N"
                    if i == 1: possibilities += "W"
                    if i == 2: possibilities += "E"
                    if i == 3: possibilities += "S"
        return possibilities

class Player(object):
    def __init__(self, location):
        self.moved_back = False
        self.location = location

    def set_moved_back(self, boolean):
        self.moved_back = boolean

    def is_moved_back(self):
        return self.moved_back

    def getLoc(self):
        return self.location

    def setLoc(self, location):
        self.location = location

    def move_up(self):
        self.location.setX(self.location.getX() - 1)

    def move_down(self):
        self.location.setX(self.location.getX() + 1)

    def move_left(self):
        self.location.setY(self.location.getY() - 1)

    def move_right(self):
        self.location.setY(self.location.getY() + 1)

    def move(self, direction):
        if string.upper(direction) == 'N':
            self.move_up()
        elif string.upper(direction) == 'W':
            self.move_left()
        elif string.upper(direction) == 'E':
            self.move_right()
        elif string.upper(direction) == 'S':
            self.move_down()
        else: print "invalid input!"

class Game(object):
    def __init__(self, map):
        self.map = map
        self.player = Player(map.start)
        self.track_points = []
        self.path_covered = ''

    def play(self, visible):
        last_dir = ''
        # helper function to move back one tracking point
        def move_back(track_point):
            self.map.update_array(track_point.get_map_snapshot())
            print "track_point loc: " + str(track_point.get_location())
            self.player.setLoc(track_point.get_location())
            print "player new loc: " + str(self.player.getLoc())
            self.path_covered = track_point.get_path_covered()
        i = 0
        while True:
            print "-------------- " + str(i) + " -------------"
            # Get players location
            player_loc = copy.copy(self.player.getLoc())
            print "Player Loc:" + str(player_loc)
            for point in self.track_points:
                print point
            if len(self.track_points) > 0:
                print "Track Point Loc: " + str(self.track_points[-1].get_location())
            if visible == True:
                os.system('clear')
                self.map.show()
                time.sleep(0.1)

            # Check if player got stuck and was moved back to this place ...
            if self.player.is_moved_back() == True:
                # in this case we take the possible directions to go from the TrackingPoint
                possible_ways = self.track_points[-1].get_choices()
            else:
                # otherwise we check the possible ways by looking at the map
                possible_ways = self.map.get_possible_ways(player_loc)

            # Check if player has possibilities to move
            print "Possible ways: " + str(possible_ways)

            if len(possible_ways) > 0:
                # 1.) Only one way to go. use this direction
                if len(possible_ways) == 1:
                    direction = possible_ways
                    if self.player.is_moved_back() == True:
                        print "Player moved back: " + str(self.player.is_moved_back())
                        self.track_points[-1].remove_choices(direction)

                #2.) More than one possible ways to go.
                else:
                    # Take snapshot of location to come back when stuck
                    if self.player.is_moved_back() != True:
                        track_point = TrackingPoint(player_loc, self.path_covered, \
                                                    possible_ways, self.map.snapshot())
                        self.track_points.append(track_point)

                    # check if we can go straight ahead. If yes we take this direction.
                    # if len(last_dir) > 0 and last_dir in possible_ways:
                    #     direction = last_dir
                    if 'S' in possible_ways:
                        direction = 'S'
                    elif 'E' in possible_ways:
                        direction = 'E'
                    elif 'W' in possible_ways:
                        direction = 'W'
                    elif len(last_dir) > 0 and last_dir in possible_ways:
                        direction = last_dir
                    else:
                        direction = possible_ways[0]
                    self.track_points[-1].remove_choices(direction)

                # Move player
                self.player.move(direction)
                # Update the covered path
                self.path_covered += direction
                # Mark the players new location as visited
                self.map.update_field_value(self.player.getLoc(), 'X')
                self.player.set_moved_back(False)

                #Check if player reached the goal
                if str(self.player.getLoc()) == str(self.map.get_goal()):
                    return string.upper(self.path_covered)

                #set last direction to check later if we can go straight ahead
                last_dir = direction
            # Player is trapped, no more possible directions to go
            else:
                print "Move back!"
                # We go back to last tracking point

                print "last Trackpoint: " + str(self.track_points[-1])
                print "track point loc: " + str(self.track_points[-1].get_location())

                move_back(self.track_points[-1])
                possible_ways = self.track_points[-1].get_choices()
                # here we check if there are possibilities to go
                if len(possible_ways) > 0:
                    self.player.set_moved_back(True)
                # if not we move back to tracking point befor last tracking point
                else:
                    self.track_points.pop()
                    if not self.track_points:
                        print "No possible way to the goal. END."
                        return
                    else:
                        move_back(self.track_points[-1])
                        self.player.set_moved_back(True)


            i += 1
            print " -------------------------------------------- "
            # stop = raw_input()



def checkio(map_array):
    map = Map(map_array)
    game = Game(map)
    print game.play(True)
    #print game.play(False)
checkio([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

# checkio([
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

# checkio([
#         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

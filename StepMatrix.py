
def discretize_direction(angle):
    direction = 0
    if angle > 22 and angle < 67:
        direction = 1
    elif angle > 68 and angle < 112:
        direction = 2
    elif angle > 113 and angle < 157:
        direction = 3
    elif angle > 158 and angle < 202:
        direction = 4
    elif angle > 203 and angle < 247:
        direction = 5
    elif angle > 248 and angle < 292:
        direction = 6
    elif angle > 293 and angle < 337:
        direction = 7
    else:
        direction = 0

    return direction

# pseudo algorithm for all the map matching method
class StepMatrix(object): # a 21 x 21 matrix
    def __init__(self, curr_step, refer, prev_step, obs_map):
        self.step_matrix = self.setup_matrix(curr_step, prev_step, obs_map)
        # 8 degrees of freedom - N, NE, E, SE, S, SW, W, NW
        self.dof = self.direction_probability_given_next(refer)

    # a matrix of probability (0 is not possible - 1 is highly probable)
    # assumes user does not go back to previous step
    def setup_matrix(self, step, prev_step, obs_map):
        step_matrix = [[0 for x in range(21)] for y in range(21)]
        # absolute obstacle is 0
        for i in range(21): # row
            for j in range(21): # col
                step_matrix[i][j] = abs(obs_map[step[1]-10+i][step[0]-10+j] - 1.0)

        step_matrix[10 + prev_step[1] - step[1]][10 + prev_step[0] - step[0]] = 0.0
        # step_matrix[10 + next_step[1] - step[1]][10 + next_step[0] - step[0]] = 0.9
        # soft gaussian the probability
        for i in range(21):
            for j in range(21):
                # obstacle
                if step_matrix[i][j] == 0:
                    for net_i in range(max(0,i-5), min(21, i+5)):
                        for net_j in range(max(0, j-5), min(21, j+5)):
                            step_matrix[net_i][net_j] = min(step_matrix[net_i][net_j], 0.5)
        step_matrix[10][10] = 0.0 # irrelevant coz assume user cannot stay
        return step_matrix

    # average likelihood of direction given map and previous step (evidence)
    def direction_probability(self):
        # NORTH
        north = 0
        for col in range(6, 16):
            for row in range(0, 10):
                north = north + self.step_matrix[row][col]
        north = north / 100

        # NORTHEAST
        northeast = 0
        for col in range(11, 21):
            for row in range(0, 10):
                northeast = northeast + self.step_matrix[row][col]
        northeast = northeast / 100

        # EAST
        east = 0
        for col in range(11, 21):
            for row in range(6, 16):
                east = east + self.step_matrix[row][col]
        east = east / 100

        # SOUTHEAST
        southeast = 0
        for col in range(11, 21):
            for row in range(11, 21):
                southeast = southeast + self.step_matrix[row][col]
        southeast = southeast / 100

        # SOUTH
        south = 0
        for col in range(6, 16):
            for row in range(11, 21):
                south = south + self.step_matrix[row][col]
        south = south / 100

        # SOUTHWEST
        southwest = 0
        for col in range(0, 10):
            for row in range(11, 21):
                southwest = southwest + self.step_matrix[row][col]
        southwest = southwest / 100

        # WEST
        west = 0
        for col in range(0, 10):
            for row in range(6, 16):
                west = west + self.step_matrix[row][col]
        west = west / 100

        # NORTHWEST
        northwest = 0
        for col in range(0, 10):
            for row in range(0, 10):
                northwest = northwest + self.step_matrix[row][col]
        northwest = northwest / 100

        return [north, northeast, east, southeast, south, southwest, west, northwest]

    # prob of direction given step
    def direction_probability_given_next(self, refer):
        direction_average = self.direction_probability() #p(dir)
        dr_direction = discretize_direction(refer[0]) #p(step)
        # soft gaussian weight the probable direction but assign 0 for those outside angle scope
        direction_likelihood = [0] * 8
        for i in range(3):
            direction_likelihood[(dr_direction + i) % 8] = 0.9 - (i * 0.4)
            direction_likelihood[(dr_direction - i) % 8] = 0.9 - (i * 0.4)
        for i in range(8):
            direction_average[i]  = direction_average[i] * direction_likelihood[i]
        return direction_average

    def get_next_direction(self):
        return max(range(len(self.dof)), key=lambda x: self.dof[x])

    def print_matrix(self):
        for row in self.step_matrix:
            print row
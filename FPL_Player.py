from colorama import Fore, Style


class Player(object):
    def __init__(self, pid, name, element_type, cost, team, team_name, next_gw, opponent_schedule, ishome_schedule,
                 fpl_expected_points,
                 selected_by, news):
        self.pid = pid
        self.name = name
        self.position = element_type
        self.cost = cost

        self.team = team
        self.team_name = team_name

        self.next_gw = next_gw
        self.opponent_schedule = opponent_schedule
        self.ishome_schedule = ishome_schedule

        self.fpl_expected_points_schedule = []
        self.expected_points_schedule = []
        self.overlord_expected_points_schedule = []

        self.news = news

        self.selected_by = selected_by
        self.fpl_expected_points = fpl_expected_points

    def print_info_basic(self):
        print("Name:", Fore.GREEN, "{:<15}".format(self.name[:15]), Style.RESET_ALL,
              "Team:", Fore.GREEN, "{:<15}".format(self.team_name[:15]), Style.RESET_ALL,
              "Pos:", Fore.GREEN, "{:<2}".format(self.position), Style.RESET_ALL,
              "Cost:", Fore.CYAN, "{:<3}".format(self.cost), Style.RESET_ALL,
              "selected:", Fore.BLUE, "{:<4}".format(self.selected_by), Style.RESET_ALL,
              "expected points:", Fore.YELLOW, "{:<4}".format(self.fpl_expected_points), Style.RESET_ALL,
              Fore.YELLOW, '{0:.2f}'.format(self.fpl_expected_points_schedule[1]),
              Fore.YELLOW, '{0:.2f}'.format(self.fpl_expected_points_schedule[2]),
              Fore.YELLOW, '{0:.2f}'.format(self.fpl_expected_points_schedule[3]),
              Fore.YELLOW, '{0:.2f}'.format(self.fpl_expected_points_schedule[4]), Style.RESET_ALL,
              "news:", Fore.RED, "{:<15}".format(str(self.news)), Style.RESET_ALL,
              )

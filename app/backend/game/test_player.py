import pypokerengine.utils.visualize_utils as U
from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.player import Player  # Import the Player class



class ConsolePlayer(BasePokerPlayer):

    GAME_STATE = ""
    HOLE_CARDS = ""


    def declare_action(self, valid_actions, hole_card, round_state):
        print(U.visualize_declare_action(valid_actions, hole_card, round_state, self.uuid))
        self._print_all_hole_cards(round_state)
        print(1)
        action, amount = self._receive_action_from_console(valid_actions)
        return action, amount

    def receive_game_start_message(self, game_info):
        print(U.visualize_game_start(game_info, self.uuid))
        print(2)
        self._wait_until_input()

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(U.visualize_round_start(round_count, hole_card, seats, self.uuid))
        print(3)
        self._wait_until_input()

    def receive_street_start_message(self, street, round_state):
        print("------------TEST-----------")
        print(self.GAME_STATE)
        print("-------TESTEND-----------")
        print(U.visualize_street_start(street, round_state, self.uuid))
        print(4)
        self._wait_until_input()

    def receive_game_update_message(self, new_action, round_state):
        self.GAME_STATE = U.visualize_game_update(new_action, round_state, self.uuid)
        print(self.GAME_STATE)
        print(5)
        self._wait_until_input()

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))
        print(6)
        self._wait_until_input()

    def _wait_until_input(self):
        input("Enter some key to continue ...")

    # FIXME: This code would be crash if receives invalid input.
    #        So you should add error handling properly.
    def _receive_action_from_console(self, valid_actions):
        action = input("Enter action to declare >> ")

        if action == 'fold': amount = 0
        if action == 'call':  amount = valid_actions[1]['amount']
        if action == 'raise':  amount = int(input("Enter raise amount >> "))
        return action, amount
    
    def _print_all_hole_cards(self, round_state):
        print("Hole cards of all players:")
        for uuid, cards in Player.hole_cards_dict.items():
            name = next((seat['name'] for seat in round_state['seats'] if seat['uuid'] == uuid), "Unknown")
            player_type = "human_player" if "human" in name else "fish_player"
            if player_type == "human_player":
                self.HOLE_CARDS = ' '.join(str(card) for card in cards)
            hole_cards_str = ' '.join(str(card) for card in cards)
            print(self.HOLE_CARDS)
            print(f"Player {name} ({player_type}): {hole_cards_str}")


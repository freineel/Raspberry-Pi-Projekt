import tkinter as tk
from PIL import Image, ImageTk
import random
import os

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")

        self.player_cards = []
        self.dealer_cards = []
        self.card_images = {}
        self.load_card_images()

        self.balance = 100
        self.bet = 0
        self.round_active = False

        self.canvas = tk.Canvas(root, width=800, height=600, bg="green")
        self.canvas.pack()

        self.info_label = tk.Label(root, text="Willkommen bei Blackjack!", font=("Arial", 14), bg="green", fg="white")
        self.info_label.pack(pady=10)

        self.balance_label = tk.Label(root, text=f"Guthaben: {self.balance}€", font=("Arial", 12), bg="green", fg="white")
        self.balance_label.pack(pady=5)

        self.bet_label = tk.Label(root, text="Einsatz: 0€", font=("Arial", 12), bg="green", fg="white")
        self.bet_label.pack(pady=5)

        self.bet_entry = tk.Entry(root)
        self.bet_entry.pack(pady=5)

        self.place_bet_button = tk.Button(root, text="Einsatz setzen", command=self.place_bet)
        self.place_bet_button.pack(pady=5)

        self.player_score_label = tk.Label(root, text="Dein Punktestand: 0", font=("Arial", 12), bg="green", fg="white")
        self.player_score_label.pack(pady=5)

        self.dealer_score_label = tk.Label(root, text="Dealer Punktestand: ?", font=("Arial", 12), bg="green", fg="white")
        self.dealer_score_label.pack(pady=5)

        self.card_button = tk.Button(root, text="Karte ziehen", command=self.draw_card, state=tk.DISABLED)
        self.card_button.pack(pady=10)

        self.stand_button = tk.Button(root, text="Stehen bleiben", command=self.stand, state=tk.DISABLED)
        self.stand_button.pack(pady=5)

        self.result_label = tk.Label(root, text="", font=("Arial", 14), bg="green", fg="white")
        self.result_label.pack(pady=10)

        self.new_game_button = tk.Button(root, text="Neue Runde", command=self.new_game, state=tk.DISABLED)
        self.new_game_button.pack(pady=10)

        self.player_card_y = 400
        self.dealer_card_y = 100
        self.card_start_x = 300
        self.card_offset = 80

    def load_card_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "cards")
        suits = ['clubs', 'diamonds', 'hearts', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

        for suit in suits:
            for value in values:
                card_name = f"{value}_of_{suit}"
                image_path = os.path.join(base_path, f"{card_name}.png")
                image = Image.open(image_path).resize((70, 100))
                self.card_images[card_name] = ImageTk.PhotoImage(image)

        back_image_path = os.path.join(base_path, "back.png")
        back_image = Image.open(back_image_path).resize((70, 100))
        self.card_images["BACK"] = ImageTk.PhotoImage(back_image)

    def place_bet(self):
        try:
            self.bet = int(self.bet_entry.get())
            if self.bet > self.balance or self.bet <= 0:
                self.result_label.config(text="Ungültiger Einsatz!")
                return
            self.balance -= self.bet
            self.balance_label.config(text=f"Guthaben: {self.balance}€")
            self.bet_label.config(text=f"Einsatz: {self.bet}€")
            self.place_bet_button.config(state=tk.DISABLED)
            self.bet_entry.config(state=tk.DISABLED)
            self.card_button.config(state=tk.NORMAL)
            self.stand_button.config(state=tk.NORMAL)
            self.round_active = True
            self.initial_deal()
        except ValueError:
            self.result_label.config(text="Bitte einen gültigen Betrag eingeben.")

    def draw_card_on_table(self, card_name, x, y):
        self.canvas.create_rectangle(x - 2, y - 2, x + 72, y + 102, fill="white", outline="black")
        self.canvas.create_image(x, y, image=self.card_images[card_name], anchor="nw")

    def initial_deal(self):
        self.player_cards = []
        self.dealer_cards = []
        self.canvas.delete("all")
        self.result_label.config(text="")

        player_card1 = self.random_card()
        player_card2 = self.random_card()
        dealer_card = self.random_card()
        dealer_hidden_card = self.random_card()

        self.player_cards.extend([player_card1, player_card2])
        self.dealer_cards.extend([dealer_card, dealer_hidden_card])

        self.draw_card_on_table(player_card1, self.card_start_x, self.player_card_y)
        self.draw_card_on_table(player_card2, self.card_start_x + self.card_offset, self.player_card_y)
        self.draw_card_on_table(dealer_card, self.card_start_x, self.dealer_card_y)
        self.draw_card_on_table("BACK", self.card_start_x + self.card_offset, self.dealer_card_y)

        self.player_score_label.config(text=f"Dein Punktestand: {self.calculate_score(self.player_cards)}")
        self.dealer_score_label.config(text="Dealer Punktestand: ?")

        if self.check_blackjack(self.player_cards):
            self.end_game("Blackjack! Du gewinnst!")
            self.balance += int(self.bet * 2.5)
            self.balance_label.config(text=f"Guthaben: {self.balance}€")

    def check_blackjack(self, cards):
        values = [card.split('_')[0] for card in cards]
        return 'ace' in values and any(v in ['10', 'jack', 'queen', 'king'] for v in values)

    def draw_card(self):
        if not self.round_active:
            return
        card = self.random_card()
        self.player_cards.append(card)
        player_score = self.calculate_score(self.player_cards)
        self.player_score_label.config(text=f"Dein Punktestand: {player_score}")
        self.draw_card_on_table(card, self.card_start_x + len(self.player_cards) * self.card_offset, self.player_card_y)

        if player_score > 21:
            self.end_game("Verloren! Dein Punktestand überschreitet 21.")

    def stand(self):
        if not self.round_active:
            return
        self.canvas.delete("all")
        for i, card in enumerate(self.dealer_cards):
            self.draw_card_on_table(card, self.card_start_x + i * self.card_offset, self.dealer_card_y)

        dealer_score = self.calculate_score(self.dealer_cards)
        while dealer_score < 17:
            card = self.random_card()
            self.dealer_cards.append(card)
            dealer_score = self.calculate_score(self.dealer_cards)
            self.draw_card_on_table(card, self.card_start_x + len(self.dealer_cards) * self.card_offset, self.dealer_card_y)

        self.dealer_score_label.config(text=f"Dealer Punktestand: {dealer_score}")
        player_score = self.calculate_score(self.player_cards)

        if dealer_score > 21 or player_score > dealer_score:
            self.end_game("Gewonnen! Du hast den Dealer besiegt!")
            self.balance += self.bet * 2
        elif player_score == dealer_score:
            self.end_game("Unentschieden!")
            self.balance += self.bet
        else:
            self.end_game("Verloren! Der Dealer hat mehr Punkte.")

        self.balance_label.config(text=f"Guthaben: {self.balance}€")

    def random_card(self):
        suits = ['clubs', 'diamonds', 'hearts', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        return f"{random.choice(values)}_of_{random.choice(suits)}"

    def calculate_score(self, cards):
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                  'jack': 10, 'queen': 10, 'king': 10, 'ace': 11}
        score = sum(values[card.split('_')[0]] for card in cards)
        if score > 21 and 'ace' in [card.split('_')[0] for card in cards]:
            score -= 10
        return score

    def end_game(self, result):
        self.result_label.config(text=result)
        self.card_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.new_game_button.config(state=tk.NORMAL)
        self.place_bet_button.config(state=tk.NORMAL)
        self.bet_entry.config(state=tk.NORMAL)
        self.round_active = False

    def new_game(self):
        if self.round_active:
            return
        self.player_cards = []
        self.dealer_cards = []
        self.bet = 0
        self.bet_label.config(text="Einsatz: 0€")
        self.canvas.delete("all")
        self.result_label.config(text="")
        self.player_score_label.config(text="Dein Punktestand: 0")
        self.dealer_score_label.config(text="Dealer Punktestand: ?")
        self.card_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.new_game_button.config(state=tk.DISABLED)
        self.round_active = False

# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()

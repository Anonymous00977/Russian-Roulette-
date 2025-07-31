import random
import gradio as gr

def play_russian_roulette(player1_name, player2_name, action, game_state=None):
    """Simulates a game of Russian Roulette for two players with actions."""
    if game_state is None:
        players = [player1_name, player2_name]
        random.shuffle(players) # Randomly decide who goes first
        bullet_chamber = random.randint(1, 6)
        current_chamber = 1
        current_player_index = 0
        output = f"Welcome, {players[0]} and {players[1]}! Let's play Russian Roulette.\n"
        game_over = False
        players_status = {player1_name: "alive", player2_name: "alive"}
    else:
        players, bullet_chamber, current_chamber, current_player_index, output, game_over, players_status = game_state

    if game_over:
        return output, (players, bullet_chamber, current_chamber, current_player_index, output, game_over, players_status)

    current_player = players[current_player_index]
    opponent_player = players[1 - current_player_index]

    output += f"\n--- {current_player}'s turn ---\n"
    output += f"Action chosen: {action}\n"

    if action == "Shoot Self":
        output += f"{current_player} bravely points the gun at themselves and pulls the trigger...\n"
        if current_chamber == bullet_chamber:
            output += f"\n💥 BANG! The bullet was in chamber {bullet_chamber}! {current_player} is out!\n"
            players_status[current_player] = "out"
            game_over = True
        else:
            output += f"Click. {current_player} is safe this round. The chamber was {current_chamber}.\n"
            current_chamber += 1
            current_player_index = 1 - current_player_index # Switch player

    elif action == "Shoot Opponent":
        output += f"{current_player} points the gun at {opponent_player} and pulls the trigger...\n"
        if current_chamber == bullet_chamber:
            output += f"\n💥 BANG! The bullet was in chamber {bullet_chamber}! {opponent_player} is out!\n"
            players_status[opponent_player] = "out"
            game_over = True
        else:
            output += f"Click. {opponent_player} is safe this round. The chamber was {current_chamber}.\n"
            current_chamber += 1
            current_player_index = 1 - current_player_index # Switch player

    elif action == "Skip":
        output += f"{current_player} decides to skip their turn, passing the gun to {opponent_player}.\n"
        current_chamber += 1
        current_player_index = 1 - current_player_index # Switch player

    else:
        output += "Invalid action. Please choose Shoot Self, Shoot Opponent, or Skip.\n"

    # Ensure chamber wraps around if it exceeds 6
    if current_chamber > 6:
        current_chamber = 1

    if game_over:
        survivor = [player for player, status in players_status.items() if status == "alive"]
        if survivor:
            output += f"\n--- Game Over ---\n{survivor[0]} wins!\n"
        else:
             output += f"\n--- Game Over ---\nIt's a draw, somehow!\n" # Should not happen in 2 player game

    return output, (players, bullet_chamber, current_chamber, current_player_index, output, game_over, players_status)

# Create the Gradio interface for Russian Roulette
with gr.Blocks() as roulette_iface:
    gr.Markdown("# Russian Roulette")
    game_state = gr.State(None) # Define the state to be managed

    with gr.Row():
        player1_input = gr.Textbox(label="Player 1 Name")
        player2_input = gr.Textbox(label="Player 2 Name")

    play_button = gr.Button("Start Game")
    game_output = gr.Textbox(label="Game Output", lines=15, interactive=False) # Increased lines for more output

    gr.Markdown("## Player Actions")
    with gr.Row():
        action_radio = gr.Radio(["Shoot Self", "Shoot Opponent", "Skip"], label="Choose your action", value="Shoot Self", interactive=False) # Disable until game starts
        action_button = gr.Button("Perform Action", interactive=False) # Disable until game starts


    def start_game(p1_name, p2_name):
        initial_output, initial_state = play_russian_roulette(p1_name, p2_name, action=None) # Pass action=None to initialize
        # Enable action controls after game starts
        return initial_output, initial_state, gr.update(interactive=True), gr.update(interactive=True)

    def perform_action(p1_name, p2_name, action, state):
        updated_output, updated_state = play_russian_roulette(p1_name, p2_name, action, state)
        game_over = updated_state[5]
        if game_over:
             # Disable action controls if game is over
             return updated_output, updated_state, gr.update(interactive=False), gr.update(interactive=False)
        else:
             return updated_output, updated_state, gr.update(interactive=True), gr.update(interactive=True)


    play_button.click(
        start_game,
        inputs=[player1_input, player2_input],
        outputs=[game_output, game_state, action_radio, action_button]
    )

    action_button.click(
        perform_action,
        inputs=[player1_input, player2_input, action_radio, game_state],
        outputs=[game_output, game_state, action_radio, action_button]
    )


roulette_iface.launch(share=True)
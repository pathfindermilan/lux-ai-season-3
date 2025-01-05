import argparse
import os
from datetime import datetime
import subprocess
import json
import time
import re
from typing import Dict, Any

YELLOW = '\033[93m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


def parse_results(output: str) -> Dict[str, Any]:
    lines = output.split('\n')
    result_dict = {}

    for line in lines:
        if line.startswith('Time Elapsed:'):
            result_dict['time'] = float(line.split(': ')[1])
        elif line.startswith('Rewards:'):
            rewards_str = line.split(': ')[1]
            rewards_str = rewards_str.replace('array(', '').replace(', dtype=int32)', '')
            result_dict['rewards'] = eval(rewards_str)
    return result_dict


def determine_winner(rewards: Dict[str, int]) -> str:
    player_0_score = rewards['player_0']
    player_1_score = rewards['player_1']

    if player_0_score > player_1_score: return 'player_0'
    elif player_1_score > player_0_score: return 'player_1'

def print_colored_result(player1_folder: str, player2_folder: str, results: Dict[str, Any]):
    rewards = results['rewards']
    winner = determine_winner(rewards)

    folder_map = {
        'player_0': player1_folder,
        'player_1': player2_folder
    }

    for player, score in rewards.items():
        folder_name = folder_map[player]
        color = YELLOW if player == 'player_0' else BLUE
        result_color = GREEN if player == winner else RED
        status = "WINNER" if player == winner else "LOSER"
        print(f"{color}{folder_name}:{RESET} Score = {score} {result_color}({status}){RESET}")

    print(f"\nTime Elapsed: {results['time']} seconds")

def main():
    parser = argparse.ArgumentParser(description="Run luxai-s3 with custom folder inputs")
    parser.add_argument("--output", help="Output folder for the replay file", default="replays")
    args = parser.parse_args()

    agent1 = input(f"{YELLOW}Enter the first folder containing the main.py:{RESET} ")
    agent2 = input(f"{BLUE}Enter the second folder containing the main.py:{RESET} ")

    if not os.path.exists(agent1) or not os.path.exists(agent2):
        print(f"{RED}One or both of the specified folders do not exist.{RESET}")
        return

    timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    output_filename = f"{agent1}?{agent2}@{timestamp}.json"
    output_path = os.path.join(args.output, output_filename)

    os.makedirs(args.output, exist_ok=True)

    command = [
        "luxai-s3",
        os.path.join(agent1, "main.py"),
        os.path.join(agent2, "main.py"),
        f"--output={output_path}"
    ]

    try:
        start_time = time.time()
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        elapsed_time = time.time() - start_time

        i, j = re.findall(r"\(\d" ,process.stdout)
        i, j = int(i[1]), int(j[1])

        results = {
            'time': elapsed_time,
            'rewards': {'player_0': i, 'player_1': j}
        }

        print_colored_result(agent1, agent2, results)
        print(f"\nReplay saved to: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"{RED}An error occurred while running the command: {e}{RESET}")

if __name__ == "__main__": main()
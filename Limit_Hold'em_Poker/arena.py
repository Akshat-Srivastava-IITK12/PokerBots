import os
import sys
import importlib
import inspect
import itertools
import concurrent.futures
from hulhe_engine import HULHEEngine

def load_all_bots(directory_name="submissions"):
    bots = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_dir, directory_name)
    
    if not os.path.exists(target_directory):
        print(f"[ERROR] Could not find the directory at {target_directory}")
        return bots

    for filename in os.listdir(target_directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{directory_name}.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
            except Exception as e:
                print(f"[DISQUALIFIED] Skipping {filename}: {e}")
                continue 

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, 'get_action') and name != 'HULHEGameState':
                    try:
                        bots.append(obj()) 
                    except Exception as e:
                        print(f"[ERROR] Failed to instantiate {name}: {e}")
    return bots

# 1. ISOLATE THE MATCH LOGIC
# Multiprocessing requires the parallelized function to be defined at the 
# module level so the OS can securely serialize (pickle) the data to other cores.
def play_match(b1, b2, hands_per_match):
    p1_profit, p2_profit = 0.0, 0.0
    for i in range(hands_per_match):
        if i % 2 == 0:
            engine = HULHEEngine(b1, b2)
            res1, res2 = engine.play_hand()
            p1_profit += res1
            p2_profit += res2
        else:
            engine = HULHEEngine(b2, b1)
            res2, res1 = engine.play_hand()
            p2_profit += res2
            p1_profit += res1
            
    # Return the names alongside the profits so the main thread knows who won
    return b1.name, b2.name, p1_profit, p2_profit

def run_round_robin():
    bots = load_all_bots()
    if len(bots) < 2:
        print("[SYSTEM] Need at least 2 valid bots.")
        return

    print(f"[SYSTEM] Loaded {len(bots)} HULHE agents. Commencing PARALLEL Tournament...\n")
    
    leaderboard = {bot.name: 0.0 for bot in bots}
    matches = list(itertools.combinations(bots, 2))
    
    hands_per_match = 10000 
    big_blind_value = 2.0 
    
    total_matches = len(matches)
    completed_matches = 0

    print(f"    [Engine] Distributing {total_matches} matches across CPU cores...")

    # 2. SPAWN THE WORKER POOL
    # ProcessPoolExecutor automatically detects your max CPU cores and spawns 
    # that exact number of isolated Python workers.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Map every match to a future (a promise of an eventual result)
        futures = [
            executor.submit(play_match, b1, b2, hands_per_match) 
            for b1, b2 in matches
        ]
        
        # 3. HARVEST RESULTS ASYNCHRONOUSLY
        # As soon as any CPU core finishes a match, collect it and update the UI
        for future in concurrent.futures.as_completed(futures):
            try:
                b1_name, b2_name, p1_profit, p2_profit = future.result()
                
                # Update the master leaderboard
                leaderboard[b1_name] += p1_profit
                leaderboard[b2_name] += p2_profit
                
                # Update the progress UI safely
                completed_matches += 1
                sys.stdout.write(f"\r    [Engine] Match Progress: [{completed_matches} / {total_matches}] completed")
                sys.stdout.flush()
                
            except Exception as exc:
                print(f"\n[CRITICAL] A match thread crashed: {exc}")

    print("\n\n=====================================================")
    print("      FINAL HULHE LEADERBOARD (Total Net Profit)     ")
    print("=====================================================")
    sorted_board = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    
    for rank, (name, profit) in enumerate(sorted_board, 1):
        total_hands_played = hands_per_match * (len(bots) - 1)
        global_bb_100 = (profit / (total_hands_played * big_blind_value)) * 100
        print(f"{rank}. {name:<25} | {profit:>10} chips | {global_bb_100:>7.2f} BB/100")

# 4. THE WINDOWS MULTIPROCESSING GUARD
# This statement is absolutely mandatory for Windows. It prevents the spawned 
# child processes from recursively importing and executing the main script forever.
if __name__ == "__main__":
    run_round_robin()
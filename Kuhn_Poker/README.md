# Instructions

## Step 1: Fork and Clone

You must use the Fork & Pull Request workflow. Do not push directly to the main repository.

Click Fork in the top right corner of the GitHub repository.

Clone your fork to your local machine by typing in the terminal:

git clone https://github.com/YOUR_USERNAME/PokerBots.git

cd PokerBots

## Step 2: Build Your Bot

Go to the submissions/ folder.

Duplicate mentee_template.py and rename it (e.g., team_alpha.py)

Open your new file and update the class name (e.g., class TeamAlphaBot:).

Write your logic inside the get_action(self, state) method.

Rule: You must return only 'p' (Pass/Fold) or 'b' (Bet/Call).

## Step 3: Test Locally

Ensure your bot works before submitting.

Open arena.py and import your new bot class.

Run the simulation on the terminal:

python arena.py

Step 4: Submit via Pull Request
Once your bot is ready, submit it to the main repository:

Commit and push your code to your fork:

git add submissions/team_alpha.py
git commit -m "Add Team Alpha Bot"
git push origin main

Go to your repository on GitHub and click Contribute -> Open Pull Request.

⚠️ Strict Rules
Do not edit engine.py or arena.py.

Keep code self-contained inside your bot's class.

No external libraries (like pandas or requests) are allowed in get_action to ensure simulation speed. Standard math/random libraries are permitted.

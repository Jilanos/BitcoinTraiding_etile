# BitcoinTraiding
Learn to trade Bitcoins from real data

This project downloads bitcoin value over time, simulate a trading agent and learn to maximize profit using hyper-parameter tuning (Optuna).


# How to run
- $ git clone https://github.com/HoffmannNicolas/BitcoinTraiding.git
- $ cd BitcoinTraiding
- $ python3 -m venv ven
- $ source env/bin/activate
- $ pip install --upgrade pip
- $ pip install -r requirements
- Add apiKeys.py file to project source
- $ python test.py

# To-do
- Uniformalize policy.betToMake arguments (by use of a new "Candle" class ?)
- Organizer Regularizers / Derivators better
- Ensure fees are well taken into account with return values of bets
- Save data in _temp/


import os
import sys
    # Adds higher directory to python modules path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# Import and instanciate a wallet
from wallet import Wallet
wallet = Wallet()
print("Wallet instanciation : OK")
6
# Import and instanciate a policy
from policy import Policy
policy = Policy()
print("Policy instanciation : OK")

# Import and instanciate an agent
from agent import Agent
agent = Agent(wallet, policy)
print("Agent instanciation : OK")

# Import and instanciate a regularizer
from regularizer import Regularizer
regularizer = Regularizer()
print("Regularizer instanciation : OK")

# Import and instanciate bets
from bet import Long, Short
long = Long(42, 1, 10)
short = Short(13, 7, 3)
print("Bet instanciation : OK")



from agent import Agent
from wallet import Wallet
from policy import Policy_01, Policy_02
from bet import Long, Short
from regularizer import Regularizer_AvgStd
from data import Data,loadData
import random


# Test Agent
print("Test Agent")
wallet = Wallet()
policy = Policy_01()
policy.sample()
agent = Agent(wallet, policy)
    # Fake data for testing
import random
initPrice = 100
sequenceLength = 60
prices = [initPrice + 10 * random.random() for _ in range(sequenceLength)]
highests = [price + 3 * random.random() for price in prices]
lowests = [price - 3 * random.random() for price in prices]
    # Simulate the agent agent
for datumNumber, (price, highest, lowest) in enumerate(zip(prices, highests, lowests)) :
    agent.act(price, highest, lowest)

# Test Policy_02
wallet = Wallet()
policy = Policy_02()
policy.sample()
agent = Agent(wallet, policy)
initPrice = 100
sequenceLength = 100
prices = [initPrice + 10 * random.random() for _ in range(sequenceLength)]
highests = [price + 3 * random.random() for price in prices]
lowests = [price - 3 * random.random() for price in prices]
for datumNumber, (price, highest, lowest) in enumerate(zip(prices, highests, lowests)) :
    agent.act(price, highest, lowest)

# Test Bet
print("Test Bet")
long = Long(42, 1, 10)
short = Short(13, 7, 3)
for price in [15, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1] :
    print("Price : ", price)
    print("\tlong : ", long.shouldTerminate(price, price+0.1, price-0.1))
    print("\tshort : ", short.shouldTerminate(price, price+0.1, price-0.1))
    print()
print(long.moneyAmount)
print(short.moneyAmount)

# Test Data
print("Test Data")
paire = "BTCUSDT"
sequenceLength = 1000
interval_value = 1
interval_unit = "m"
interval_str = f"{interval_value}{interval_unit}"
data = loadData(paire=paire, sequenceLength=sequenceLength, interval_str=interval_str, numPartitions=4)
data.plot()

# Test Regularizer
print("Test Regularizer")
import random
regularizer = Regularizer_AvgStd()
printStep = 1
for _ in range(int(1e3)) :
    value = 1000 * random.random()
    regularizedValue = regularizer.regularize(value)
    if _ >= printStep :
        printStep *= 1.3
        print(f"Value {_} : {value}")
        print(f"\t{regularizer}")
        print("\tregularizedValue : ", regularizedValue)

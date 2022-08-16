
from wallet import Wallet
from policy import Policy, Policy_01, Policy_02
from bet import Long, Short

class Agent() :

    """ Manages a wallet according to a policy """

    def __init__(self, wallet : Wallet, policy : Policy, ignoreTimer : int = 50) :
            # Check types and values
        assert isinstance(wallet, Wallet), f"[Type Error] :: <wallet> should be a Wallet (got '{type(wallet)}' instead)."
        assert isinstance(policy, Policy), f"[Type Error] :: <policy> should be a Policy (got '{type(policy)}' instead)."
        assert isinstance(ignoreTimer, (int, float)), f"[Type Error] :: <ignoreTimer> should be an integer of a float (got '{type(ignoreTimer)}' instead)."
        assert ignoreTimer >= 0, f"[Value Error] :: <ignoreTimer> should be >= 0 (got '{ignoreTimer}' instead)."
            # Store values
        self.wallet = wallet
        self.policy = policy
        self.ignoreTimer = ignoreTimer # How many time steps the agent waits before acting
        self.bet = None


    def act(self, indic, price : float, highest : float, lowest : float, volume : float) :
            # <price> is the current price
            # <highest> is the highest price the value had in the interval
            # <lowest> is the lowest price the value had in the interval

            # Check types and values
        assert isinstance(price, (int, float)), f"[Type Error] :: <price> should be an integer or a float (got '{type(price)}' instead)."
        assert price > 0, f"[Value Error] :: <price> should be > 0 (got '{price}' instead)."
        assert isinstance(highest, (int, float)), f"[Type Error] :: <highest> should be an integer or a float (got '{type(highest)}' instead)."
        assert highest > 0, f"[Value Error] :: <highest> should be > 0 (got '{highest}' instead)."
        assert isinstance(lowest, (int, float)), f"[Type Error] :: <lowest> should be an integer or a float (got '{type(lowest)}' instead)."
        assert lowest > 0, f"[Value Error] :: <lowest> should be > 0 (got '{lowest}' instead)."
        assert lowest <= highest, f"[Value Error] :: <lowest> should be <= <highest> (got '{lowest}' and '{highest}' instead)."

            # End current bet
        if self.bet != None :
            shouldEnd,win = self.bet.shouldTerminate(price, highest, lowest)
            if shouldEnd :
                    # End Long bet
                if isinstance(self.bet, Long) :
                    self.wallet.sell(self.wallet.bitcoins, self.bet.sellPrice,"long")
                    self.policy.addTrade(win, self.bet.sellPrice)
                    self.bet = None
                    # End Short bet
                if isinstance(self.bet, Short) :
                    #self.wallet.buy(self.wallet.getMoneyAmountShort(self.bet.moneyAmount, self.bet.buyPrice) self.bet.moneyAmount, self.bet.buyPrice)
                    self.wallet.buy(-self.wallet.bitcoins*self.bet.buyPrice,self.bet.buyPrice,"short")
                    self.policy.addTrade(win, self.bet.buyPrice)
                    self.bet = None


            # Start a new bet
        betToMake, moneyToBet, takeProfit, stopLoss = self.policy.betToMake(price, indic, highest, lowest, volume, self.bet)
        
        if betToMake == "Long" :
            self.wallet.buy(moneyToBet, price,"long")
            self.bet = Long(moneyToBet, price * (1 - stopLoss / 100), price * (1 + takeProfit / 100))
        elif betToMake == "Short" :
            btcToBet = moneyToBet/ price
            self.wallet.sell(btcToBet, price,"short")
            self.bet = Short(btcToBet, price * (1 + stopLoss / 100), price * (1 - takeProfit / 100))



if __name__ == "__main__" :

        # Instanciate an agent
    wallet = Wallet()
    policy = Policy_01()
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
        print(f"[Data {datumNumber}] :: price={price}, highest={highest}, lowest={lowest}")
        agent.act(price, highest, lowest)

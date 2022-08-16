
import abc # Abstract Basic Class

class Bet() :

    """ Encapsulate a Bet made by an agent """

    def __init__(self, moneyAmount, stopLossPrice, takeProfitPrice) :
            # Check type and values
        assert isinstance(moneyAmount, (int, float)), f"[Type Error] :: <moneyAmount> should be an integer or a float (got '{type(moneyAmount)}' instead)."
        assert moneyAmount > 0, f"[Value Error] :: <moneyAmount> should be > 0 (got '{moneyAmount}' instead)."
        assert isinstance(stopLossPrice, (int, float)), f"[Type Error] :: <stopLossPrice> should be an integer of a float (got '{type(stopLossPrice)}' instead)."
        assert stopLossPrice > 0, f"[Value Error] :: <stopLossPrice> should be > 0 (got '{stopLossPrice}' instead)."
        assert isinstance(takeProfitPrice, (int, float)), f"[Type Error] :: <takeProfitPrice> should be an integer or a float (got '{type(takeProfitPrice)}' instead)."
        assert takeProfitPrice > 0, f"[Value Error] :: <takeProfitPrice> should be > 0 (got '{takeProfitPrice}' instead)."
            # Save values
        self.moneyAmount = moneyAmount
        self.stopLossPrice = stopLossPrice
        self.takeProfitPrice = takeProfitPrice

        # All bet must have a terminaison criterion to know when to end the bet
    @abc.abstractmethod
    def shouldTerminate(self, price, highest, lowest) :
        pass



class Long(Bet) :

    """ A bet predicting the price will go up """

    def __init__(self, moneyAmount : float, stopLossPrice : float, takeProfitPrice : float) :
            # Call __init__ of parent class Bet
        super(Long, self).__init__(moneyAmount, stopLossPrice, takeProfitPrice)
            # Field required to end the bet
        assert takeProfitPrice > stopLossPrice, f"[Value Error] :: <takeProfitPrice> should be > <stopLossPrice> (got '{takeProfitPrice}' and '{stopLossPrice}' instead)."
        self.sellPrice = None


    def shouldTerminate(self, price : float, highest : float, lowest : float) :
            # Check types and values
        assert isinstance(price, (int, float)), f"[Type Error] :: <price> should be an integer of a float (got '{type(price)}' instead)."
        assert price > 0, f"[Value Error] :: <price> should be > 0 (got '{price}' instead)."
        assert isinstance(highest, (int, float)), f"[Type Error] :: <highest> should be an integer or a float (got '{type(highest)}' instead)."
        assert highest > 0, f"[Value Error] :: <highest> should be > 0 (got '{highest}' instead)."
        assert isinstance(lowest, (int, float)), f"[Type Error] :: <lowest> should be an integer or a float (got '{type(lowest)}' instead)."
        assert lowest > 0, f"[Value Error] :: <lowest> should be > 0 (got '{lowest}' instead)."
        assert lowest <= highest, f"[Value Error] :: <lowest> should be <= <highest> (got '{lowest}' and '{highest}' instead)."
            # Bet is lost
        if lowest < self.stopLossPrice :
            self.sellPrice = self.stopLossPrice
            return True,False
            # Bet is won
        if highest > self.takeProfitPrice :
            self.sellPrice = self.takeProfitPrice
            return True,True
        # Bet neither won nor lost do not terminate
        return False,False



class Short(Bet) :

    """ A bet predicting the price will go down """

    def __init__(self, moneyAmount : float, stopLossPrice : float, takeProfitPrice : float) :
            # Call __init__ of parent class Bet
        super(Short, self).__init__(moneyAmount, stopLossPrice, takeProfitPrice)
        assert takeProfitPrice < stopLossPrice, f"[Value Error] :: <takeProfitPrice> should be < <stopLossPrice> (got '{takeProfitPrice}' and '{stopLossPrice}' instead)."
            # Field required to end the bet
        self.buyPrice = None


    def shouldTerminate(self, price : float, highest : float, lowest : float) :
            # Check types and values
        assert isinstance(price, (int, float)), f"[Type Error] :: <price> should be an integer of a float (got '{type(price)}' instead)."
        assert price > 0, f"[Value Error] :: <price> should be > 0 (got '{price}' instead)."
        assert isinstance(highest, (int, float)), f"[Type Error] :: <highest> should be an integer or a float (got '{type(highest)}' instead)."
        assert highest > 0, f"[Value Error] :: <highest> should be > 0 (got '{highest}' instead)."
        assert isinstance(lowest, (int, float)), f"[Type Error] :: <lowest> should be an integer or a float (got '{type(lowest)}' instead)."
        assert lowest > 0, f"[Value Error] :: <lowest> should be > 0 (got '{lowest}' instead)."
        assert lowest <= highest, f"[Value Error] :: <lowest> should be <= <highest> (got '{lowest}' and '{highest}' instead)."
            # Bet is lost
        if highest > self.stopLossPrice :
            self.buyPrice = self.stopLossPrice
            return True,False
            # Bet is won
        if lowest < self.takeProfitPrice :
            self.buyPrice = self.takeProfitPrice
            return True,True

        # Bet neither won nor lost do not terminate
        return False,False



if __name__ == "__main__" :
    long = Long(42, 1, 10)
    short = Short(13, 7, 3)
    for price in [15, 13, 9, 8, 7, 6, 5, 4, 3, 2, 1] :
        print("Price : ", price)
        print("\tlong : ", long.shouldTerminate(price, price+0.1, price-0.1))
        print("\tshort : ", short.shouldTerminate(price, price+0.1, price-0.1))
        print()
    print(long.moneyAmount)
    print(short.moneyAmount)

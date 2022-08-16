
class Wallet() :

    """ Encapsulates all current ressources and exchanges of ressources """

    def __init__(self, initMoney : float = 200, initBitcoins : float = 0, fees : float = 5) :
            # Check types and values
        assert isinstance(initMoney, (int, float)), f"[Type Error] :: <initMoney> should be an integer or a float  (got '{type(initMoney)}' instead)."
        assert initMoney >= 0, f"[Value Error] :: <initMoney> should be > 0 (got '{initMoney}' instead)."
        assert isinstance(initBitcoins, (int, float)), f"[Type Error] :: <initBitcoins> should be an integer or a float (got '{type(initBitcoins)}' instead)."
        assert initBitcoins >= 0, f"[Value Error] :: <initBitcoins> should be > 0 (got '{initBitcoins}' instead)."
        assert isinstance(fees, (int, float)), f"[Type Error] :: <fees> should be an integer or a float (got '{type(fees)}' instead)."
        #assert fees > 0, f"[Value Error] :: <fees> should be > 0 (got '{fees}' instead)."
            # Store values
        self.initialMoney = initMoney
        self.money = initMoney
        self.bitcoins = initBitcoins
        self.fees = fees # In percentage
        self.enter = 0
        self.gain =0


    def getBtcAmount(self, moneyAmount : float, price : float) -> float :
        # Compute how many BTC can be bought from <money>, considering <price> and <self.fees>
        return moneyAmount * (1 - self.fees / 100) / price

    def getMoneyAmount(self, btcAmount : float, price : float) -> float :
        return btcAmount * (1 - self.fees / 100) * price
    
    def getMoneyAmountShort(self, btcAmount : float, price : float) -> float :
        return btcAmount / (1 - self.fees / 100) * price
    
    def getBtcAmountShort(self, moneyAmount : float, price : float) -> float :
        # Compute how many BTC can be bought from <money>, considering <price> and <self.fees>
        return moneyAmount * (1 - self.fees / 100) / price
    


    def buy(self, moneyAmount : float, price : float, applyfees : str) :
            # Check types and values
        assert isinstance(moneyAmount, (int, float)), f"[Type Error] :: <moneyAmount> should be an integer or a float (got '{type(moneyAmount)}' instead)."
        assert moneyAmount > 0, f"[Value Error] :: <moneyAmount> should be > 0 (got '{moneyAmount}' instead)."
        assert isinstance(price, (int, float)), f"[Type Error] :: <price> should be an integer or a float (got '{type(price)}' instead)."
        assert price > 0, f"[Value Error] :: <price> should be > 0 (got '{price}' instead)."
            # Make the transaction
        if applyfees=="short":#END
            feesBTC=1
            feesEUR=1+self.fees / 100
            self.gain+=(self.money - moneyAmount*feesEUR)-self.enter
        elif applyfees=="long":#DEBUT
            feesBTC=1-self.fees / 100
            feesEUR=1
            self.enter=self.money
        else:
            feesBTC=1
            feesEUR=1
        self.money -= moneyAmount*feesEUR
        #self.bitcoins += self.getBtcAmount(moneyAmount, price)
        self.bitcoins += moneyAmount/price*feesBTC


    def sell(self, btcAmount : float, price : float, applyfees : str) :
            # Check types and values
        assert isinstance(btcAmount, (int, float)), f"[Type Error] :: <btcAmount> should be an integer or a float (got '{type(btcAmount)}' instead)."
        assert btcAmount > 0, f"[Value Error] :: <btcAmount> should be > 0 (got '{btcAmount}' instead)."
        assert isinstance(price, (int, float)), f"[Type Error] :: <price> should be an integer or a float (got '{type(price)}' instead)."
        assert price > 0, f"[Value Error] :: <price> should be > 0 (got '{price}' instead)."
            # Make the transaction
        if applyfees=="long":#END
            feesBTC=1
            feesEUR=1-self.fees / 100
            self.gain+=(self.money + btcAmount*price*feesEUR)-self.enter
        elif applyfees=="short":#DEBUT
            feesBTC=1
            feesEUR=1-self.fees / 100
            self.enter=self.money
        else:
            feesBTC=1
            feesEUR=1
        self.money += btcAmount*price*feesEUR
        self.bitcoins -= btcAmount*feesBTC


    def totalValue(self, price : float) :
        assert isinstance(price, (int, float)), f"[Type Error] :: <price> should be an integer of a float (got '{type(price)}' instead)."
        assert price > 0, f"[Value Error] :: <price> should be > 0 (got '{price}' instead)."
        return self.money + self.getMoneyAmount(self.bitcoins, price)


    def profit(self, price : float) :
        #return self.totalValue(price) - self.initialMoney
        return self.gain


    def __str__(self) :
        return f"[Wallet] :: {self.money} $ ; {self.bitcoins} bitcoins"



if __name__ == "__main__" :
    fees = 10
    price = 20
    wallet = Wallet(fees=fees)
    print("-----------TEST de FEES----------")
    print("-----------LONG----------")
    print(wallet)
    wallet.buy(200, price,"long")
    print(wallet)
    wallet.sell(wallet.bitcoins, price,"long")
    print(wallet)
    print("-----------SHORT----------")
    wallet = Wallet(fees=fees)
    print(wallet)
    wallet.sell(200/price, price,"short")
    print(wallet)
    wallet.buy(200, price,"short")
    print(wallet)
    
    fees = 0
    price1 = 10
    price2 = 11
    price3 = 9
    wallet = Wallet(fees=fees)
    print("\n-----------TEST de PRIX----------")
    print("-----------LONG----------")
    print(wallet)
    wallet.buy(200, price1,"long")
    print(wallet)
    wallet.sell(wallet.bitcoins, price2,"long")
    print(wallet)
    print("-----------SHORT----------")
    wallet = Wallet(fees=fees)
    print(wallet)
    wallet.sell(200/price1, price1,"short")
    print(wallet)
    print("bitcoins : {}".format(wallet.bitcoins))
    wallet.buy(-wallet.bitcoins*price3, price3,"short")
    print(wallet)
    
    fees = 0.018
    price1 = 44601
    price2 = 45047
    price3 = 48397
    price4 = 47913.03
    wallet = Wallet(fees=fees)
    print("\n-----------TEST REEEELS----------")
    print("-----------LONG----------")
    print(wallet)
    wallet.buy(100, price1,"long")
    print(wallet)
    wallet.sell(wallet.bitcoins, price2,"long")
    print(wallet)
    wallet.sell(100/price3, price3,"short")
    print(wallet)
    print("bitcoins : {}".format(wallet.bitcoins))
    wallet.buy(-wallet.bitcoins*price4, price4,"short")
    print(wallet)
# =============================================================================
# 
#     print("---------------------")
#     wallet = Wallet(fees=fees)
#     print(wallet)
#     wallet.sell(10, price)
#     print(wallet)
#     wallet.buy(wallet.getMoneyAmountShort(10, price), price)
#     print(wallet)
# =============================================================================

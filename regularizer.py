

import abc # Abstract Basic Class


class Regularizer() :

    """ Regularize a signal """

    value = None

    @abc.abstractmethod
    def regularize(self, value : float) :
        pass

    def __call__(self, value : float) :
        return self.regularize(value)



class Regularizer_EMA(Regularizer) :

    """ Exponential Moving Average as defined here : https://www.investopedia.com/terms/e/ema.asp """

    def __init__(self, period : float = 10, smoothing : float = 2) :
            # Check type and value
        assert isinstance(period, (int, float)), f"[Type Error] :: <period> should be a float or an integer (got '{type(period)}' instead)."
        assert period >= 0, f"[Value Error] :: <period> should be >= 0 (got '{period}' instead)."
        assert isinstance(smoothing, (int, float)), f"[Type Error] :: <smoothing> should be a float or an integer (got '{type(smoothing)}' instead)."
        assert smoothing >= 0, f"[Value Error] :: <smoothing> should be >= 0 (got '{smoothing}' instead)."
            # Store values
        self.period = period
        self.smoothing = smoothing
        self.value = None

    def regularize(self, newValue : float) :
        if self.value is None :
            self.value = newValue
        else :
            proportion = self.smoothing / (1 + self.period)
            self.value = newValue * proportion + self.value * (1 - proportion)
        return self.value

    def __str__(self) :
        return f"[Regularizer_EMA] :: period={self.period} :: smoothing={self.smoothing} :: value={self.value}"


class Regularizer_AvgStd(Regularizer) :

    """ Regularise a value stream using average and standart deviation """

    def __init__(self, theta : float = 0.99) :
            # Check type and value
        assert isinstance(theta, (int, float)), f"[Type Error] :: <theta> should be a float or an integer (got '{type(theta)}' instead)."
        assert theta >= 0, f"[Value Error] :: <theta> should be >= 0 (got '{theta}' instead)."
        assert theta <= 1, f"[Value Error] :: <theta> should be <= 1 (got '{theta}' instead)."
            # Store values
        self.theta = theta
        self.estimatedAverage = None
        self.estimatedStd = None # Average distance to average

    def regularize(self, value : float) :
            # Update estimated average
        if self.estimatedAverage is None :
            self.estimatedAverage = value
        else :
            self.estimatedAverage = self.theta * self.estimatedAverage + (1 - self.theta) * value

            # Update estimated std
        currentStd = abs(value - self.estimatedAverage)
        if self.estimatedStd is None :
            self.estimatedStd = currentStd
        else :
            self.estimatedStd = self.theta * self.estimatedStd + (1 - self.theta) * currentStd

            # Regularize value
        if (self.estimatedStd == 0) :
            return 0
        else :
            return (value - self.estimatedAverage) / self.estimatedStd

    def __str__(self) :
        return f"[Regularizer_AvgStd] :: Avg={self.estimatedAverage} :: Std={self.estimatedStd}"



class Derivator() :

    """ Derivate a value stream """

    def __init__(self) :
        self.previousValue = None
        self.derivative = None


    def derivate(self, value : float) :
        if self.previousValue is None :
            self.derivative = 1
        else :
            self.derivative = value - self.previousValue
        self.previousValue = value
        return self.derivative


    def __str__(self) :
        return f"[Derivator] :: PreviousValue={self.previousValue} :: Derivative={self.derivative}"


    def __call__(self, value : float) :
        return self.derivate(value)


if __name__ == "__main__" :
        # Run tests
    import random
    regularizer_AvgStd = Regularizer_AvgStd()
    regularizer_EMA = Regularizer_EMA()
    derivator = Derivator()
    printStep = 1
    for _ in range(int(1e9)) :
        value = 1000 * random.random()
        regularizedValue_AvgStd = regularizer_AvgStd.regularize(value)
        regularizedValue_EMA = regularizer_EMA(value)
        derivative = derivator(value)
        if _ >= printStep :
            printStep *= 1.3
            print(f"Value {_} : {value}")
            print(f"\t{regularizer_AvgStd}")
            print("\tregularizedValue_AvgStd : ", regularizedValue_AvgStd)
            print(f"\t{regularizer_EMA}")
            print("\tregularizedValue_EMA : ", regularizedValue_EMA)
            print("\tderivative : ", derivative)

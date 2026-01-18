"""
रुपैयाँको यात्रा - Financial Calculations Module
All financial formulas in one place
"""


class InflationCalculator:
    """Calculate purchasing power loss due to inflation"""
    
    def __init__(self, initial_amount, inflation_rate, years):
        self.initial = initial_amount
        self.rate = inflation_rate
        self.years = years
        self.data = self._calculate()
    
    def _calculate(self):
        """Calculate year-by-year purchasing power"""
        result = []
        for year in range(self.years + 1):
            pp = self.initial / ((1 + self.rate) ** year)
            result.append({
                'year': year,
                'value': pp,
                'scale': pp / self.initial
            })
        return result
    
    def get_value(self, time):
        """Get value at any time (with interpolation)"""
        if time <= 0:
            return self.data[0]
        if time >= self.years:
            return self.data[-1]
        
        # Calculate exact value for smooth animation
        value = self.initial / ((1 + self.rate) ** time)
        return {
            'year': time,
            'value': value,
            'scale': value / self.initial
        }


class CompoundCalculator:
    """Calculate compound interest growth"""
    
    def __init__(self, principal, rate, years, frequency=12):
        self.principal = principal
        self.rate = rate
        self.years = years
        self.freq = frequency
        self.data = self._calculate()
    
    def _calculate(self):
        """Calculate year-by-year growth"""
        result = []
        for year in range(self.years + 1):
            amount = self.principal * ((1 + self.rate/self.freq) ** (self.freq * year))
            result.append({
                'year': year,
                'value': amount,
                'scale': amount / self.principal
            })
        return result
    
    def get_value(self, time):
        """Get value at any time (with interpolation)"""
        if time <= 0:
            return self.data[0]
        if time >= self.years:
            return self.data[-1]
        
        # Calculate exact value
        amount = self.principal * ((1 + self.rate/self.freq) ** (self.freq * time))
        return {
            'year': time,
            'value': amount,
            'scale': amount / self.principal
        }


class RealReturnCalculator:
    """Calculate inflation-adjusted returns"""
    
    def __init__(self, principal, interest_rate, inflation_rate, years, frequency=12):
        self.principal = principal
        self.interest = interest_rate
        self.inflation = inflation_rate
        self.years = years
        self.freq = frequency
        self.compound = CompoundCalculator(principal, interest_rate, years, frequency)
        self.data = self._calculate()
    
    def _calculate(self):
        """Calculate real vs nominal values"""
        result = []
        for year in range(self.years + 1):
            nominal = self.compound.data[year]['value']
            real = nominal / ((1 + self.inflation) ** year)
            result.append({
                'year': year,
                'nominal': nominal,
                'real': real,
                'nominal_scale': nominal / self.principal,
                'real_scale': real / self.principal
            })
        return result
    
    def get_value(self, time):
        """Get value at any time"""
        if time <= 0:
            return self.data[0]
        if time >= self.years:
            return self.data[-1]
        
        nominal_data = self.compound.get_value(time)
        nominal = nominal_data['value']
        real = nominal / ((1 + self.inflation) ** time)
        
        return {
            'year': time,
            'nominal': nominal,
            'real': real,
            'nominal_scale': nominal / self.principal,
            'real_scale': real / self.principal
        }


# Easing functions for smooth animations
def ease_cubic(t):
    """Smooth cubic easing"""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def lerp(start, end, t):
    """Linear interpolation"""
    return start + (end - start) * t

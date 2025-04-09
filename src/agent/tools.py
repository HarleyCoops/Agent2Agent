"""
Tools for the LangGraph agent.
"""

import json
import random
from typing import Dict, Any, Optional
import requests
from datetime import datetime


class CurrencyConverter:
    """A tool for converting between currencies."""
    
    def __init__(self):
        # For demo purposes, we'll use a simple dictionary of exchange rates
        # In a real application, you would use an API like Open Exchange Rates
        self.exchange_rates = {
            "USD": {
                "EUR": 0.92,
                "GBP": 0.77,
                "JPY": 151.72,
                "CAD": 1.35,
                "AUD": 1.48,
                "CHF": 0.89,
                "CNY": 7.23,
                "INR": 83.45,
                "BRL": 5.05,
                "ZAR": 18.32
            }
        }
        
        # Generate exchange rates for all currency pairs
        self._generate_all_rates()
    
    def _generate_all_rates(self):
        """Generate exchange rates for all currency pairs."""
        currencies = list(self.exchange_rates.keys()) + list(self.exchange_rates["USD"].keys())
        currencies = list(set(currencies))  # Remove duplicates
        
        for base in currencies:
            if base not in self.exchange_rates:
                self.exchange_rates[base] = {}
            
            # If we have USD rates, use them to calculate other rates
            if base != "USD" and "USD" not in self.exchange_rates[base]:
                usd_rate = 1 / self.exchange_rates["USD"][base]
                self.exchange_rates[base]["USD"] = usd_rate
            
            for target in currencies:
                if base != target and target not in self.exchange_rates[base]:
                    # Calculate cross rate via USD
                    if base == "USD":
                        rate = self.exchange_rates["USD"][target]
                    elif target == "USD":
                        rate = self.exchange_rates[base]["USD"]
                    else:
                        base_to_usd = self.exchange_rates[base]["USD"]
                        usd_to_target = self.exchange_rates["USD"][target]
                        rate = base_to_usd * usd_to_target
                    
                    self.exchange_rates[base][target] = rate
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Convert an amount from one currency to another.
        
        Args:
            amount: The amount to convert
            from_currency: The source currency code (e.g., "USD")
            to_currency: The target currency code (e.g., "EUR")
            
        Returns:
            A dictionary with the conversion result
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in self.exchange_rates:
            return {
                "success": False,
                "error": f"Currency {from_currency} not supported"
            }
        
        if to_currency not in self.exchange_rates[from_currency]:
            return {
                "success": False,
                "error": f"Currency {to_currency} not supported"
            }
        
        rate = self.exchange_rates[from_currency][to_currency]
        converted_amount = amount * rate
        
        return {
            "success": True,
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "rate": rate,
            "result": converted_amount,
            "timestamp": datetime.now().isoformat()
        }


class WeatherService:
    """A tool for getting weather information."""
    
    def __init__(self):
        # For demo purposes, we'll generate random weather data
        # In a real application, you would use an API like OpenWeatherMap
        self.conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorm", "Snowy", "Foggy", "Windy"]
    
    def get_weather(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weather information for a location.
        
        Args:
            location: The location to get weather for
            date: The date to get weather for (optional, defaults to today)
            
        Returns:
            A dictionary with weather information
        """
        # Generate random weather data
        temperature = round(random.uniform(0, 35), 1)
        condition = random.choice(self.conditions)
        humidity = random.randint(30, 90)
        wind_speed = round(random.uniform(0, 30), 1)
        
        return {
            "success": True,
            "location": location,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "timestamp": datetime.now().isoformat()
        }


# Initialize tools
currency_converter = CurrencyConverter()
weather_service = WeatherService()


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount from one currency to another.
    
    Args:
        amount: The amount to convert
        from_currency: The source currency code (e.g., "USD")
        to_currency: The target currency code (e.g., "EUR")
        
    Returns:
        A string with the conversion result
    """
    result = currency_converter.convert(amount, from_currency, to_currency)
    
    if result["success"]:
        return (
            f"Based on the current exchange rate, {amount} {from_currency} "
            f"is equivalent to {result['result']:.2f} {to_currency}. "
            f"The exchange rate is 1 {from_currency} = {result['rate']:.5f} {to_currency}."
        )
    else:
        return f"Error: {result['error']}"


def get_weather(location: str, date: Optional[str] = None) -> str:
    """
    Get weather information for a location.
    
    Args:
        location: The location to get weather for
        date: The date to get weather for (optional, defaults to today)
        
    Returns:
        A string with weather information
    """
    result = weather_service.get_weather(location, date)
    
    if result["success"]:
        return (
            f"Weather for {result['location']} on {result['date']}: "
            f"{result['condition']} with a temperature of {result['temperature']}°C, "
            f"humidity of {result['humidity']}%, and wind speed of {result['wind_speed']} km/h."
        )
    else:
        return f"Error: {result['error']}"

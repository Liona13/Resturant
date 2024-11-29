class PriceCalculator:
    @staticmethod
    def calculate_menu_price(total_cost, target_margin):
        """
        Calculate the recommended menu price based on cost and desired profit margin
        
        Args:
            total_cost (float): Total cost of ingredients and overhead
            target_margin (float): Desired profit margin percentage (e.g., 30 for 30%)
            
        Returns:
            float: Recommended menu price
        """
        if target_margin >= 100:
            raise ValueError("Profit margin must be less than 100%")
        
        if target_margin <= 0:
            raise ValueError("Profit margin must be greater than 0%")
            
        markup_factor = 1 / (1 - (target_margin / 100))
        return round(total_cost * markup_factor, 2)
    
    @staticmethod
    def calculate_profit_margin(price, cost):
        """
        Calculate the profit margin percentage for a given price and cost
        
        Args:
            price (float): Selling price
            cost (float): Total cost
            
        Returns:
            float: Profit margin percentage
        """
        if price <= 0:
            raise ValueError("Price must be greater than 0")
        
        if cost <= 0:
            raise ValueError("Cost must be greater than 0")
            
        margin = ((price - cost) / price) * 100
        return round(margin, 2)
    
    @staticmethod
    def calculate_total_cost(ingredients):
        """
        Calculate the total cost of a menu item based on its ingredients
        
        Args:
            ingredients (list): List of dictionaries containing ingredient costs and quantities
            
        Returns:
            float: Total cost of ingredients
        """
        total_cost = 0
        for ingredient in ingredients:
            cost_per_unit = ingredient.get('cost_per_unit', 0)
            quantity = ingredient.get('quantity', 0)
            total_cost += cost_per_unit * quantity
            
        return round(total_cost, 2)

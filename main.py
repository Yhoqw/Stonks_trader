import pygame
import random
import math
import time
from datetime import datetime, timedelta
import json
import os
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60
INITIAL_CASH = 10000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

class Stock:
    def __init__(self, symbol, name, initial_price):
        self.symbol = symbol
        self.name = name
        self.price = initial_price
        self.price_history = [initial_price]
        self.timestamps = [datetime.now()]
        self.last_update = time.time()
        self.volatility = random.uniform(0.5, 2.0)
        self.trend = random.choice([-1, 0, 1])
        self.trend_strength = random.uniform(0.1, 0.3)
        
    def update_price(self):
        current_time = time.time()
        if current_time - self.last_update >= 1.0:  # Update every second
            # Random walk with trend
            change_percent = random.gauss(0, self.volatility / 100)
            trend_influence = self.trend * self.trend_strength / 100
            change_percent += trend_influence
            
            new_price = self.price * (1 + change_percent)
            new_price = max(0.01, new_price)  # Prevent negative prices
            
            self.price = round(new_price, 2)
            self.price_history.append(self.price)
            self.timestamps.append(datetime.now())
            
            # Keep only last 300 price points for performance
            if len(self.price_history) > 300:
                self.price_history.pop(0)
                self.timestamps.pop(0)
            
            # Occasionally change trend
            if random.random() < 0.05:  # 5% chance per update
                self.trend = random.choice([-1, 0, 1])
                self.trend_strength = random.uniform(0.1, 0.3)
            
            self.last_update = current_time

class Portfolio:
    def __init__(self, initial_cash=INITIAL_CASH):
        self.cash = initial_cash
        self.holdings = {}  # {symbol: quantity}
        self.transaction_history = []
        
    def buy_stock(self, stock, quantity):
        total_cost = stock.price * quantity
        if self.cash >= total_cost:
            self.cash -= total_cost
            if stock.symbol in self.holdings:
                self.holdings[stock.symbol] += quantity
            else:
                self.holdings[stock.symbol] = quantity
            
            self.transaction_history.append({
                'type': 'BUY',
                'symbol': stock.symbol,
                'quantity': quantity,
                'price': stock.price,
                'timestamp': datetime.now()
            })
            return True
        return False
    
    def sell_stock(self, stock, quantity):
        if stock.symbol in self.holdings and self.holdings[stock.symbol] >= quantity:
            self.cash += stock.price * quantity
            self.holdings[stock.symbol] -= quantity
            
            if self.holdings[stock.symbol] == 0:
                del self.holdings[stock.symbol]
            
            self.transaction_history.append({
                'type': 'SELL',
                'symbol': stock.symbol,
                'quantity': quantity,
                'price': stock.price,
                'timestamp': datetime.now()
            })
            return True
        return False
    
    def get_portfolio_value(self, stocks):
        total_value = self.cash
        for symbol, quantity in self.holdings.items():
            for stock in stocks:
                if stock.symbol == symbol:
                    total_value += stock.price * quantity
                    break
        return total_value

class GraphRenderer:
    def __init__(self, width=700, height=400):
        
        self.width = width
        self.height = height
        self.dpi = 100
        self.fig = Figure(figsize=(width/self.dpi, height/self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        
        # Set matplotlib style
        plt.style.use('default')
        self.fig.patch.set_facecolor('white')
        
    def render_stock_chart(self, stock):
        self.ax.clear()
        
        if len(stock.price_history) < 2:
            self.ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', 
                        transform=self.ax.transAxes, fontsize=12)
            return self.fig_to_surface()
        
        # Prepare data
        prices = np.array(stock.price_history)
        timestamps = stock.timestamps
        
        # Create the main price line
        self.ax.plot(timestamps, prices, 'b-', linewidth=2, label='Price')
        
        # Add moving average if we have enough data
        if len(prices) >= 20:
            ma_20 = np.convolve(prices, np.ones(20)/20, mode='valid')
            ma_timestamps = timestamps[19:]  # Skip first 19 points
            self.ax.plot(ma_timestamps, ma_20, 'r--', linewidth=1, alpha=0.7, label='20-period MA')
        
        # Color the area under the curve
        self.ax.fill_between(timestamps, prices, alpha=0.3, color='lightblue')
        
        # Formatting
        self.ax.set_title(f'{stock.symbol} - {stock.name}', fontsize=14, fontweight='bold')
        self.ax.set_ylabel('Price ($)', fontsize=12)
        self.ax.set_xlabel('Time', fontsize=12)
        
        # Format x-axis to show time nicely
        if len(timestamps) > 0:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            self.ax.xaxis.set_major_locator(mdates.SecondLocator(interval=30))
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add grid
        self.ax.grid(True, alpha=0.3)
        
        # Add current price annotation
        if len(prices) > 0:
            current_price = prices[-1]
            current_time = timestamps[-1]
            self.ax.annotate(f'${current_price:.2f}', 
                           xy=(current_time, current_price),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # Add price change indicator
        if len(prices) > 1:
            change = prices[-1] - prices[-2]
            change_percent = (change / prices[-2]) * 100
            change_text = f'Change: {change:+.2f} ({change_percent:+.1f}%)'
            change_color = 'green' if change >= 0 else 'red'
            self.ax.text(0.02, 0.98, change_text, transform=self.ax.transAxes, 
                        fontsize=10, verticalalignment='top', color=change_color,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Add legend
        self.ax.legend(loc='upper right')
        
        # Tight layout
        self.fig.tight_layout()
        
        return self.fig_to_surface()
    
    def fig_to_surface(self):
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        return pygame.image.fromstring(raw_data, size, 'RGB')

class StockTradingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        pygame.display.set_caption("Stock Trading Game - Enhanced with Matplotlib")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 32)
        
        # Initialize sound
        pygame.mixer.init()
        try:
            self.sounds = {
                'click': pygame.mixer.Sound('click3.wav')
            }
        except pygame.error as e:
            print(f"Couldn't load sound files: {e}. Game will run without sound.")
            # Create a dummy sound class that does nothing so the game doesn't crash
            class DummySound:
                def play(self): pass
            self.sounds = {key: DummySound() for key in ['click']}
        
        #Background Music
        try:
            pygame.mixer.music.load('BossMain.wav')
            pygame.mixer.music.set_volume(0.4) # Adjust volume (0.0 to 1.0)
            pygame.mixer.music.play(loops=-1) # Loop indefinitely
        except pygame.error as e:
            print(f"Couldn't load background music 'sounds/BossMain.wav': {e}")

        # Initialize stocks
        self.stocks = [
            Stock("AAPL", "Apple Inc.", 150.00),
            Stock("GOOGL", "Alphabet Inc.", 2500.00),
            Stock("MSFT", "Microsoft Corp.", 300.00),
            Stock("TSLA", "Tesla Inc.", 800.00),
            Stock("AMZN", "Amazon.com Inc.", 3200.00),
            Stock("META", "Meta Platforms", 320.00),
            Stock("NVDA", "NVIDIA Corp.", 450.00),
            Stock("NFLX", "Netflix Inc.", 400.00)
        ]
        
        self.portfolio = Portfolio()
        self.selected_stock = 0
        self.quantity_input = ""
        self.input_active = False
        self.transaction_mode = "BUY"  # BUY or SELL
        
        # Graph renderer
        self.graph_renderer = GraphRenderer(700, 400)
        self.graph_surface = None
        self.last_graph_update = 0
        
        # UI elements
        self.buttons = {
            'buy': pygame.Rect(50, 750, 80, 40),
            'sell': pygame.Rect(140, 750, 80, 40),
        }
        
        self.quantity_input_rect = pygame.Rect(50, 800, 200, 30)
        
        # Graph area
        self.graph_area = pygame.Rect(450, 50, 700, 400)

        # Message system
        self.message = ""
        self.message_timer = 0
        self.MESSAGE_DURATION = 3 # seconds
        
    def draw_stock_list(self):
        # Stock list background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (20, 50, 400, 650))
        pygame.draw.rect(self.screen, BLACK, (20, 50, 400, 650), 2)
        
        title = self.large_font.render("STOCK MARKET", True, BLACK)
        self.screen.blit(title, (30, 60))
        
        # Column headers
        headers = ["Symbol", "Price", "Change", "Holdings"]
        header_x = [30, 140, 250, 330]
        for i, header in enumerate(headers):
            text = self.font.render(header, True, BLACK)
            self.screen.blit(text, (header_x[i], 100))
        
        # Stock entries
        for i, stock in enumerate(self.stocks):
            y = 130 + i * 65
            
            # Highlight selected stock
            if i == self.selected_stock:
                pygame.draw.rect(self.screen, YELLOW, (25, y-5, 390, 60))
            
            # Stock symbol
            symbol_text = self.font.render(stock.symbol, True, BLACK)
            self.screen.blit(symbol_text, (30, y))
            
            # Stock name
            name_text = self.small_font.render(stock.name[:20], True, DARK_GRAY)
            self.screen.blit(name_text, (30, y + 25))
            
            # Current price
            price_text = self.font.render(f"${stock.price:.2f}", True, BLACK)
            self.screen.blit(price_text, (140, y))
            
            # Price change
            if len(stock.price_history) > 1:
                change = stock.price - stock.price_history[-2]
                change_percent = (change / stock.price_history[-2]) * 100
                change_color = GREEN if change >= 0 else RED
                change_text = f"{change:+.2f}"
                change_percent_text = f"({change_percent:+.1f}%)"
                
                change_surface = self.small_font.render(change_text, True, change_color)
                self.screen.blit(change_surface, (250, y + 5))
                
                percent_surface = self.small_font.render(change_percent_text, True, change_color)
                self.screen.blit(percent_surface, (250, y + 20))
            
            # Holdings
            holdings = self.portfolio.holdings.get(stock.symbol, 0)
            if holdings > 0:
                holdings_text = self.font.render(str(holdings), True, BLUE)
                self.screen.blit(holdings_text, (330, y))
                
                # Holdings value
                value = holdings * stock.price
                value_text = self.small_font.render(f"${value:.0f}", True, BLUE)
                self.screen.blit(value_text, (330, y + 20))
    
    def draw_graph(self):
        # Update graph every 2 seconds to avoid performance issues
        current_time = time.time()
        if current_time - self.last_graph_update >= 2.0 or self.graph_surface is None:
            stock = self.stocks[self.selected_stock]
            self.graph_surface = self.graph_renderer.render_stock_chart(stock)
            self.last_graph_update = current_time
        
        # Draw the graph
        if self.graph_surface:
            self.screen.blit(self.graph_surface, (self.graph_area.x, self.graph_area.y))
        pygame.draw.rect(self.screen, BLACK, self.graph_area, 2)    # Draw graph border
    
    def draw_portfolio_info(self):
        # Portfolio background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (450, 480, 700, 180))
        pygame.draw.rect(self.screen, BLACK, (450, 480, 700, 180), 2)
        
        # Portfolio title
        title = self.large_font.render("PORTFOLIO SUMMARY", True, BLACK)
        self.screen.blit(title, (460, 490))
        
        # Cash
        cash_text = self.font.render(f"Cash Available: ${self.portfolio.cash:,.2f}", True, BLACK)
        self.screen.blit(cash_text, (460, 530))
        
        # Total portfolio value
        total_value = self.portfolio.get_portfolio_value(self.stocks)
        total_text = self.font.render(f"Total Portfolio Value: ${total_value:,.2f}", True, BLACK)
        self.screen.blit(total_text, (460, 560))
        
        # Profit/Loss
        profit_loss = total_value - INITIAL_CASH 
        profit_color = GREEN if profit_loss >= 0 else RED
        profit_text = self.font.render(f"Profit/Loss: ${profit_loss:+,.2f}", True, profit_color)
        self.screen.blit(profit_text, (460, 590))
        
        # Return percentage
        return_percent = (profit_loss / INITIAL_CASH) * 100
        return_text = self.font.render(f"Return: {return_percent:+.1f}%", True, profit_color)
        self.screen.blit(return_text, (460, 620))
        
        # Holdings summary
        holdings_x = 750
        holdings_y = 530
        holdings_title = self.font.render("Current Holdings:", True, BLACK)
        self.screen.blit(holdings_title, (holdings_x, 500))
        
        if not self.portfolio.holdings:
            no_holdings_text = self.small_font.render("No holdings", True, GRAY)
            self.screen.blit(no_holdings_text, (holdings_x, holdings_y))
        else:
            row = 0
            for symbol, quantity in self.portfolio.holdings.items():
                if row >= 5:  # Limit display to 5 rows
                    break
                for stock in self.stocks:
                    if stock.symbol == symbol:
                        value = quantity * stock.price
                        holding_text = f"{symbol}: {quantity} shares"
                        value_text = f"Value: ${value:,.0f}"
                        
                        holding_surface = self.small_font.render(holding_text, True, BLACK)
                        value_surface = self.small_font.render(value_text, True, BLUE)
                        
                        self.screen.blit(holding_surface, (holdings_x, holdings_y + row * 25))
                        self.screen.blit(value_surface, (holdings_x, holdings_y + row * 25 + 12))
                        break
                row += 1
    
    def draw_trading_interface(self):
        # Trading interface background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (20, 720, 400, 150))
        pygame.draw.rect(self.screen, BLACK, (20, 720, 400, 150), 2)
        
        # Selected stock info
        stock = self.stocks[self.selected_stock]
        stock_info = f"Trading: {stock.symbol} @ ${stock.price:.2f}"
        info_surface = self.font.render(stock_info, True, BLACK)
        self.screen.blit(info_surface, (30, 730))
        
        # Transaction cost calculation
        if self.quantity_input and self.quantity_input.isdigit():
            quantity = int(self.quantity_input)
            cost = quantity * stock.price
            cost_text = f"Total Cost: ${cost:,.2f}"
            cost_surface = self.small_font.render(cost_text, True, BLACK)
            self.screen.blit(cost_surface, (250, 730))
        
        # Buttons
        for button_name, rect in self.buttons.items():
            color = GRAY
            if button_name == self.transaction_mode.lower():
                color = GREEN if button_name == 'buy' else RED
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            text = self.font.render(button_name.upper(), True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Quantity input
        input_color = WHITE if self.input_active else LIGHT_GRAY
        pygame.draw.rect(self.screen, input_color, self.quantity_input_rect)
        pygame.draw.rect(self.screen, BLACK, self.quantity_input_rect, 2)
        
        input_label = self.small_font.render("", True, BLACK)
        self.screen.blit(input_label, (self.quantity_input_rect.x, self.quantity_input_rect.y - 50))
        
        # Input text
        input_text = self.font.render(self.quantity_input, True, BLACK)
        self.screen.blit(input_text, (self.quantity_input_rect.x + 5, self.quantity_input_rect.y + 5))
        
        # Cursor
        if self.input_active:
            cursor_x = self.quantity_input_rect.x + 5 + input_text.get_width()
            pygame.draw.line(self.screen, BLACK, 
                           (cursor_x, self.quantity_input_rect.y + 5),
                           (cursor_x, self.quantity_input_rect.y + 20), 2)

    def set_message(self, text, color=BLACK):
        self.message = text
        self.message_color = color
        self.message_timer = time.time() + self.MESSAGE_DURATION

    def display_message(self):
        if self.message and time.time() < self.message_timer:
            message_surface = self.large_font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            # Add a background rectangle for better visibility
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, LIGHT_GRAY, bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, bg_rect, 2, border_radius=5)
            self.screen.blit(message_surface, message_rect)
        else:
            self.message = "" # Clear message if time is up
            self.message_timer = 0
    
    def handle_click(self, pos):
        # Check stock selection
        for i in range(len(self.stocks)):
            stock_rect = pygame.Rect(25, 125 + i * 65, 390, 60)
            if stock_rect.collidepoint(pos):
                if self.selected_stock != i:
                    self.sounds['click'].play()
                    self.selected_stock = i
                    # Force graph update when stock changes
                    self.graph_surface = None
                    self.set_message(f"Selected {self.stocks[self.selected_stock].symbol}", BLUE)
                return
        
        # Check button clicks
        for button_name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                self.sounds['click'].play()
                if button_name == 'buy':
                    self.transaction_mode = 'BUY'
                    self.set_message("Ready to BUY", GREEN)
                elif button_name == 'sell':
                    self.transaction_mode = 'SELL'
                    self.set_message("Ready to SELL", RED)
                return
        
        # Check quantity input
        if self.quantity_input_rect.collidepoint(pos):
            self.sounds['click'].play()
            self.input_active = True
            self.set_message("Enter quantity", BLACK)
        else:
            self.input_active = False
    
    def execute_transaction(self):
        if not self.quantity_input:
            self.set_message("Please enter a quantity.", RED)
            return
        
        if not self.quantity_input.isdigit():
            self.set_message("Invalid quantity. Enter numbers only.", RED)
            self.quantity_input = "" # Clear invalid input
            return
        
        quantity = int(self.quantity_input)
        if quantity <= 0:
            self.set_message("Quantity must be greater than 0.", RED)
            self.quantity_input = "" # Clear invalid input
            return
            
        stock = self.stocks[self.selected_stock]
        
        if self.transaction_mode == 'BUY':
            if self.portfolio.buy_stock(stock, quantity):
                self.set_message(f"BOUGHT {quantity} shares of {stock.symbol} for ${stock.price * quantity:.2f}", GREEN)
                self.sounds['click'].play()
                self.quantity_input = ""
            else:
                self.set_message(f"BUY FAILED: Not enough cash for {quantity} shares of {stock.symbol}", RED)
        elif self.transaction_mode == 'SELL':
            if self.portfolio.sell_stock(stock, quantity):
                self.set_message(f"SOLD {quantity} shares of {stock.symbol} for ${stock.price * quantity:.2f}", BLUE)
                self.sounds['click'].play()
                self.quantity_input = ""
            else:
                current_holdings = self.portfolio.holdings.get(stock.symbol, 0)
                self.set_message(f"SELL FAILED: Not enough {stock.symbol} shares. You have {current_holdings}.", RED)
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.K_ESCAPE:
                    running = False # Press Escape to exit the program
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False  # Press Escape to exit the program
                    elif self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.execute_transaction()
                        elif event.key == pygame.K_BACKSPACE:
                            self.quantity_input = self.quantity_input[:-1]
                        elif event.unicode.isdigit():
                            self.quantity_input += event.unicode
                    
                    # Stock selection with arrow keys
                    elif event.key == pygame.K_UP:
                        self.selected_stock = (self.selected_stock - 1) % len(self.stocks)
                        self.graph_surface = None  # Force graph update
                        self.set_message(f"Selected {self.stocks[self.selected_stock].symbol}", BLUE)
                        self.sounds['click'].play()
                    elif event.key == pygame.K_DOWN:
                        self.selected_stock = (self.selected_stock + 1) % len(self.stocks)
                        self.graph_surface = None  # Force graph update
                        self.set_message(f"Selected {self.stocks[self.selected_stock].symbol}", BLUE)
                        self.sounds['click'].play()
            
            # Update stock prices
            for stock in self.stocks:
                stock.update_price()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_stock_list()
            self.draw_graph()
            self.draw_portfolio_info()
            self.draw_trading_interface()
            self.display_message() # Display messages last so they are on top
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = StockTradingGame()
    game.run()

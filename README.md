# Stonk Trader - Python Stock Trading Simulator

*A real-time stock market simulation game built with Python, Pygame, and Matplotlib. Experience the thrill of the market with dynamic price movements, technical indicators, and portfolio management.

*[Link to the game](https://cluster.itch.io/stonk-trader)

## Features

*   **Real-Time Market Simulation:** Stocks fluctuate every second using a random walk algorithm with trending bias.
*   **Dynamic Charting:** Live-updating price charts powered by Matplotlib, featuring:
    *   Price history (last 300 data points).
    *   20-period Moving Average (MA).
    *   Visual price change indicators and annotations.
*   **Portfolio Management:** Track your cash, holdings, total value, and Profit/Loss (P/L) percentage.
*   **Interactive UI:** 
    *   Select stocks from a sidebar list.
    *   Buy and Sell interface with quantity input.
    *   Visual feedback and status messages.
*   **Audio:** Background music and UI sound effects.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/Stonk_trader.git
    cd Stonk_trader
    ```

2.  **Install dependencies:**
    Ensure you have Python 3.8+ installed, then run:
    ```bash
    pip install pygame matplotlib numpy
    ```

3.  **Assets:**
    Ensure the following audio files are in the root directory:
    *   `click3.wav` (UI sound)
    *   `BossMain.wav` (Background music)

## How to Play

*   **Select a Stock:** Click on a stock in the left sidebar or use the **UP/DOWN** arrow keys.
*   **Enter Quantity:** Click the input box at the bottom left and type the number of shares.
*   **Trade:** Click the **BUY** or **SELL** buttons to toggle the mode, then press **ENTER** to execute the trade.
*   **Exit:** Press **ESC** to close the game.

## Technical Stack

*   **Pygame:** Handles the game loop, rendering, and user input.
*   **Matplotlib:** Generates the financial charts, which are converted to Pygame surfaces for display.
*   **Asyncio:** Used for the main loop to ensure compatibility with web-based Python environments (like Pyodide).

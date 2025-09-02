#!/usr/bin/env python3
"""
Test data generator for trading journal with lot sizes
Creates 6+ months of sample trade data for testing P&L charts
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Sample trade data with lot sizes
SYMBOLS = {
    'AAPL': {'lot_size': 100, 'price_range': (150, 200)},
    'GOOGL': {'lot_size': 100, 'price_range': (100, 150)},
    'MSFT': {'lot_size': 100, 'price_range': (300, 400)},
    'TSLA': {'lot_size': 100, 'price_range': (200, 300)},
    'AMZN': {'lot_size': 100, 'price_range': (120, 180)},
    'META': {'lot_size': 100, 'price_range': (250, 350)},
    'NVDA': {'lot_size': 100, 'price_range': (400, 600)},
    'NFLX': {'lot_size': 100, 'price_range': (400, 500)},
    'AMD': {'lot_size': 100, 'price_range': (80, 120)},
    'INTC': {'lot_size': 100, 'price_range': (30, 50)},
    'BTCUSD': {'lot_size': 1, 'price_range': (40000, 70000)},
    'ETHUSD': {'lot_size': 1, 'price_range': (2000, 4000)},
    'EURUSD': {'lot_size': 100000, 'price_range': (1.05, 1.15)},
    'GBPUSD': {'lot_size': 100000, 'price_range': (1.20, 1.30)},
    'XAUUSD': {'lot_size': 100, 'price_range': (1800, 2100)},
}
SIDES = ['buy', 'sell']

async def create_test_trades():
    """Create test trades spanning 6+ months with lot sizes"""

    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='app_db'
    )

    try:
        # Clear existing trades (optional - comment out if you want to keep existing data)
        await conn.execute("DELETE FROM trades")
        print("Cleared existing trades")

        # Generate trades for the last 6+ months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 months

        trades_created = 0

        # Generate trades for each month
        current_date = start_date.replace(day=1)  # Start from first day of month

        while current_date < end_date:
            # Generate 8-20 trades per month (more realistic)
            trades_this_month = random.randint(8, 20)

            print(f"Generating {trades_this_month} trades for {current_date.strftime('%Y-%m')}")

            for _ in range(trades_this_month):
                # Random date within the month
                # Get the last day of the current month
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1, day=1)

                last_day = (next_month - timedelta(days=1)).day

                trade_date = current_date.replace(
                    day=random.randint(1, last_day),
                    hour=random.randint(9, 16),  # Trading hours
                    minute=random.randint(0, 59)
                )

                # Skip if trade date is in the future
                if trade_date >= end_date:
                    continue

                # Generate trade data
                symbol = random.choice(list(SYMBOLS.keys()))
                symbol_data = SYMBOLS[symbol]
                lot_size = symbol_data['lot_size']
                price_range = symbol_data['price_range']

                side = random.choice(SIDES)
                quantity = random.randint(1, 10)  # Number of lots
                entry_price = round(random.uniform(price_range[0], price_range[1]), 2)

                # Calculate stop loss and take profit based on side
                if side == 'buy':
                    stop_loss = round(entry_price * random.uniform(0.95, 0.98), 2)
                    take_profit = round(entry_price * random.uniform(1.02, 1.08), 2)
                else:  # sell
                    stop_loss = round(entry_price * random.uniform(1.02, 1.05), 2)
                    take_profit = round(entry_price * random.uniform(0.92, 0.98), 2)

                # Random exit time (1-30 days later)
                exit_date = trade_date + timedelta(days=random.randint(1, 30))

                # Skip if exit date is in the future
                if exit_date >= end_date:
                    continue

                # Calculate exit price and P&L
                if side == 'buy':
                    # 65% chance of hitting take profit, 35% chance of hitting stop loss
                    if random.random() < 0.65:
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                    else:
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                else:  # sell
                    if random.random() < 0.65:
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                    else:
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'

                # Calculate P&L with lot size
                if side == 'buy':
                    pnl = (exit_price - entry_price) * quantity * lot_size
                else:  # sell
                    pnl = (entry_price - exit_price) * quantity * lot_size

                # Add some random fees
                fees = round(random.uniform(0.5, 5.0), 2)
                pnl -= fees

                # Generate checklist data (weighted towards better grades)
                checklist_grades = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D']
                # Weight the grades - more A's and B's
                grade_weights = [0.15, 0.25, 0.20, 0.20, 0.10, 0.05, 0.03, 0.02]
                checklist_grade = random.choices(checklist_grades, weights=grade_weights)[0]
                checklist_score = random.randint(20, 100)

                # Insert trade
                await conn.execute("""
                    INSERT INTO trades (
                        symbol, side, quantity, lot_size, entry_price, entry_time,
                        stop_loss, take_profit, exit_price, exit_time, exit_reason,
                        fees, notes, pnl, checklist_grade, checklist_score
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                    symbol, side, quantity, lot_size, entry_price, trade_date,
                    stop_loss, take_profit, exit_price, exit_date, exit_reason,
                    fees, f"Test trade for {symbol} (Lot: {lot_size})", pnl, checklist_grade, checklist_score
                )

                trades_created += 1

            # Move to next month (handles year transitions properly)
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)

        print(f"\nCreated {trades_created} test trades spanning 6+ months with lot sizes")

        # Show summary
        result = await conn.fetch("""
            SELECT
                COUNT(*) as total_trades,
                COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
                COUNT(CASE WHEN pnl < 0 THEN 1 END) as losing_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM trades
        """)

        if result:
            stats = result[0]
            print(f"\nTrade Summary:")
            print(f"Total Trades: {stats['total_trades']}")
            print(f"Winning Trades: {stats['winning_trades']}")
            print(f"Losing Trades: {stats['losing_trades']}")
            print(f"Total P&L: ${stats['total_pnl']:.2f}")
            print(f"Average P&L: ${stats['avg_pnl']:.2f}")

        # Show monthly breakdown
        monthly_result = await conn.fetch("""
            SELECT
                TO_CHAR(exit_time, 'YYYY-MM') as month,
                COUNT(*) as trades,
                SUM(pnl) as monthly_pnl
            FROM trades
            GROUP BY TO_CHAR(exit_time, 'YYYY-MM')
            ORDER BY month
        """)

        print(f"\nMonthly Breakdown:")
        for row in monthly_result:
            print(f"{row['month']}: {row['trades']} trades, P&L: ${row['monthly_pnl']:.2f}")

        # Show lot size distribution
        lot_result = await conn.fetch("""
            SELECT
                lot_size,
                COUNT(*) as count,
                AVG(pnl) as avg_pnl
            FROM trades
            GROUP BY lot_size
            ORDER BY lot_size
        """)

        print(f"\nLot Size Distribution:")
        for row in lot_result:
            print(f"Lot Size {row['lot_size']}: {row['count']} trades, Avg P&L: ${row['avg_pnl']:.2f}")

        # Show grade distribution
        grade_result = await conn.fetch("""
            SELECT
                checklist_grade,
                COUNT(*) as count
            FROM trades
            WHERE checklist_grade IS NOT NULL
            GROUP BY checklist_grade
            ORDER BY checklist_grade
        """)

        print(f"\nGrade Distribution:")
        for row in grade_result:
            print(f"{row['checklist_grade']}: {row['count']} trades")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_test_trades())

def calculate_allocation(amount: float, risk: str, horizon: str) -> dict:
    """
    Returns the target allocation between index funds and curated stocks.
    
    amount: float
    risk: 'Low', 'Medium', 'High'
    horizon: 'Short (<3y)', 'Medium (3-7y)', 'Long (>7y)'
    """
    index_pct = 60
    stock_pct = 40
    
    if risk == "Low" or horizon == "Short (<3y)":
        index_pct = 70
        stock_pct = 30
    elif risk == "High" and horizon == "Long (>7y)":
        index_pct = 50
        stock_pct = 50
        
    return {
        "Index Exposure (Nifty 50)": index_pct,
        "Curated Stock Basket": stock_pct,
        "Index Amount": amount * (index_pct / 100),
        "Stock Amount": amount * (stock_pct / 100)
    }

def evaluate_position_sizing(portfolio: list, total_portfolio_value: float) -> list:
    """
    Evaluates sizing rules and returns actionable alerts.
    Rule 1: Max allocation per stock 5-8% (Strictly enforced at 8%)
    Rule 2: Averaging down is disallowed
    """
    alerts = []
    if total_portfolio_value == 0:
        return alerts
        
    for item in portfolio:
        sym = item.get("symbol", item.get("Symbol", "Unknown"))
        qty = float(item.get("quantity", item.get("Quantity", 0)))
        current_price = float(item.get("current_price", item.get("avg_price", 0))) # fallback
        avg_price = float(item.get("avg_price", current_price))
        
        position_value = qty * current_price
        allocation_pct = (position_value / total_portfolio_value) * 100
        
        if allocation_pct > 8.0:
            excess_value = position_value - (total_portfolio_value * 0.08)
            excess_qty = max(1, int(excess_value / current_price))
            alerts.append({
                "type": "WARNING",
                "symbol": sym,
                "message": f"Concentration Risk: Allocation is {allocation_pct:.1f}% (Max 8%). Consider reducing position.",
                "action": f"Sell {excess_qty} shares to return to 8% limit."
            })
            
        if item.get("intent") == "buy_more":
            if current_price < avg_price:
                alerts.append({
                    "type": "BLOCKED",
                    "symbol": sym,
                    "message": "Blind averaging down is disabled. The price trend is negative relative to your entry.",
                    "action": "Hold current position. Do not add capital."
                })
    return alerts

def evaluate_risk_control(portfolio: list, total_portfolio_value: float) -> dict:
    """
    Evaluates individual and portfolio-level risk control mechanisms.
    """
    position_alerts = []
    portfolio_alerts = []
    
    total_cost = 0.0
    total_current = 0.0
    
    for item in portfolio:
        sym = item.get("symbol", item.get("Symbol", "Unknown"))
        qty = float(item.get("quantity", item.get("Quantity", 0.0)))
        avg_price = float(item.get("avg_price", 0.0))
        current_price = float(item.get("current_price", 0.0))
        
        if avg_price > 0 and qty > 0:
            cost_basis = avg_price * qty
            current_val = current_price * qty
            
            total_cost += cost_basis
            total_current += current_val
            
            drawdown_pct = ((current_price - avg_price) / avg_price) * 100
            
            # Risk Downside Estimates
            expected_downside = current_price * 0.75  # ~25% normal
            crisis_downside = current_price * 0.60    # ~40% crisis
            
            item["risk_metrics"] = {
                "drawdown": drawdown_pct,
                "normal_downside": expected_downside,
                "crisis_downside": crisis_downside
            }
            
            if drawdown_pct <= -25.0:
                sell_qty = max(1, int(qty // 2))
                position_alerts.append({
                    "type": "ACTION REQUIRED",
                    "symbol": sym,
                    "message": f"Hard stop triggered. Drawdown is {drawdown_pct:.1f}%.",
                    "action": f"Mandatory risk reduction: Sell {sell_qty} shares instantly."
                })
            elif drawdown_pct <= -15.0:
                position_alerts.append({
                    "type": "WARNING",
                    "symbol": sym,
                    "message": f"Position drawdown is {drawdown_pct:.1f}%. Approaching hard stop (-25%).",
                    "action": "Review thesis and prepare to reduce position."
                })
                
    # Portfolio level rules
    if total_cost > 0:
        portfolio_drawdown = ((total_current - total_cost) / total_cost) * 100
        
        if portfolio_drawdown <= -15.0:
             portfolio_alerts.append({
                "type": "CRITICAL",
                "message": f"Portfolio drawdown at {portfolio_drawdown:.1f}%.",
                "action": "Halt stock buys. Shift new capital to Index Funds only."
            })
        elif portfolio_drawdown <= -10.0:
            portfolio_alerts.append({
                "type": "WARNING",
                "message": f"Portfolio drawdown at {portfolio_drawdown:.1f}%.",
                "action": "Reduce exposure to high-beta/high-risk positions."
            })
            
    return {
        "position_alerts": position_alerts,
        "portfolio_alerts": portfolio_alerts,
        "portfolio_drawdown": portfolio_drawdown if total_cost > 0 else 0
    }

def evaluate_exit_strategy(item: dict) -> list:
    """
    Evaluates exit conditions and winner management.
    Requires item to have: current_price, avg_price, dma_200 (optional), qty
    """
    alerts = []
    sym = item.get("symbol", item.get("Symbol", "Unknown"))
    qty = float(item.get("quantity", item.get("Quantity", 0)))
    current_price = float(item.get("current_price", 0))
    avg_price = float(item.get("avg_price", 0))
    dma_200 = float(item.get("dma_200", 0))
    
    if current_price == 0 or avg_price == 0:
        return alerts
        
    gain_pct = ((current_price - avg_price) / avg_price) * 100
    
    # 200 DMA break
    if dma_200 > 0 and current_price < dma_200:
        alerts.append({
             "type": "EXIT SIGNAL",
             "symbol": sym,
             "message": "Price closed below 200-day moving average.",
             "action": f"Consider full exit: Sell {qty} shares."
        })
        
    # Winner management
    if gain_pct >= 40.0:
        stop_price = current_price * 0.85 # -15% trailing
        alerts.append({
             "type": "WINNER MANAGEMENT",
             "symbol": sym,
             "message": f"Exceptional gain of {gain_pct:.1f}%. Using wider trailing stop.",
             "action": f"Set strict trailing stop at INR {stop_price:.2f}."
        })
    elif gain_pct >= 20.0:
        stop_price = current_price * 0.90 # -10% trailing
        alerts.append({
             "type": "WINNER MANAGEMENT",
             "symbol": sym,
             "message": f"Solid gain of {gain_pct:.1f}%. Securing profits.",
             "action": f"Set tight trailing stop at INR {stop_price:.2f}."
        })
        
    return alerts

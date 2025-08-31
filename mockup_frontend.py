# nunno_streamlit_enhanced.py
import streamlit as st
import requests
import base64
import re
import io
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fuzzywuzzy import process
import time
from typing import Dict, List, Optional, Tuple
import json
import streamlit as st
import time
import base64
from pathlib import Path

# --- Opening Page Logic ---
if "splash_shown" not in st.session_state:
    st.session_state["splash_shown"] = False

if not st.session_state["splash_shown"]:
    # Hide Streamlit default UI
    hide = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: black !important;} /* force full black bg */
    html, body, [data-testid="stAppViewContainer"] {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background-color: black !important;
    }
    </style>
    """
    st.markdown(hide, unsafe_allow_html=True)

    # Load logo.png from local repo (root folder)
    logo_path = Path("logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_data = f.read()
        logo_b64 = base64.b64encode(logo_data).decode()
        logo_src = f"data:image/png;base64,{logo_b64}"
    else:
        logo_src = ""  # fallback

    # Splash Screen (fade + breathing + blur)
    splash_html = f"""
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                display: flex; justify-content: center; align-items: center;
                background-color: black; z-index: 9999;">
        {"<img src='"+logo_src+"' class='breathing-logo'>" if logo_src else "<h1 style='color:white; font-size:3em;'>Nunno</h1>"}
    </div>

    <style>
    @keyframes fadeBreathBlur {{
      0%   {{ opacity: 0; transform: scale(0.95); filter: blur(5px); }}
      20%  {{ opacity: 1; transform: scale(1.05); filter: blur(0px); }}
      70%  {{ opacity: 1; transform: scale(1.08); filter: blur(0px); }}
      100% {{ opacity: 0; transform: scale(1.2); filter: blur(12px); }}
    }}
    .breathing-logo {{
        width: 30vw;
        max-width: 600px;
        animation: fadeBreathBlur 3s ease-in-out forwards;
    }}
    </style>
    """
    st.markdown(splash_html, unsafe_allow_html=True)

    # Wait, then rerun main app
    time.sleep(3)
    st.session_state["splash_shown"] = True
    st.rerun()

# Try importing local modules (optional - prediction & monte carlo features)
try:
    import betterpredictormodule
except Exception:
    betterpredictormodule = None

try:
    from montecarlo_module import simulate_trades, monte_carlo_summary
except Exception:
    simulate_trades = None
    monte_carlo_summary = None

# API keys (recommended to put into Streamlit secrets)
try:
    AI_API_KEY = st.secrets.get("AI_API_KEY", "")
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")
except:
    AI_API_KEY = ""
    NEWS_API_KEY = ""

SYSTEM_PROMPT = (
    "You are Nunno, a friendly AI (Numinous Nexus AI). "
    "You teach trading and investing to complete beginners in very simple language. "
    "The user's name is {user_name}, age {user_age}. Tailor explanations for beginners. "
    "You have integrated prediction, tokenomics, monte carlo simulation and chart analysis. "
    "When giving outputs, make them neat with headings, tables, and emojis. "
    "If asked about your founder, say you were built by Mujtaba Kazmi. "
    "For tokenomics analysis, explain each metric in simple terms that beginners can understand."
)

MAX_HISTORY_MESSAGES = 20

class ComprehensiveTokenomics:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
    def fetch_comprehensive_token_data(self, coin_id: str, investment_amount: float = 1000) -> Dict:
        """Fetch comprehensive tokenomics data with detailed analysis"""
        try:
            # Main coin data from CoinGecko
            coin_data = self._fetch_coingecko_data(coin_id)
            if not coin_data:
                return None
                
            # Historical price analysis
            price_analysis = self._analyze_price_history(coin_id)
            
            # Market metrics
            market_metrics = self._calculate_market_metrics(coin_data, investment_amount)
            
            # On-chain and technical metrics
            technical_metrics = self._calculate_technical_metrics(coin_data)
            
            # Liquidity and exchange data
            liquidity_data = self._fetch_liquidity_data(coin_data)
            
            # Social and development metrics
            social_metrics = self._fetch_social_metrics(coin_data)
            
            # Risk assessment
            risk_assessment = self._calculate_risk_metrics(coin_data, price_analysis, market_metrics)
            
            # Supply economics
            supply_economics = self._analyze_supply_economics(coin_data)
            
            # Competitive analysis
            competitive_metrics = self._get_competitive_position(coin_data)
            
            # Combine all data
            comprehensive_data = {
                **self._format_basic_info(coin_data),
                **market_metrics,
                **price_analysis,
                **technical_metrics,
                **liquidity_data,
                **social_metrics,
                **risk_assessment,
                **supply_economics,
                **competitive_metrics
            }
            
            return comprehensive_data
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return None
    
    def _fetch_coingecko_data(self, coin_id: str) -> Dict:
        """Fetch detailed coin data from CoinGecko"""
        try:
            url = f"{self.coingecko_base}/coins/{coin_id.lower().strip()}"
            params = {
                "localization": "false",
                "tickers": "true",
                "market_data": "true",
                "community_data": "true",
                "developer_data": "true",
                "sparkline": "false"
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"CoinGecko API error: {e}")
            return None
    
    def _analyze_price_history(self, coin_id: str) -> Dict:
        """Analyze historical price data for multiple timeframes"""
        try:
            timeframes = {
                "7d": 7,
                "30d": 30,
                "90d": 90,
                "1y": 365
            }
            
            analysis = {}
            
            for period, days in timeframes.items():
                url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
                params = {"vs_currency": "usd", "days": days}
                
                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    prices = [p[1] for p in data.get("prices", [])]
                    volumes = [v[1] for v in data.get("total_volumes", [])]
                    
                    if len(prices) >= 2:
                        returns = self._calculate_returns_metrics(prices, days)
                        volume_analysis = self._analyze_volume(volumes)
                        
                        analysis[f"Performance_{period}"] = f"{returns['total_return']:+.2f}% (Vol: {returns['volatility']:.1f}%)"
                        analysis[f"CAGR_{period}"] = f"{returns['annualized_return']:+.2f}%"
                        analysis[f"Sharpe_Ratio_{period}"] = f"{returns['sharpe_ratio']:.2f}"
                        analysis[f"Max_Drawdown_{period}"] = f"-{returns['max_drawdown']:.2f}%"
                        analysis[f"Avg_Volume_{period}"] = f"${volume_analysis['avg_volume']/1e6:,.1f}M"
                        
                    time.sleep(0.2)  # Rate limiting
                    
                except Exception:
                    continue
            
            return analysis
            
        except Exception:
            return {}
    
    def _calculate_returns_metrics(self, prices: List[float], days: int) -> Dict:
        """Calculate comprehensive return metrics"""
        if len(prices) < 2:
            return {}
            
        # Calculate returns
        returns = [np.log(prices[i+1] / prices[i]) for i in range(len(prices)-1)]
        
        # Total return
        total_return = (prices[-1] / prices[0] - 1) * 100
        
        # Annualized return
        annualized_return = ((prices[-1] / prices[0]) ** (365/days) - 1) * 100
        
        # Volatility (annualized)
        volatility = np.std(returns) * np.sqrt(365) * 100
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return/100 - risk_free_rate) / (volatility/100) if volatility > 0 else 0
        
        # Maximum drawdown
        peak = prices[0]
        max_dd = 0
        for price in prices:
            if price > peak:
                peak = price
            dd = (peak - price) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_dd
        }
    
    def _analyze_volume(self, volumes: List[float]) -> Dict:
        """Analyze trading volume patterns"""
        if len(volumes) < 7:
            return {"avg_volume": 0, "trend": "Unknown"}
            
        avg_volume = np.mean(volumes)
        recent_avg = np.mean(volumes[-7:])  # Last 7 days
        older_avg = np.mean(volumes[-14:-7]) if len(volumes) >= 14 else avg_volume
        
        trend = "Increasing" if recent_avg > older_avg * 1.1 else "Decreasing" if recent_avg < older_avg * 0.9 else "Stable"
        
        return {
            "avg_volume": avg_volume,
            "trend": trend
        }
    
    def _calculate_market_metrics(self, coin_data: Dict, investment_amount: float) -> Dict:
        """Calculate advanced market metrics"""
        market_data = coin_data.get("market_data", {})
        
        # Basic price and supply data
        price = market_data.get("current_price", {}).get("usd", 0) or 0
        circulating_supply = market_data.get("circulating_supply") or 0
        total_supply = market_data.get("total_supply") or 0
        max_supply = market_data.get("max_supply") or 0
        market_cap = market_data.get("market_cap", {}).get("usd", 0) or 0
        volume_24h = market_data.get("total_volume", {}).get("usd", 0) or 0
        
        # Advanced calculations
        fdv = total_supply * price if total_supply else market_cap
        max_fdv = max_supply * price if max_supply else None
        
        circulating_percent = (circulating_supply / total_supply) * 100 if total_supply else None
        max_supply_percent = (circulating_supply / max_supply) * 100 if max_supply else None
        
        # Volume metrics
        volume_to_mcap = (volume_24h / market_cap) * 100 if market_cap > 0 else 0
        
        # Investment calculations
        tokens_bought = investment_amount / price if price > 0 else 0
        
        # Price performance metrics
        price_changes = {
            "1h": market_data.get("price_change_percentage_1h_in_currency", {}).get("usd"),
            "24h": market_data.get("price_change_percentage_24h_in_currency", {}).get("usd"),
            "7d": market_data.get("price_change_percentage_7d_in_currency", {}).get("usd"),
            "30d": market_data.get("price_change_percentage_30d_in_currency", {}).get("usd"),
            "1y": market_data.get("price_change_percentage_1y_in_currency", {}).get("usd")
        }
        
        # All-time high/low analysis
        ath = market_data.get("ath", {}).get("usd", 0)
        atl = market_data.get("atl", {}).get("usd", 0)
        ath_change = market_data.get("ath_change_percentage", {}).get("usd", 0)
        atl_change = market_data.get("atl_change_percentage", {}).get("usd", 0)
        ath_date = market_data.get("ath_date", {}).get("usd", "")
        atl_date = market_data.get("atl_date", {}).get("usd", "")
        
        return {
            "Current_Price": f"${price:,.8f}",
            "Market_Cap": f"${market_cap/1e9:,.2f}B" if market_cap >= 1e9 else f"${market_cap/1e6:,.2f}M",
            "Market_Cap_Rank": str(market_data.get("market_cap_rank", "N/A")),
            "24h_Volume": f"${volume_24h/1e9:,.2f}B" if volume_24h >= 1e9 else f"${volume_24h/1e6:,.2f}M",
            "Volume_to_MCap_Ratio": f"{volume_to_mcap:.2f}%",
            "Circulating_Supply": f"{circulating_supply/1e6:,.2f}M" if circulating_supply >= 1e6 else f"{circulating_supply:,.0f}",
            "Total_Supply": f"{total_supply/1e6:,.2f}M" if total_supply and total_supply >= 1e6 else f"{total_supply:,.0f}" if total_supply else "N/A",
            "Max_Supply": f"{max_supply/1e6:,.2f}M" if max_supply and max_supply >= 1e6 else f"{max_supply:,.0f}" if max_supply else "Unlimited",
            "Circulating_Percentage": f"{circulating_percent:.2f}%" if circulating_percent else "N/A",
            "Supply_Inflation_Rate": f"{self._calculate_inflation_rate(circulating_supply, total_supply, max_supply):.2f}% annually",
            "Fully_Diluted_Valuation": f"${fdv/1e9:,.2f}B" if fdv >= 1e9 else f"${fdv/1e6:,.2f}M",
            "FDV_to_MCap_Ratio": f"{(fdv/market_cap):,.2f}x" if market_cap > 0 else "N/A",
            "Investment_Tokens": f"{tokens_bought:,.6f} tokens",
            "Price_Change_1h": f"{price_changes['1h']:+.2f}%" if price_changes['1h'] else "N/A",
            "Price_Change_24h": f"{price_changes['24h']:+.2f}%" if price_changes['24h'] else "N/A",
            "Price_Change_7d": f"{price_changes['7d']:+.2f}%" if price_changes['7d'] else "N/A",
            "Price_Change_30d": f"{price_changes['30d']:+.2f}%" if price_changes['30d'] else "N/A",
            "Price_Change_1y": f"{price_changes['1y']:+.2f}%" if price_changes['1y'] else "N/A",
            "All_Time_High": f"${ath:,.8f}",
            "ATH_Date": ath_date.split('T')[0] if ath_date else "N/A",
            "Distance_from_ATH": f"{ath_change:+.2f}%",
            "All_Time_Low": f"${atl:,.8f}",
            "ATL_Date": atl_date.split('T')[0] if atl_date else "N/A",
            "Distance_from_ATL": f"{atl_change:+.2f}%"
        }
    
    def _calculate_inflation_rate(self, circulating: float, total: float, max_supply: float) -> float:
        """Calculate estimated annual inflation rate"""
        if not circulating or not total:
            return 0.0
            
        if max_supply and circulating >= max_supply * 0.99:  # Nearly fully diluted
            return 0.0
            
        # Estimate based on remaining supply to be released
        remaining = total - circulating if total > circulating else 0
        if remaining <= 0:
            return 0.0
            
        # Rough estimation: assume remaining supply is released over next 3-5 years
        annual_new_supply = remaining / 4  # 4 year average
        current_inflation_rate = (annual_new_supply / circulating) * 100
        
        return min(current_inflation_rate, 100)  # Cap at 100% for sanity
    
    def _calculate_technical_metrics(self, coin_data: Dict) -> Dict:
        """Calculate technical and fundamental metrics"""
        market_data = coin_data.get("market_data", {})
        
        # Market dominance
        market_cap = market_data.get("market_cap", {}).get("usd", 0) or 0
        
        # Calculate market cap categories
        if market_cap >= 10e9:
            mcap_category = "Large Cap (>$10B)"
        elif market_cap >= 2e9:
            mcap_category = "Mid Cap ($2B-$10B)"
        elif market_cap >= 300e6:
            mcap_category = "Small Cap ($300M-$2B)"
        elif market_cap >= 50e6:
            mcap_category = "Micro Cap ($50M-$300M)"
        else:
            mcap_category = "Nano Cap (<$50M)"
        
        # Price metrics
        price = market_data.get("current_price", {}).get("usd", 0) or 0
        ath = market_data.get("ath", {}).get("usd", 0)
        atl = market_data.get("atl", {}).get("usd", 0)
        
        # Price position analysis
        if ath > 0 and atl > 0:
            price_range_position = ((price - atl) / (ath - atl)) * 100
        else:
            price_range_position = 0
            
        return {
            "Market_Cap_Category": mcap_category,
            "Price_Range_Position": f"{price_range_position:.1f}% between ATL and ATH",
            "Genesis_Date": coin_data.get("genesis_date", "N/A"),
            "Block_Time_Minutes": str(coin_data.get("block_time_in_minutes", "N/A")),
            "Hashing_Algorithm": coin_data.get("hashing_algorithm", "N/A"),
            "Market_Data_Last_Updated": market_data.get("last_updated", "N/A").split('T')[0] if market_data.get("last_updated") else "N/A"
        }
    
    def _fetch_liquidity_data(self, coin_data: Dict) -> Dict:
        """Analyze liquidity and exchange data"""
        try:
            tickers = coin_data.get("tickers", [])
            
            if not tickers:
                return {"Exchange_Count": "0", "Top_Exchange": "N/A", "Liquidity_Score": "Low"}
            
            # Count unique exchanges
            exchanges = set()
            total_volume = 0
            exchange_volumes = {}
            
            for ticker in tickers[:50]:  # Limit to avoid rate limits
                exchange = ticker.get("market", {}).get("name", "Unknown")
                volume = ticker.get("converted_volume", {}).get("usd", 0) or 0
                
                exchanges.add(exchange)
                total_volume += volume
                
                if exchange in exchange_volumes:
                    exchange_volumes[exchange] += volume
                else:
                    exchange_volumes[exchange] = volume
            
            # Find top exchange
            top_exchange = max(exchange_volumes.items(), key=lambda x: x[1])[0] if exchange_volumes else "N/A"
            
            # Liquidity score based on exchange count and volume
            exchange_count = len(exchanges)
            if exchange_count >= 20 and total_volume >= 100e6:
                liquidity_score = "Excellent"
            elif exchange_count >= 10 and total_volume >= 10e6:
                liquidity_score = "Good"
            elif exchange_count >= 5 and total_volume >= 1e6:
                liquidity_score = "Fair"
            else:
                liquidity_score = "Poor"
            
            return {
                "Exchange_Count": str(exchange_count),
                "Top_Exchange": top_exchange,
                "Total_Exchange_Volume": f"${total_volume/1e6:,.1f}M",
                "Liquidity_Score": liquidity_score
            }
            
        except Exception:
            return {"Exchange_Count": "N/A", "Top_Exchange": "N/A", "Liquidity_Score": "Unknown"}
    
    def _fetch_social_metrics(self, coin_data: Dict) -> Dict:
        """Fetch social media and community metrics"""
        try:
            community = coin_data.get("community_data", {})
            developer = coin_data.get("developer_data", {})
            
            # Social metrics
            twitter_followers = community.get("twitter_followers") or 0
            reddit_subscribers = community.get("reddit_subscribers") or 0
            telegram_users = community.get("telegram_channel_user_count") or 0
            
            # Developer metrics
            github_forks = developer.get("forks") or 0
            github_stars = developer.get("stars") or 0
            github_commits_4w = developer.get("commit_count_4_weeks") or 0
            github_contributors = developer.get("subscribers") or 0
            
            # Calculate social score
            social_score = self._calculate_social_score(twitter_followers, reddit_subscribers, telegram_users)
            dev_score = self._calculate_development_score(github_commits_4w, github_contributors, github_stars)
            
            return {
                "Twitter_Followers": f"{twitter_followers:,}" if twitter_followers else "N/A",
                "Reddit_Subscribers": f"{reddit_subscribers:,}" if reddit_subscribers else "N/A",
                "Telegram_Users": f"{telegram_users:,}" if telegram_users else "N/A",
                "Social_Media_Score": social_score,
                "GitHub_Stars": f"{github_stars:,}" if github_stars else "N/A",
                "GitHub_Forks": f"{github_forks:,}" if github_forks else "N/A",
                "GitHub_Commits_4w": f"{github_commits_4w:,}" if github_commits_4w else "N/A",
                "GitHub_Contributors": f"{github_contributors:,}" if github_contributors else "N/A",
                "Development_Activity": dev_score
            }
            
        except Exception:
            return {
                "Social_Media_Score": "Unknown",
                "Development_Activity": "Unknown"
            }
    
    def _calculate_social_score(self, twitter: int, reddit: int, telegram: int) -> str:
        """Calculate social media engagement score"""
        total_score = 0
        
        # Twitter scoring
        if twitter >= 1000000:
            total_score += 30
        elif twitter >= 100000:
            total_score += 20
        elif twitter >= 10000:
            total_score += 10
        
        # Reddit scoring
        if reddit >= 500000:
            total_score += 25
        elif reddit >= 50000:
            total_score += 15
        elif reddit >= 5000:
            total_score += 8
        
        # Telegram scoring
        if telegram >= 100000:
            total_score += 20
        elif telegram >= 10000:
            total_score += 10
        elif telegram >= 1000:
            total_score += 5
        
        if total_score >= 50:
            return "Excellent (Very High Engagement)"
        elif total_score >= 30:
            return "Good (High Engagement)"
        elif total_score >= 15:
            return "Fair (Moderate Engagement)"
        else:
            return "Poor (Low Engagement)"
    
    def _calculate_development_score(self, commits: int, contributors: int, stars: int) -> str:
        """Calculate development activity score"""
        score = 0
        
        # Commits in last 4 weeks
        if commits >= 100:
            score += 40
        elif commits >= 50:
            score += 25
        elif commits >= 10:
            score += 15
        elif commits > 0:
            score += 5
        
        # Contributors
        if contributors >= 100:
            score += 30
        elif contributors >= 20:
            score += 20
        elif contributors >= 5:
            score += 10
        
        # Stars
        if stars >= 10000:
            score += 30
        elif stars >= 1000:
            score += 20
        elif stars >= 100:
            score += 10
        
        if score >= 70:
            return "Very Active (High Development)"
        elif score >= 40:
            return "Active (Regular Development)"
        elif score >= 20:
            return "Moderate (Some Development)"
        else:
            return "Low (Minimal Development)"
    
    def _calculate_risk_metrics(self, coin_data: Dict, price_analysis: Dict, market_metrics: Dict) -> Dict:
        """Calculate comprehensive risk assessment"""
        market_data = coin_data.get("market_data", {})
        
        # Extract key metrics for risk calculation
        market_cap = market_data.get("market_cap", {}).get("usd", 0) or 0
        circulating_supply = market_data.get("circulating_supply") or 0
        total_supply = market_data.get("total_supply") or 0
        max_supply = market_data.get("max_supply") or 0
        volume_24h = market_data.get("total_volume", {}).get("usd", 0) or 0
        
        risk_factors = []
        risk_score = 0
        
        # Market cap risk
        if market_cap < 50e6:
            risk_factors.append("Very Low Market Cap (<$50M)")
            risk_score += 25
        elif market_cap < 300e6:
            risk_factors.append("Low Market Cap (<$300M)")
            risk_score += 15
        elif market_cap < 2e9:
            risk_score += 5
        
        # Supply risk
        if total_supply and circulating_supply:
            circ_percent = (circulating_supply / total_supply) * 100
            if circ_percent < 50:
                risk_factors.append("Low Circulating Supply (<50%)")
                risk_score += 20
            elif circ_percent < 80:
                risk_score += 10
        
        # Liquidity risk
        volume_to_mcap = (volume_24h / market_cap) * 100 if market_cap > 0 else 0
        if volume_to_mcap < 0.5:
            risk_factors.append("Very Low Liquidity (<0.5% vol/mcap)")
            risk_score += 20
        elif volume_to_mcap < 2:
            risk_factors.append("Low Liquidity (<2% vol/mcap)")
            risk_score += 10
        
        # Volatility risk from price analysis
        for key, value in price_analysis.items():
            if "Performance_30d" in key and "%" in str(value):
                try:
                    perf_30d = float(str(value).split('(Vol: ')[1].split('%')[0])
                    if perf_30d > 100:
                        risk_factors.append("Extremely High Volatility (>100%)")
                        risk_score += 25
                    elif perf_30d > 50:
                        risk_factors.append("High Volatility (>50%)")
                        risk_score += 15
                except:
                    pass
        
        # Age risk
        genesis_date = coin_data.get("genesis_date")
        if genesis_date:
            try:
                genesis = datetime.fromisoformat(genesis_date.replace('Z', '+00:00'))
                age_days = (datetime.now(genesis.tzinfo) - genesis).days
                if age_days < 365:
                    risk_factors.append("New Token (<1 year old)")
                    risk_score += 15
                elif age_days < 730:
                    risk_score += 5
            except:
                pass
        
        # Risk level classification
        if risk_score >= 60:
            risk_level = "EXTREMELY HIGH RISK"
        elif risk_score >= 40:
            risk_level = "HIGH RISK"
        elif risk_score >= 20:
            risk_level = "MODERATE RISK"
        elif risk_score >= 10:
            risk_level = "LOW-MODERATE RISK"
        else:
            risk_level = "RELATIVELY LOW RISK"
        
        return {
            "Risk_Level": risk_level,
            "Risk_Score": f"{risk_score}/100",
            "Risk_Factors": "; ".join(risk_factors) if risk_factors else "No major risk factors identified",
            "Investment_Recommendation": self._get_investment_recommendation(risk_score, market_cap)
        }
    
    def _get_investment_recommendation(self, risk_score: int, market_cap: float) -> str:
        """Generate investment recommendation based on risk"""
        if risk_score >= 60:
            return "NOT RECOMMENDED - Only for experienced traders with high risk tolerance"
        elif risk_score >= 40:
            return "HIGH RISK - Maximum 2-5% of portfolio, expect high volatility"
        elif risk_score >= 20:
            return "MODERATE RISK - Consider 5-10% of portfolio allocation"
        elif risk_score >= 10:
            return "LOW-MODERATE RISK - Suitable for 10-20% portfolio allocation"
        else:
            return "RELATIVELY SAFE - Can consider larger allocation (20%+ of crypto portfolio)"
    
    def _analyze_supply_economics(self, coin_data: Dict) -> Dict:
        """Analyze token supply economics in detail"""
        market_data = coin_data.get("market_data", {})
        
        circulating = market_data.get("circulating_supply") or 0
        total = market_data.get("total_supply") or 0
        max_supply = market_data.get("max_supply") or 0
        price = market_data.get("current_price", {}).get("usd", 0) or 0
        
        # Supply distribution analysis
        if max_supply and total and circulating:
            unreleased_tokens = max_supply - circulating
            unreleased_value = unreleased_tokens * price
            future_dilution = (unreleased_tokens / circulating) * 100 if circulating > 0 else 0
            
            # Token release rate estimation
            if total > circulating:
                current_unreleased = total - circulating
                release_timeline = "Immediate to medium-term release risk"
            else:
                current_unreleased = 0
                release_timeline = "No immediate release pressure"
            
            supply_model = self._determine_supply_model(max_supply, total, circulating)
            
        else:
            unreleased_value = 0
            future_dilution = 0
            release_timeline = "Unknown"
            supply_model = "Unknown"
        
        return {
            "Supply_Model": supply_model,
            "Unreleased_Token_Value": f"${unreleased_value/1e9:,.2f}B" if unreleased_value >= 1e9 else f"${unreleased_value/1e6:,.2f}M",
            "Future_Dilution_Risk": f"{future_dilution:.1f}%",
            "Token_Release_Timeline": release_timeline,
            "Supply_Distribution": self._analyze_supply_distribution(circulating, total, max_supply)
        }
    
    def _determine_supply_model(self, max_supply: float, total: float, circulating: float) -> str:
        """Determine the token's supply model"""
        if not max_supply:
            return "Inflationary (No Max Supply)"
        elif max_supply == total == circulating:
            return "Fixed Supply (Fully Circulating)"
        elif max_supply == total:
            return "Fixed Supply (Gradual Release)"
        elif total < max_supply:
            return "Controlled Emission Model"
        else:
            return "Unknown Supply Model"
    
    def _analyze_supply_distribution(self, circulating: float, total: float, max_supply: float) -> str:
        """Analyze how token supply is distributed"""
        if not circulating:
            return "No data available"
            
        if max_supply:
            circ_of_max = (circulating / max_supply) * 100
            if circ_of_max >= 95:
                return "Fully distributed (>95% of max supply)"
            elif circ_of_max >= 70:
                return "Mostly distributed (70-95% of max supply)"
            elif circ_of_max >= 40:
                return "Partially distributed (40-70% of max supply)"
            else:
                return "Early distribution phase (<40% of max supply)"
        else:
            return "Ongoing emission (no max supply)"
    
    def _get_competitive_position(self, coin_data: Dict) -> Dict:
        """Analyze competitive position and market context"""
        try:
            market_data = coin_data.get("market_data", {})
            market_cap = market_data.get("market_cap", {}).get("usd", 0) or 0
            market_cap_rank = market_data.get("market_cap_rank", 999)
            
            # Category analysis
            categories = coin_data.get("categories", [])
            main_category = categories[0] if categories else "Unknown"
            
            # Market position
            if market_cap_rank <= 10:
                market_position = "Top 10 - Blue Chip Crypto"
            elif market_cap_rank <= 50:
                market_position = "Top 50 - Established Project"
            elif market_cap_rank <= 100:
                market_position = "Top 100 - Mid-tier Project"
            elif market_cap_rank <= 500:
                market_position = "Top 500 - Emerging Project"
            else:
                market_position = "Outside Top 500 - Speculative"
            
            return {
                "Primary_Category": main_category,
                "Market_Position": market_position,
                "Competitive_Rank": f"#{market_cap_rank}" if market_cap_rank < 999 else "Unranked",
                "All_Categories": ", ".join(categories[:5]) if len(categories) > 1 else main_category
            }
            
        except Exception:
            return {
                "Primary_Category": "Unknown",
                "Market_Position": "Unknown",
                "Competitive_Rank": "Unknown"
            }
    
    def _format_basic_info(self, coin_data: Dict) -> Dict:
        """Format basic token information"""
        # Safe handling of potentially None values
        asset_platform = coin_data.get("asset_platform_id")
        if asset_platform:
            blockchain = asset_platform.replace("-", " ").title()
        else:
            blockchain = "Native Blockchain"
            
        # Safe handling of homepage links
        homepage_links = coin_data.get("links", {}).get("homepage", [])
        if homepage_links and isinstance(homepage_links, list):
            website = ", ".join([link for link in homepage_links[:2] if link])
        else:
            website = "N/A"
            
        # Safe handling of contract address
        contract_addr = coin_data.get("contract_address")
        if contract_addr:
            contract_address = str(contract_addr)
        else:
            contract_address = "Native Token"
            
        return {
            "Token_Name": coin_data.get("name", "Unknown"),
            "Symbol": (coin_data.get("symbol") or "").upper(),
            "Description": self._truncate_description(coin_data.get("description", {}).get("en", "")),
            "Website": website,
            "Blockchain": blockchain,
            "Contract_Address": contract_address
        }
    
    def _truncate_description(self, description: str) -> str:
        """Truncate description to reasonable length"""
        if not description:
            return "No description available"
        
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        
        # Truncate to first 200 characters
        if len(description) > 200:
            return description[:200] + "..."
        return description

def get_ai_tokenomics_explanation(token_data: Dict, user_name: str) -> str:
    """Generate AI explanation of tokenomics data"""
    if not AI_API_KEY or not token_data:
        return "Unable to generate explanation - API key not configured or no data available."
    
    # Create a summary of key metrics for AI to explain
    key_metrics = {
        "Token": f"{token_data.get('Token_Name')} ({token_data.get('Symbol')})",
        "Price": token_data.get("Current_Price"),
        "Market_Cap": token_data.get("Market_Cap"),
        "Rank": token_data.get("Market_Cap_Rank"),
        "Supply_Model": token_data.get("Supply_Model"),
        "Circulating_Percentage": token_data.get("Circulating_Percentage"),
        "FDV_Ratio": token_data.get("FDV_to_MCap_Ratio"),
        "Risk_Level": token_data.get("Risk_Level"),
        "Liquidity_Score": token_data.get("Liquidity_Score"),
        "Social_Score": token_data.get("Social_Media_Score"),
        "Development_Activity": token_data.get("Development_Activity"),
        "Investment_Recommendation": token_data.get("Investment_Recommendation")
    }
    
    prompt = f"""
    Explain this tokenomics analysis to {user_name} in simple, beginner-friendly terms. 
    Break down what each metric means and why it matters for investors:
    
    {json.dumps(key_metrics, indent=2)}
    
    Focus on:
    1. What the price and market cap tell us
    2. Why supply metrics matter (inflation/deflation)
    3. What the risk assessment means
    4. How liquidity affects trading
    5. Whether this looks like a good investment opportunity
    
    Keep it conversational and educational, not financial advice.
    """
    
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "meta-llama/llama-3.2-11b-vision-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
        
    except Exception as e:
        return f"Unable to generate explanation: {e}"

# Enhanced tokenomics function
def fetch_enhanced_token_data(coin_id: str, investment_amount: float = 1000) -> Tuple[Dict, str]:
    """
    Fetch comprehensive tokenomics data and AI explanation
    Returns: (token_data_dict, ai_explanation)
    """
    try:
        analyzer = ComprehensiveTokenomics()
        token_data = analyzer.fetch_comprehensive_token_data(coin_id, investment_amount)
        
        if not token_data:
            return None, "Could not fetch token data. Please check the token name/symbol."
        
        # Get AI explanation
        ai_explanation = get_ai_tokenomics_explanation(token_data, st.session_state.get("user_name", "User"))
        
        return token_data, ai_explanation
        
    except Exception as e:
        return None, f"Error in enhanced tokenomics analysis: {e}"

def enhanced_tokenomics_df(token_data: Dict) -> pd.DataFrame:
    """Create organized DataFrame for comprehensive tokenomics display"""
    if not token_data:
        return None
    
    # Organize data into categories
    categories = {
        "🏷️ Basic Information": [
            "Token_Name", "Symbol", "Description", "Website", "Blockchain", "Contract_Address"
        ],
        "💰 Market Data": [
            "Current_Price", "Market_Cap", "Market_Cap_Rank", "Market_Cap_Category", 
            "24h_Volume", "Volume_to_MCap_Ratio", "Liquidity_Score"
        ],
        "📊 Supply Economics": [
            "Circulating_Supply", "Total_Supply", "Max_Supply", "Circulating_Percentage",
            "Supply_Model", "Supply_Inflation_Rate", "Fully_Diluted_Valuation", 
            "FDV_to_MCap_Ratio", "Supply_Distribution"
        ],
        "📈 Price Performance": [
            "Price_Change_1h", "Price_Change_24h", "Price_Change_7d", 
            "Price_Change_30d", "Price_Change_1y", "All_Time_High", 
            "ATH_Date", "Distance_from_ATH", "All_Time_Low", "ATL_Date", "Distance_from_ATL"
        ],
        "🎯 Investment Analysis": [
            "Investment_Tokens", "Risk_Level", "Risk_Score", "Risk_Factors", "Investment_Recommendation"
        ],
        "🌐 Community & Development": [
            "Twitter_Followers", "Reddit_Subscribers", "Telegram_Users", "Social_Media_Score",
            "GitHub_Stars", "GitHub_Forks", "GitHub_Commits_4w", "Development_Activity"
        ],
        "🔍 Technical Details": [
            "Genesis_Date", "Block_Time_Minutes", "Hashing_Algorithm", 
            "Exchange_Count", "Top_Exchange", "Primary_Category"
        ]
    }
    
    # Add historical performance data
    performance_keys = [k for k in token_data.keys() if k.startswith(("Performance_", "CAGR_", "Sharpe_", "Max_Drawdown_", "Avg_Volume_"))]
    if performance_keys:
        categories["📊 Historical Analysis"] = performance_keys
    
    # Create organized dataframe
    organized_data = []
    
    for category, keys in categories.items():
        # Add category header
        organized_data.append({"Category": category, "Metric": "", "Value": ""})
        
        for key in keys:
            if key in token_data:
                # Format the key for display
                display_key = key.replace("_", " ").title()
                value = token_data[key]
                
                organized_data.append({
                    "Category": "",
                    "Metric": display_key,
                    "Value": str(value)
                })
    
    df = pd.DataFrame(organized_data)
    return df

# Update the main tokenomics function call in the original code
def fetch_token_data(coin_id, investment_amount=1000):
    """Legacy function - redirects to enhanced version"""
    token_data, explanation = fetch_enhanced_token_data(coin_id, investment_amount)
    return token_data

def get_theme_css(theme):
    """Generate CSS for professional dark/light mode themes"""
    if theme == "dark":
        return """
        <style>
        /* Global transition for smooth theme switching */
        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
        }
        
        .stApp {
            background: #1a1a1a;
            color: #ffffff !important;
            transition: background-color 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        /* Fix Streamlit header - the white bar at the top */
        header[data-testid="stHeader"],
        .stAppHeader,
        .st-emotion-cache-1eyfjps {
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
            border-bottom: 1px solid #30363d !important;
        }
        
        /* Fix the decoration bar inside header */
        .stDecoration,
        .st-emotion-cache-1dp5vir {
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
        }
        
        /* Fix toolbar area */
        .stAppToolbar,
        .st-emotion-cache-15ecox0 {
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
        }
        
        /* Fix toolbar actions */
        .stToolbarActions,
        .st-emotion-cache-1p1m4ay {
            background: #1a1a1a !important;
        }
        
        /* Style the Deploy button and menu in header */
        button[data-testid="stBaseButton-header"],
        button[data-testid="stBaseButton-headerNoPadding"],
        .st-emotion-cache-usvq0g,
        .st-emotion-cache-1w7bu1y {
            background: #30363d !important;
            color: #ffffff !important;
            border: 1px solid #484f58 !important;
        }
        
        /* Hide or style the main menu */
        .stMainMenu {
            background: #1a1a1a !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-1lcbmhc, section[data-testid="stSidebar"] {
            background: #161b22 !important;
            border-right: 1px solid #30363d;
        }
        
        .css-1d391kg *, .css-1lcbmhc *, section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        /* Nuclear approach for white bar above chat */
        .stApp > div {
            background: #1a1a1a !important;
        }
        
        .stApp > div > div {
            background: #1a1a1a !important;
        }
        
        .stApp > div > div > div {
            background: #1a1a1a !important;
        }
        
        .stApp > div > div > div > div {
            background: #1a1a1a !important;
        }
        
        /* Target all possible main content wrappers */
        .main, 
        .main > div,
        .main > div > div,
        .main > div > div > div,
        div[data-testid="block-container"],
        div[data-testid="stVerticalBlock"],
        div[data-testid="column"] {
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
        }
        
        /* Override any element that might be white */
        .stApp div:not([data-testid="stChatMessage"]):not(.stFileUploader):not(.stButton) {
            background: transparent !important;
        }
        
        /* Specific fix for main container */
        .css-1y4p8pa, .css-12oz5g7, .css-1629p8f {
            background: #1a1a1a !important;
        }
        
        /* Chat messages */
        .stChatMessage {
            background: #21262d !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
            margin: 1rem 0;
            padding: 1rem;
        }
        
        .stChatMessage * {
            color: #ffffff !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 600;
        }
        
        /* Buttons */
        .stButton > button {
            background: #238636 !important;
            color: white !important;
            border: 1px solid #2ea043 !important;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-size: 14px;
        }
        
        .stButton > button:hover {
            background: #2ea043 !important;
        }
        
        /* Theme toggle button - Exact selector targeting */
        button[data-testid="stBaseButton-secondary"][kind="secondary"] {
            background: #30363d !important;
            color: #ffffff !important;
            border: 1px solid #484f58 !important;
            border-radius: 6px !important;
            padding: 0.4rem 0.6rem !important;
            min-width: 42px !important;
            height: 38px !important;
        }
        
        /* Target the specific emotion-cache class if needed */
        .st-emotion-cache-qm7g72 {
            background: #30363d !important;
            color: #ffffff !important;
            border: 1px solid #484f58 !important;
            border-radius: 6px !important;
        }
        
        /* Target the inner markdown container and paragraph */
        button[data-testid="stBaseButton-secondary"] .st-emotion-cache-p7i6r9,
        button[data-testid="stBaseButton-secondary"] .st-emotion-cache-p7i6r9 p {
            color: #ffffff !important;
        }
        
        /* Backup selector using the button structure */
        button[kind="secondary"]:has(div[data-testid="stMarkdownContainer"]) {
            background: #30363d !important;
            color: #ffffff !important;
            border: 1px solid #484f58 !important;
        }
        
        /* Input fields - FIXED for dark mode visibility */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stChatInput > div > div > input {
            background: #21262d !important;
            border: 1px solid #30363d !important;
            color: #ffffff !important;
            border-radius: 6px;
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder,
        .stChatInput > div > div > input::placeholder {
            color: #8b949e !important;
            opacity: 1 !important;
            transition: color 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus, 
        .stTextArea > div > div > textarea:focus, 
        .stChatInput > div > div > input:focus {
            border-color: #388bfd !important;
            box-shadow: 0 0 0 2px rgba(56, 139, 253, 0.3) !important;
        }
        
        /* Chat input styling - Nuclear approach for stubborn Streamlit styling */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] > div > div > div {
            background: #21262d !important;
            background-color: #21262d !important;
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
        }
        
        [data-testid="stChatInput"] input,
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] > div input,
        [data-testid="stChatInput"] > div textarea,
        [data-testid="stChatInput"] > div > div input,
        [data-testid="stChatInput"] > div > div textarea,
        [data-testid="stChatInput"] > div > div > div input,
        [data-testid="stChatInput"] > div > div > div textarea {
            background: #21262d !important;
            background-color: #21262d !important;
            color: #ffffff !important;
            border: none !important;
            border-color: transparent !important;
        }
        
        [data-testid="stChatInput"] input::placeholder,
        [data-testid="stChatInput"] textarea::placeholder {
            color: #8b949e !important;
        }
        
        /* Catch-all for any remaining chat input elements */
        .stApp [data-testid="stChatInput"] * {
            background: #21262d !important;
            color: #ffffff !important;
        }
        
        /* Override any emotion-cache classes that might be interfering */
        div[class*="st-emotion-cache"] input,
        div[class*="st-emotion-cache"] textarea {
            background: #21262d !important;
            color: #ffffff !important;
        }
        
        /* File uploader - FIXED for dark mode */
        .stFileUploader > div {
            background: #21262d !important;
            border: 1px dashed #30363d !important;
            border-radius: 6px;
            color: #ffffff !important;
        }
        
        .stFileUploader * {
            color: #ffffff !important;
        }
        
        /* File uploader button and text */
        .stFileUploader label {
            color: #ffffff !important;
        }
        
        .stFileUploader button {
            background: #30363d !important;
            color: #ffffff !important;
            border: 1px solid #484f58 !important;
        }
        
        /* File uploader drag area */
        .stFileUploader [data-testid="stFileUploaderDropzone"] {
            background: #21262d !important;
            border: 2px dashed #30363d !important;
            color: #ffffff !important;
        }
        
        .stFileUploader [data-testid="stFileUploaderDropzone"] * {
            color: #ffffff !important;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: #238636 !important;
            border: 1px solid #2ea043 !important;
            color: white !important;
            border-radius: 6px;
        }
        
        .stError, .stWarning {
            background: #da3633 !important;
            border: 1px solid #f85149 !important;
            color: white !important;
            border-radius: 6px;
        }
        
        .stInfo {
            background: #1f6feb !important;
            border: 1px solid #388bfd !important;
            color: white !important;
            border-radius: 6px;
        }
        
        /* Tables */
        .stDataFrame {
            background: #21262d !important;
            border-radius: 6px;
            border: 1px solid #30363d;
        }
        
        .stDataFrame * {
            color: #ffffff !important;
            background: #21262d !important;
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background: #21262d !important;
            border: 1px solid #30363d !important;
            border-radius: 6px !important;
            padding: 1rem;
        }
        
        div[data-testid="metric-container"] * {
            color: #ffffff !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: #21262d !important;
            color: #ffffff !important;
        }
        
        .streamlit-expanderContent {
            background: #161b22 !important;
            border: 1px solid #30363d !important;
        }
        
        /* Select boxes */
        .stSelectbox * {
            color: #ffffff !important;
            background: #21262d !important;
        }
        
        /* Select box dropdown */
        .stSelectbox > div > div {
            background: #21262d !important;
            border: 1px solid #30363d !important;
        }
        
        .stSelectbox option {
            background: #21262d !important;
            color: #ffffff !important;
        }
        
        /* Markdown text */
        .stMarkdown * {
            color: #ffffff !important;
        }
        
        /* Labels for inputs */
        label {
            color: #ffffff !important;
        }
        
        /* Progress bars */
        .stProgress > div > div {
            background: #238636 !important;
        }
        
        /* Sliders */
        .stSlider * {
            color: #ffffff !important;
        }
        
        /* Number input */
        .stNumberInput > div > div > input {
            background: #21262d !important;
            border: 1px solid #30363d !important;
            color: #ffffff !important;
        }
        
        /* Date input */
        .stDateInput > div > div > input {
            background: #21262d !important;
            border: 1px solid #30363d !important;
            color: #ffffff !important;
        }
        
        /* Time input */
        .stTimeInput > div > div > input {
            background: #21262d !important;
            border: 1px solid #30363d !important;
            color: #ffffff !important;
        }
        
        /* Code blocks */
        .stCodeBlock {
            background: #0d1117 !important;
            border: 1px solid #30363d !important;
        }
        
        .stCodeBlock * {
            color: #e6edf3 !important;
        }
        </style>
        """
    else:  # light theme
        return """
        <style>
        /* Global transition for smooth theme switching */
        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
        }
        
        .stApp {
            background: #ffffff;
            color: #1a202c !important;
            transition: background-color 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        /* Global text color */
        .stApp * {
            color: #1a202c !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-1lcbmhc, section[data-testid="stSidebar"] {
            background: #f7fafc !important;
            border-right: 1px solid #e2e8f0;
        }
        
        .css-1d391kg *, .css-1lcbmhc *, section[data-testid="stSidebar"] * {
            color: #1a202c !important;
        }
        
        /* Main content area */
        .main .block-container {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
        }
        
        /* Chat messages */
        .stChatMessage {
            background: rgba(247, 250, 252, 0.8) !important;
            border: 1px solid #cbd5e0 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
            margin: 1rem 0;
            padding: 1rem;
        }
        
        /* User messages */
        div[data-testid="stChatMessageContainer"]:has(div[data-testid="chatAvatarIcon-user"]) {
            background: linear-gradient(135deg, #3182ce 0%, #2b77cb 100%) !important;
            border: 1px solid #4299e1 !important;
            color: white !important;
        }
        
        /* Assistant messages */
        div[data-testid="stChatMessageContainer"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
            background: linear-gradient(135deg, #38a169 0%, #48bb78 100%) !important;
            border: 1px solid #68d391 !important;
            color: white !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #2d3748 !important;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #3182ce !important;
            background: linear-gradient(90deg, #3182ce, #4299e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3182ce 0%, #2b77cb 100%) !important;
            color: white !important;
            border: 1px solid #4299e1 !important;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(49, 130, 206, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2c5aa0 0%, #2a69ac 100%) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(49, 130, 206, 0.4);
        }
        
        /* Input fields */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stChatInput > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid #e2e8f0 !important;
            color: #2d3748 !important;
            border-radius: 6px;
        }
        
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus, .stChatInput > div > div > input:focus {
            border-color: #3182ce !important;
            box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.2) !important;
        }
        
        /* File uploader */
        .stFileUploader > div {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px dashed #e2e8f0 !important;
            border-radius: 8px;
            padding: 2rem;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: linear-gradient(135deg, #38a169 0%, #48bb78 100%) !important;
            border: 1px solid #68d391 !important;
            color: white !important;
            border-radius: 8px;
        }
        
        .stError {
            background: linear-gradient(135deg, #e53e3e 0%, #fc8181 100%) !important;
            border: 1px solid #feb2b2 !important;
            color: white !important;
            border-radius: 8px;
        }
        
        /* Tables */
        .stDataFrame {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%) !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 1rem;
        }
        
        /* Toggle switch */
        .stToggle > label {
            color: #2d3748 !important;
            font-weight: 500;
        }
        </style>
        """

def manage_history_length(history_list):
    if not history_list:
        return []
    system_msg = None
    if history_list and history_list[0].get("role") == "system":
        system_msg = history_list[0]
        temp = history_list[1:]
    else:
        temp = history_list
    if len(temp) > MAX_HISTORY_MESSAGES - 1:
        temp = temp[-(MAX_HISTORY_MESSAGES - 1):]
    if system_msg:
        return [system_msg] + temp
    return temp

def flatten_conversation_for_api(conv):
    msgs = []
    for m in conv:
        role = m.get("role", "user")
        if role == "system":
            msgs.append({"role":"system", "content": m.get("content", "")})
        elif role == "user":
            msgs.append({"role":"user", "content": m.get("content", "")})
        elif role == "assistant":
            kind = m.get("kind", "text")
            if kind == "tokenomics":
                # Include both data summary and AI explanation
                explanation = m.get("ai_explanation", "")
                data_summary = f"Comprehensive tokenomics analysis completed for {m.get('token_name', 'token')}."
                content = f"{data_summary}\n\nAI Explanation: {explanation}" if explanation else data_summary
                msgs.append({"role":"assistant", "content": content})
            elif kind == "prediction":
                data = m.get("data", {})
                text = f"Prediction for {data.get('symbol','')}: Bias {data.get('bias','')}, Strength {data.get('strength','')}\nPlan:\n{data.get('plan','')}"
                msgs.append({"role":"assistant", "content": text})
            elif kind == "news":
                headlines = m.get("data", [])
                text = "News headlines:\n" + "\n".join(headlines)
                msgs.append({"role":"assistant", "content": text})
            else:
                msgs.append({"role":"assistant", "content": m.get("content", "")})
    return msgs

# ---------------------------
# Market news
# ---------------------------
def fetch_market_news():
    if not NEWS_API_KEY:
        return ["[Error] NEWS_API_KEY not configured in Streamlit secrets."]
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "finance OR bitcoin OR stock market OR federal reserve OR inflation",
        "from": datetime.now().strftime("%Y-%m-%d"),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        return [f"- {a['title']} ({a['source']['name']})" for a in data.get("articles", [])]
    except Exception as e:
        return [f"[Error fetching news] {e}"]

# ---------------------------
# AI / Chart calls
# ---------------------------
def ask_nunno(messages):
    if not AI_API_KEY:
        return "[Error] AI_API_KEY not configured."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-3.2-11b-vision-instruct",
        "messages": messages
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[AI Error] {e}"

def analyze_chart(image_b64):
    if not AI_API_KEY:
        return "[Error] AI_API_KEY not configured."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-3.2-11b-vision-instruct",
        "messages": [{
            "role": "user",
            "content": [
                {"type":"text", "text":"You're an expert trading analyst. Analyze this chart: identify trend, SR, patterns, and predict the next move."},
                {"type":"image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        }],
        "max_tokens": 1000
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Chart API Error] {e}"

def is_tokenomics_request(text):
    """Check if request is specifically about tokenomics"""
    tokenomics_specific = [
        "tokenomics", "supply", "fdv", "market cap", "circulating", 
        "should i invest", "inflation rate", "token economics", "coin analysis",
        "comprehensive analysis", "full analysis", "detailed analysis"
    ]
    text_lower = text.lower()
    
    # Check for explicit tokenomics keywords
    has_tokenomics = any(keyword in text_lower for keyword in tokenomics_specific)
    
    # Check for prediction keywords that should override tokenomics
    prediction_override = any(keyword in text_lower for keyword in [
        "predict", "forecast", "next move", "price prediction", 
        "where will", "target price", "technical analysis", "trend"
    ])
    
    # If it has prediction keywords, it's NOT tokenomics
    if prediction_override:
        return False
        
    return has_tokenomics

def is_prediction_request(text):
    """Check if request is specifically about predictions/technical analysis"""
    prediction_keywords = [
        "predict", "forecast", "next move", "price prediction", 
        "where will", "target price", "technical analysis", "trend",
        "analysis", "chart", "bullish", "bearish", "support", "resistance"
    ]
    return any(keyword in text.lower() for keyword in prediction_keywords)

def suggest_similar_tokens(user_input):
    try:
        res = requests.get("https://api.coingecko.com/api/v3/coins/list", timeout=10)
        res.raise_for_status()
        coin_list = res.json()
        coin_ids = [coin['id'] for coin in coin_list]
        best = process.extract(user_input.lower(), coin_ids, limit=5)
        return [b[0] for b in best if b[1] > 60]
    except Exception:
        return []

# ---------------------------
# Streamlit UI start
# ---------------------------
st.set_page_config(page_title="Nunno AI", page_icon="🧠", layout="wide")

# Theme state management
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# session state initialization
if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role":"system", "content": SYSTEM_PROMPT.format(user_name="User", user_age="N/A")}]
if "user_name" not in st.session_state:
    st.session_state.user_name = "User"
if "user_age" not in st.session_state:
    st.session_state.user_age = "N/A"
if "uploaded_b64" not in st.session_state:
    st.session_state.uploaded_b64 = None
if "chart_analysis" not in st.session_state:
    st.session_state.chart_analysis = None

# sidebar
with st.sidebar:
    # Header with simple theme toggle
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header("Profile & Controls")
    with col2:
        # Simple toggle button
        if st.button("◐", help="Toggle theme", key="theme_toggle"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    
    st.session_state.user_name = st.text_input("Your name", st.session_state.user_name)
    st.session_state.user_age = st.text_input("Your age (optional)", st.session_state.user_age)
    if st.button("Start New Chat"):
        st.session_state.conversation = [{"role":"system", "content": SYSTEM_PROMPT.format(user_name=st.session_state.user_name, user_age=st.session_state.user_age)}]
        st.rerun()

    st.markdown("---")
    st.subheader("Upload Chart (optional)")
    uploaded = st.file_uploader("Upload trading chart image (png/jpg)", type=["png","jpg","jpeg"])
    if uploaded is not None:
        st.session_state.uploaded_b64 = base64.b64encode(uploaded.read()).decode("utf-8")
        st.success("Chart uploaded and ready for analysis.")
        
        # Add analyze button when chart is uploaded
        if st.button("🔍 Analyze Chart", key="analyze_chart_btn"):
            with st.spinner("Analyzing chart..."):
                result = analyze_chart(st.session_state.uploaded_b64)
                st.session_state.chart_analysis = result
            st.rerun()

    st.markdown("---")
    st.subheader("Quick Examples")
    if st.button("Comprehensive Bitcoin Analysis ($1000)"):
        st.session_state.conversation.append({"role":"user","content":"Give me comprehensive tokenomics analysis for Bitcoin with $1000 investment"})
        st.rerun()
    if st.button("Analyze Ethereum Tokenomics"):
        st.session_state.conversation.append({"role":"user","content":"Full tokenomics analysis for Ethereum"})
        st.rerun()
    if st.button("What's happening in the market?"):
        st.session_state.conversation.append({"role":"user","content":"What's happening in the market?"})
        st.rerun()
    if st.button("Predict BTC price movement"):
        st.session_state.conversation.append({"role":"user","content":"Predict BTC price movement 15m"})
        st.rerun()

# main layout
col1, col2 = st.columns([3,1])

with col1:
    st.header("Chat")
    # render conversation
    for msg in st.session_state.conversation:
        role = msg.get("role","user")
        if role == "system":
            continue  # Don't show system messages
        elif role == "user":
            with st.chat_message("user"):
                st.markdown(msg.get("content",""))
        elif role == "assistant":
            kind = msg.get("kind","text")
            if kind == "tokenomics":
                with st.chat_message("assistant"):
                    st.markdown("📊 **Comprehensive Tokenomics Analysis**")
                    
                    # Display the organized dataframe
                    df = enhanced_tokenomics_df(msg.get("data",{}))
                    if df is not None:
                        # Display each category as an expander
                        current_category = None
                        category_data = []
                        
                        for _, row in df.iterrows():
                            if row["Category"] and row["Category"] != current_category:
                                # Display previous category if exists
                                if current_category and category_data:
                                    with st.expander(current_category, expanded=True):
                                        category_df = pd.DataFrame(category_data)
                                        st.table(category_df[["Metric", "Value"]])
                                
                                # Start new category
                                current_category = row["Category"]
                                category_data = []
                            elif row["Metric"]:  # Only add rows with actual metrics
                                category_data.append({"Metric": row["Metric"], "Value": row["Value"]})
                        
                        # Display final category
                        if current_category and category_data:
                            with st.expander(current_category, expanded=True):
                                category_df = pd.DataFrame(category_data)
                                st.table(category_df[["Metric", "Value"]])
                    
                    # Display risk assessment prominently
                    data = msg.get("data", {})
                    risk_level = data.get("Risk_Level", "")
                    if "EXTREMELY HIGH" in risk_level or "HIGH RISK" in risk_level:
                        st.error(f"⚠️ {risk_level}")
                    elif "MODERATE" in risk_level:
                        st.warning(f"⚡ {risk_level}")
                    else:
                        st.success(f"✅ {risk_level}")
                    
                    # Display AI explanation
                    ai_explanation = msg.get("ai_explanation", "")
                    if ai_explanation:
                        st.markdown("### 🤖 AI Explanation")
                        st.markdown(ai_explanation)
                    
                    # Display investment recommendation prominently
                    recommendation = data.get("Investment_Recommendation", "")
                    if recommendation:
                        st.info(f"💡 **Investment Recommendation:** {recommendation}")
                        
            elif kind == "prediction":
                with st.chat_message("assistant"):
                    data = msg.get("data",{})
                    bias = data.get("bias","")
                    strength = data.get("strength",0) or 0
                    symbol = data.get("symbol","")
                    tf = data.get("tf","")
                    
                    # Display prediction header
                    if isinstance(bias, str) and "bullish" in bias.lower():
                        st.success(f"🎯 {symbol} ({tf}) — Bias: {bias} ({strength:.1f}% confidence)")
                    elif isinstance(bias, str) and "bearish" in bias.lower():
                        st.error(f"🎯 {symbol} ({tf}) — Bias: {bias} ({strength:.1f}% confidence)")
                    else:
                        st.info(f"🎯 {symbol} ({tf}) — Bias: {bias} ({strength:.1f}% confidence)")

                    # Display confluences with better formatting
                    confluences = data.get("confluences", {})
                    if confluences:
                        st.markdown("### 📊 Confluence Analysis")
                        
                        # Bullish confluences
                        if confluences.get("bullish"):
                            st.markdown("#### 🟢 Bullish Signals")
                            for i, conf in enumerate(confluences["bullish"], 1):
                                with st.expander(f"{i}. {conf.get('indicator', 'Signal')} [{conf.get('strength', 'Medium')}]"):
                                    st.markdown(f"**Condition:** {conf.get('condition', 'N/A')}")
                                    st.markdown(f"**Implication:** {conf.get('implication', 'N/A')}")
                                    st.markdown(f"**Timeframe:** {conf.get('timeframe', 'N/A')}")
                        
                        # Bearish confluences
                        if confluences.get("bearish"):
                            st.markdown("#### 🔴 Bearish Signals")
                            for i, conf in enumerate(confluences["bearish"], 1):
                                with st.expander(f"{i}. {conf.get('indicator', 'Signal')} [{conf.get('strength', 'Medium')}]"):
                                    st.markdown(f"**Condition:** {conf.get('condition', 'N/A')}")
                                    st.markdown(f"**Implication:** {conf.get('implication', 'N/A')}")
                                    st.markdown(f"**Timeframe:** {conf.get('timeframe', 'N/A')}")
                        
                        # Neutral signals
                        if confluences.get("neutral"):
                            st.markdown("#### 🟡 Neutral/Mixed Signals")
                            for i, conf in enumerate(confluences["neutral"], 1):
                                with st.expander(f"{i}. {conf.get('indicator', 'Signal')} [{conf.get('strength', 'Medium')}]"):
                                    st.markdown(f"**Condition:** {conf.get('condition', 'N/A')}")
                                    st.markdown(f"**Implication:** {conf.get('implication', 'N/A')}")
                                    st.markdown(f"**Timeframe:** {conf.get('timeframe', 'N/A')}")

                    # Display trading plan
                    plan = data.get("plan","")
                    if plan:
                        st.markdown("### 📋 Trading Plan")
                        st.text(plan)
                        
                    # Display key levels if available
                    latest_data = data.get("latest_data")
                    if latest_data:
                        st.markdown("### 📊 Key Levels")
                        cols = st.columns(2)
                        with cols[0]:
                            st.metric("Current Price", f"${latest_data.get('Close', 0):.4f}")
                            st.metric("EMA 21", f"${latest_data.get('EMA_21', 0):.4f}")
                            st.metric("EMA 50", f"${latest_data.get('EMA_50', 0):.4f}")
                        with cols[1]:
                            st.metric("RSI", f"{latest_data.get('RSI_14', 0):.1f}")
                            st.metric("BB Upper", f"${latest_data.get('BB_Upper', 0):.4f}")
                            st.metric("BB Lower", f"${latest_data.get('BB_Lower', 0):.4f}")
                    
                    note = msg.get("content","")
                    if note:
                        st.markdown("### 💡 Additional Notes")
                        st.markdown(note)
                        
            elif kind == "montecarlo":
                with st.chat_message("assistant"):
                    st.markdown("🧪 **Monte Carlo Simulation**")
                    st.markdown(msg.get("content",""))
            elif kind == "news":
                with st.chat_message("assistant"):
                    st.markdown("📰 **Market News**")
                    for h in msg.get("data",[]):
                        st.markdown(h)
                    if msg.get("content"):
                        st.markdown("**AI Explanation:**")
                        st.markdown(msg.get("content"))
            elif kind == "chart":
                with st.chat_message("assistant"):
                    st.markdown("📷 **Chart Analysis**")
                    st.markdown(msg.get("content",""))
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg.get("content",""))

    # Chat input
    prompt = st.chat_input("Ask Nunno about trading, tokenomics, predictions, news...")
    if prompt:
        st.session_state.conversation.append({"role":"user","content":prompt})
        lower = prompt.lower()

        assistant_entry = {"role":"assistant", "kind":"text", "content":""}

        # PREDICTION - Check this FIRST and make it more specific
        if is_prediction_request(prompt):
            if betterpredictormodule is None:
                assistant_entry["content"] = "Prediction features require the local module 'betterpredictormodule'. It's not available on this server."
            else:
                # Extract symbol
                symbol = "BTCUSDT"
                symbol_mappings = {
                    "btc": "BTCUSDT", "bitcoin": "BTCUSDT", "xbt": "BTCUSDT",
                    "eth": "ETHUSDT", "ethereum": "ETHUSDT",
                    "bnb": "BNBUSDT", "binance": "BNBUSDT",
                    # Layer 1s
                    "sol": "SOLUSDT", "solana": "SOLUSDT",
                    "ada": "ADAUSDT", "cardano": "ADAUSDT",
                    "avax": "AVAXUSDT", "avalanche": "AVAXUSDT",
                    "dot": "DOTUSDT", "polkadot": "DOTUSDT",
                    "atom": "ATOMUSDT", "cosmos": "ATOMUSDT",
                    "near": "NEARUSDT", "near protocol": "NEARUSDT",
                    "algo": "ALGOUSDT", "algorand": "ALGOUSDT",
                    "apt": "APTUSDT", "aptos": "APTUSDT",
                    "sui": "SUIUSDT", "sui network": "SUIUSDT",
                    # Layer 2s / Scaling
                    "matic": "MATICUSDT", "polygon": "MATICUSDT",
                    "op": "OPUSDT", "optimism": "OPUSDT",
                    "arb": "ARBUSDT", "arbitrum": "ARBUSDT",
                    "imx": "IMXUSDT", "immutable": "IMXUSDT",
                    # Meme Coins
                    "doge": "DOGEUSDT", "dogecoin": "DOGEUSDT",
                    "shib": "SHIBUSDT", "shiba": "SHIBUSDT", "shiba inu": "SHIBUSDT",
                    "pepe": "PEPEUSDT", "pepe coin": "PEPEUSDT",
                    "floki": "FLOKIUSDT", "floki inu": "FLOKIUSDT",
                    # Stablecoins
                    "usdt": "USDTUSDT", "tether": "USDTUSDT",
                    "usdc": "USDCUSDT", "usd coin": "USDCUSDT",
                    "dai": "DAIUSDT",
                    "busd": "BUSDUSDT", "binance usd": "BUSDUSDT",
                    "tusd": "TUSDUSDT", "trueusd": "TUSDUSDT",
                    # Other Majors & DeFi
                    "xrp": "XRPUSDT", "ripple": "XRPUSDT",
                    "ltc": "LTCUSDT", "litecoin": "LTCUSDT",
                    "link": "LINKUSDT", "chainlink": "LINKUSDT",
                    "uni": "UNIUSDT", "uniswap": "UNIUSDT",
                    "aave": "AAVEUSDT",
                    "comp": "COMPUSDT", "compound": "COMPUSDT",
                    "sand": "SANDUSDT", "sandbox": "SANDUSDT",
                    "mana": "MANAUSDT", "decentraland": "MANAUSDT",
                    "axs": "AXSUSDT", "axie": "AXSUSDT",
                    "rndr": "RNDRUSDT", "render": "RNDRUSDT",
                    "gala": "GALAUSDT",
                    "fil": "FILUSDT", "filecoin": "FILUSDT",
                    "icp": "ICPUSDT", "internet computer": "ICPUSDT",
                    "hbar": "HBARUSDT", "hedera": "HBARUSDT",
                }
                
                for key, val in symbol_mappings.items():
                    if key in lower:
                        symbol = val
                        break
                
                # Extract timeframe
                tf = "15m"
                tf_mappings = {
                    "1m": "1m", "1 minute": "1m", "1min": "1m",
                    "5m": "5m", "5 minute": "5m", "5min": "5m", 
                    "15m": "15m", "15 minute": "15m", "15min": "15m",
                    "1h": "1h", "1 hour": "1h", "1hr": "1h", "hourly": "1h",
                    "4h": "4h", "4 hour": "4h", "4hr": "4h",
                    "1d": "1d", "daily": "1d", "day": "1d"
                }
                
                for key, val in tf_mappings.items():
                    if key in lower:
                        tf = val
                        break
                
                try:
                    analyzer = betterpredictormodule.TradingAnalyzer()
                    df = analyzer.fetch_binance_ohlcv(symbol=symbol, interval=tf, limit=1000)
                    df = analyzer.add_comprehensive_indicators(df)
                    confluences, latest = analyzer.generate_comprehensive_analysis(df)
                    bias, strength = analyzer.calculate_confluence_strength(confluences)
                    
                    # Capture trading plan output
                    old_stdout = io.StringIO()
                    backup = sys.stdout
                    try:
                        sys.stdout = old_stdout
                        betterpredictormodule.generate_trading_plan(confluences, latest, bias, strength)
                    finally:
                        sys.stdout = backup
                    plan_text = old_stdout.getvalue()
                    
                    assistant_entry["kind"] = "prediction"
                    assistant_entry["data"] = {
                        "symbol": symbol,
                        "tf": tf,
                        "bias": bias,
                        "strength": strength,
                        "confluences": confluences,
                        "plan": plan_text,
                        "latest_data": latest.to_dict() if latest is not None else None
                    }
                    assistant_entry["content"] = f"Completed technical analysis for {symbol} on {tf} timeframe."
                    
                except Exception as e:
                    assistant_entry["content"] = f"Prediction error: {e}"

        # ENHANCED TOKENOMICS - now comes AFTER prediction check
        elif is_tokenomics_request(prompt):
            # Extract investment amount
            investment = 1000
            match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', prompt)
            if match:
                investment = float(match.group(1).replace(',', ''))
            
            # Extract coin/token
            coin = "bitcoin"
            common_coins = {
                "btc": "bitcoin", "bitcoin": "bitcoin",
                "eth": "ethereum", "ethereum": "ethereum",
                "ada": "cardano", "cardano": "cardano",
                "sol": "solana", "solana": "solana",
                "doge": "dogecoin", "dogecoin": "dogecoin",
                "shib": "shiba-inu", "shiba": "shiba-inu",
                "matic": "polygon", "polygon": "polygon",
                "avax": "avalanche-2", "avalanche": "avalanche-2",
                "dot": "polkadot", "polkadot": "polkadot",
                "link": "chainlink", "chainlink": "chainlink",
                "uni": "uniswap", "uniswap": "uniswap",
                "xrp": "ripple", "ripple": "ripple",
                "ltc": "litecoin", "litecoin": "litecoin",
                "bnb": "binancecoin", "binance": "binancecoin",
                "usdt": "tether", "tether": "tether",
                "usdc": "usd-coin", "steth": "staked-ether",
                "ton": "the-open-network", "trx": "tron",
                "avax": "avalanche-2", "shib": "shiba-inu",
                "wbtc": "wrapped-bitcoin", "leo": "leo-token",
                "pepe": "pepe", "near": "near", "dai": "dai",
                "kas": "kaspa", "icp": "internet-computer",
                "apt": "aptos", "pol": "polymath",
                "render": "render-token", "arb": "arbitrum",
                "vechain": "vechain", "vet": "vechain",
                "algo": "algorand", "imx": "immutable-x",
                "op": "optimism", "inj": "injective-protocol",
                "fil": "filecoin", "hbar": "hedera-hashgraph",
                "sui": "sui", "atom": "cosmos",
                "grt": "the-graph", "rune": "thorchain",
                "sei": "sei-network", "tia": "celestia"
            }
            
            for key, val in common_coins.items():
                if key in lower:
                    coin = val
                    break
            
            # If no common coin found, try fuzzy matching
            if coin == "bitcoin" and not any(k in lower for k in common_coins.keys()):
                tokens = re.findall(r'\b([a-z]{2,10})\b', lower)
                if tokens:
                    suggestions = suggest_similar_tokens(tokens[0])
                    if suggestions:
                        coin = suggestions[0]
            
            # Use enhanced tokenomics function
            with st.spinner("Fetching comprehensive tokenomics data..."):
                token_data, ai_explanation = fetch_enhanced_token_data(coin, investment)
            
            if token_data:
                assistant_entry["kind"] = "tokenomics"
                assistant_entry["data"] = token_data
                assistant_entry["ai_explanation"] = ai_explanation
                assistant_entry["token_name"] = token_data.get("Token_Name", "Unknown")
                assistant_entry["content"] = f"Comprehensive tokenomics analysis completed for {token_data.get('Token_Name', 'the token')} with ${investment:,} investment."
            else:
                assistant_entry["content"] = f"Sorry, couldn't find comprehensive tokenomics data for '{coin}'. Try a different coin name or symbol."

        # NEWS
        elif "news" in lower or "market" in lower or "happening" in lower:
            headlines = fetch_market_news()
            assistant_entry["kind"] = "news"
            assistant_entry["data"] = headlines
            if not any("Error" in h for h in headlines):
                # Get AI summary of news
                news_text = "\n".join(headlines)
                ai_messages = flatten_conversation_for_api(st.session_state.conversation)
                ai_messages.append({"role": "user", "content": f"Explain these news headlines in simple terms for a beginner trader:\n{news_text}"})
                ai_response = ask_nunno(ai_messages)
                assistant_entry["content"] = ai_response

        # MONTE CARLO
        elif ("monte carlo" in lower or "simulation" in lower) and simulate_trades:
            try:
                results = simulate_trades(num_simulations=1000)
                summary = monte_carlo_summary(results)
                assistant_entry["kind"] = "montecarlo"
                assistant_entry["content"] = summary
            except Exception as e:
                assistant_entry["content"] = f"Monte Carlo simulation error: {e}"

        # DEFAULT AI CHAT
        else:
            ai_messages = flatten_conversation_for_api(st.session_state.conversation)
            ai_messages.append({"role": "user", "content": prompt})
            ai_response = ask_nunno(ai_messages)
            assistant_entry["content"] = ai_response

        st.session_state.conversation.append(assistant_entry)
        st.session_state.conversation = manage_history_length(st.session_state.conversation)
        st.rerun()

with col2:
    st.subheader("Quick Info")
    
    # Module Status
    st.markdown("**🧩 Features**")
    if betterpredictormodule:
        st.success("✅ Predictions Available")
    else:
        st.warning("⚠️ Predictions Module Missing")
        
    if simulate_trades:
        st.success("✅ Monte Carlo Available")
    else:
        st.warning("⚠️ Monte Carlo Module Missing")
    
    # Upload status
    if st.session_state.uploaded_b64:
        st.success("📷 Chart Ready for Analysis")
    else:
        st.info("📷 No Chart Uploaded")
        
    st.markdown("---")
    st.markdown("**💡 Tips**")
    st.markdown("- Use specific coin names (BTC, ETH, ADA)")
    st.markdown("- Include timeframes (15m, 1h, 4h, 1d)")
    st.markdown("- Ask for predictions, tokenomics, or news")
    st.markdown("- Upload charts for technical analysis")
    st.markdown("- Try 'comprehensive analysis' for full tokenomics")
    
    # Chart Analysis Results Section
    if st.session_state.chart_analysis:
        st.markdown("---")
        st.markdown("**📈 Chart Analysis**")
        with st.expander("View Analysis", expanded=True):
            st.markdown(st.session_state.chart_analysis)
            if st.button("Clear Analysis", key="clear_analysis"):
                st.session_state.chart_analysis = None
                st.rerun()


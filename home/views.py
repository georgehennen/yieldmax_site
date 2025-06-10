from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import date, timedelta
import yfinance as yf
import pandas as pd
from django.contrib import messages
from .models import Lot, UserProfile 
from .forms import UserRegisterForm, GoalForm, LotForm, FinancialSettingsForm, UserUpdateForm
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict 
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.views.decorators.http import require_POST
from django.utils import timezone

class DecimalEncoder(json.JSONEncoder):
    """ Custom JSON encoder for Decimal and date types. """
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, pd.Timestamp)): 
             return o.isoformat()
        return super().default(o)

def register(request):
    """ Handles user registration. """
    if request.user.is_authenticated:
        return redirect('home:dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    """ Handles user profile updates. """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('home:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {'u_form': u_form}
    return render(request, 'home/profile.html', context)

@login_required
def get_portfolio_data_api(request):
    """
    API endpoint to fetch, calculate, and return all portfolio data.
    Caches the result to improve performance.
    """
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    marginal_tax_rate_decimal = profile.marginal_tax_rate if profile.marginal_tax_rate is not None else Decimal(0)

    CACHE_KEY = f'portfolio_data_{user.id}'
    CACHE_TIMEOUT = 900 # 15 minutes

    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        return JsonResponse(cached_data, encoder=DecimalEncoder, safe=False)

    lots = Lot.objects.filter(user=user).order_by("date_purchased")
    if not lots.exists():
        return JsonResponse({"has_lots": False})

    tickers_list = list(lots.values_list("ticker", flat=True).distinct())
    ticker_data_yf = {}
    if tickers_list:
        try:
            # Use yf.download for more efficient bulk fetching for current prices
            data = yf.download(tickers_list, period="5d", progress=False)
            for tkr_symbol in tickers_list:
                tkr_obj = yf.Ticker(tkr_symbol)
                try:
                    # Get latest price from the downloaded bulk data
                    latest_price = data['Close'][tkr_symbol].dropna().iloc[-1]
                    dividends_series_yf = tkr_obj.dividends
                    if not dividends_series_yf.empty and not pd.api.types.is_datetime64_any_dtype(dividends_series_yf.index):
                        try: dividends_series_yf.index = pd.to_datetime(dividends_series_yf.index)
                        except Exception: dividends_series_yf = pd.Series(dtype=float)
                    if pd.api.types.is_datetime64_any_dtype(dividends_series_yf.index) and dividends_series_yf.index.tz is not None:
                        dividends_series_yf.index = dividends_series_yf.index.tz_localize(None)
                    ticker_data_yf[tkr_symbol] = {"price": latest_price if latest_price is not None else 0, "divs": dividends_series_yf}
                except Exception: 
                    ticker_data_yf[tkr_symbol] = {"price": 0, "divs": pd.Series(dtype=float)}
        except Exception as e:
            print(f"Error fetching yfinance data: {e}")
            return JsonResponse({'error': 'Failed to fetch market data.'}, status=500)
    
    processed_lots_data = []; summary_data_per_ticker = {} 
    monthly_dividend_estimate_actual_received = Decimal(0)
    today_date_for_divs = now().date(); twenty_eight_days_ago_for_divs = today_date_for_divs - timedelta(days=28)
    aggregated_dividends_by_date = defaultdict(lambda: defaultdict(Decimal))
    
    for lot_item in lots: 
        tkr_symbol = lot_item.ticker; purchase_date = lot_item.date_purchased
        shares_count = Decimal(str(lot_item.shares)); cost_per_share = Decimal(str(lot_item.price))
        current_ticker_info = ticker_data_yf.get(tkr_symbol, {"price": Decimal(0), "divs": pd.Series(dtype=float)})
        current_price = Decimal(str(current_ticker_info.get("price", 0)))
        dividends_series = current_ticker_info.get("divs", pd.Series(dtype=float))
        
        divs_after_purchase_sum_total_for_lot = Decimal(0)
        if not dividends_series.empty and pd.api.types.is_datetime64_any_dtype(dividends_series.index):
            normalized_index_date_total = dividends_series.index.normalize().date
            divs_after_purchase_total_series = dividends_series[normalized_index_date_total > purchase_date]
            divs_after_purchase_sum_total_for_lot = Decimal(str(divs_after_purchase_total_series.sum()))
            for div_date, div_amount in divs_after_purchase_total_series.items():
                if isinstance(div_date, pd.Timestamp) and div_amount > 0:
                    week_start_date = (div_date - pd.to_timedelta(div_date.weekday(), unit='D')).strftime('%Y-%m-%d')
                    dividend_value_for_this_payment_on_lot = Decimal(str(div_amount)) * shares_count
                    aggregated_dividends_by_date[week_start_date][tkr_symbol] += dividend_value_for_this_payment_on_lot
        dividends_received_for_lot_historical = divs_after_purchase_sum_total_for_lot * shares_count
        divs_last_28_days_for_lot_sum = Decimal(0)
        if not dividends_series.empty and pd.api.types.is_datetime64_any_dtype(dividends_series.index):
            normalized_index_date_28day = dividends_series.index.normalize().date
            eligible_dividend_dates = (normalized_index_date_28day >= twenty_eight_days_ago_for_divs) & (normalized_index_date_28day > purchase_date)
            divs_last_28_days_series = dividends_series[eligible_dividend_dates]
            divs_last_28_days_for_lot_sum = Decimal(str(divs_last_28_days_series.sum()))
        monthly_dividend_estimate_actual_received += divs_last_28_days_for_lot_sum * shares_count
        current_value_of_lot = shares_count * current_price
        invested_amount_for_lot = shares_count * cost_per_share
        nav_return_for_lot = ((current_value_of_lot - invested_amount_for_lot) / invested_amount_for_lot * Decimal(100)) if invested_amount_for_lot else Decimal(0)
        
        after_tax_divs_for_lot = dividends_received_for_lot_historical * (Decimal(1) - marginal_tax_rate_decimal)
        total_return_for_lot_perc = ((current_value_of_lot - invested_amount_for_lot + after_tax_divs_for_lot) / invested_amount_for_lot * 100) if invested_amount_for_lot > 0 else Decimal(0)
        
        processed_lots_data.append({"id": lot_item.id, "ticker": tkr_symbol, "purchase_date": purchase_date, "shares": shares_count, "price_paid": cost_per_share, "total_cost": invested_amount_for_lot, "dividends_received": dividends_received_for_lot_historical, "current_price": current_price, "current_value": current_value_of_lot, "nav_return": nav_return_for_lot, "total_return_lot": total_return_for_lot_perc})
        
        if tkr_symbol not in summary_data_per_ticker: summary_data_per_ticker[tkr_symbol] = {"shares": Decimal(0), "invested": Decimal(0), "value": Decimal(0), "dividends_received_total_ticker": Decimal(0), "price": current_price}
        summary_data_per_ticker[tkr_symbol]["shares"] += shares_count
        summary_data_per_ticker[tkr_symbol]["invested"] += invested_amount_for_lot
        summary_data_per_ticker[tkr_symbol]["value"] += current_value_of_lot
        summary_data_per_ticker[tkr_symbol]["dividends_received_total_ticker"] += dividends_received_for_lot_historical
    
    total_invested = sum(v["invested"] for v in summary_data_per_ticker.values())
    portfolio_value = sum(v["value"] for v in summary_data_per_ticker.values())
    total_dividends_received = sum(v["dividends_received_total_ticker"] for v in summary_data_per_ticker.values())
    
    portfolio_summary_table_data = []
    for tkr, v_data in summary_data_per_ticker.items():
        avg_cost = v_data["invested"] / v_data["shares"] if v_data["shares"] else Decimal(0)
        nav_return_ticker = (v_data["value"] - v_data["invested"]) / v_data["invested"] * Decimal(100) if v_data["invested"] else Decimal(0)
        portfolio_percentage = v_data["value"] / portfolio_value * Decimal(100) if portfolio_value else Decimal(0)
        ticker_after_tax_divs = v_data["dividends_received_total_ticker"] * (Decimal(1) - marginal_tax_rate_decimal)
        percent_to_house_money_ticker = (ticker_after_tax_divs / v_data["invested"] * 100) if v_data["invested"] > 0 else Decimal(0)
        total_return_ticker_perc = ((v_data["value"] - v_data["invested"] + ticker_after_tax_divs) / v_data["invested"] * 100) if v_data["invested"] > 0 else Decimal(0)
        portfolio_summary_table_data.append({"ticker": tkr, "shares": v_data["shares"], "average_cost": avg_cost, "current_price": v_data["price"], "portfolio_percentage": portfolio_percentage, "dividends_received": v_data["dividends_received_total_ticker"], "nav_return_ticker": nav_return_ticker, "percent_to_house_money": percent_to_house_money_ticker, "total_return_ticker": total_return_ticker_perc})

    after_tax_total_dividends_historical = total_dividends_received * (Decimal(1) - marginal_tax_rate_decimal)
    
    current_metrics = {
        "net_liquidation_value": portfolio_value - profile.current_margin_used, "portfolio_value": portfolio_value,
        "nlv_goal": profile.nlv_goal, "monthly_estimate": monthly_dividend_estimate_actual_received, "monthly_goal": profile.monthly_goal,
        "nav_return_total": ((portfolio_value - total_invested) / total_invested * Decimal(100)) if total_invested else Decimal(0), 
        "nav_goal": (profile.nav_goal * 100) if profile.nav_goal is not None else Decimal(0), "total_invested": total_invested, 
        "total_dividends_received": total_dividends_received, "percent_to_house_money": (after_tax_total_dividends_historical / total_invested * Decimal(100)) if total_invested else Decimal(0),
        "marginal_tax_rate": marginal_tax_rate_decimal * 100, "current_margin_used": profile.current_margin_used,
        "margin_percentage_of_portfolio": (profile.current_margin_used / portfolio_value * Decimal(100)) if portfolio_value else Decimal(0), 
        "taxes_to_withhold_est": total_dividends_received * marginal_tax_rate_decimal,
        "estimated_daily_interest": (profile.current_margin_used * profile.margin_interest_rate) / Decimal(365) if profile.margin_interest_rate and profile.margin_interest_rate > 0 else Decimal(0),
        "total_return_after_tax_dividends_perc": ((portfolio_value - total_invested + after_tax_total_dividends_historical) / total_invested * Decimal(100)) if total_invested > 0 else Decimal(0),
    }

    dividend_chart_data = {}
    if aggregated_dividends_by_date:
        sorted_dates = sorted(aggregated_dividends_by_date.keys())
        all_tickers_with_dividends = sorted(list(set(ticker for date_data in aggregated_dividends_by_date.values() for ticker in date_data.keys())))
        datasets = [];
        for ticker in all_tickers_with_dividends: datasets.append({ "label": ticker, "data": [aggregated_dividends_by_date[date].get(ticker, 0) for date in sorted_dates] })
        dividend_chart_data = {"labels": sorted_dates, "datasets": datasets}
    
    # START: Corrected Performance Chart Data Calculation for Bar Chart
    performance_chart_data = {}
    start_date = lots.first().date_purchased
    try:
        # Fetch SPY data for the required period
        spy_data = yf.download('SPY', start=start_date, end=now().date() + timedelta(days=1), auto_adjust=False, progress=False)
        
        print(spy_data.head(4))
        spy_adj_close = spy_data['Adj Close'].dropna()
        print(spy_adj_close)
        if spy_adj_close.empty:
            raise ValueError("SPY 'Adj Close' data is empty after dropping NaNs.")

        # --- Safe Data Extraction ---
        spy_start_price_raw = spy_adj_close.iloc[0].item()
        spy_end_price_raw = spy_adj_close.iloc[-1].item()

        print(f"SPY START PRICE RAW{spy_start_price_raw}")
        print(f"SPY END PRICE RAW{spy_end_price_raw}")
        
        # Convert to Decimal safely, handling potential non-numeric data
        spy_start_price = Decimal(str(spy_start_price_raw))
        spy_end_price = Decimal(str(spy_end_price_raw))
        
        print(f"SPY START PRICE {spy_start_price}")
        print(f"SPY END PRICE {spy_end_price}")
        # Calculate SPY total return
        if spy_start_price > 0:
            spy_total_return = ((spy_end_price) / spy_start_price - 1) * 100
        else:
            spy_total_return = Decimal(0)

        print(f"SPY TOTAL RETURN {spy_total_return}")

        # Portfolio total return is already calculated
        portfolio_total_return = current_metrics['total_return_after_tax_dividends_perc']
        print(f"portfolio TOTAL RETURN {portfolio_total_return}")

        # Format data for a bar chart
        performance_chart_data = {
            'labels': ['Portfolio Return', 'SPY Total Return'],
            'datasets': [{
                'label': 'Total Return %',
                'data': [portfolio_total_return, spy_total_return],
                'backgroundColor': ['#0dcaf0', '#28a745']
            }]
        }
    except Exception as e:
        # Print the specific error for debugging
        print(f"Could not generate performance chart data: {e} ({type(e)})") 
        performance_chart_data = {} # Ensure it's an empty dict on failure
    # END: Corrected Performance Chart Data Calculation

    final_data = { 
        "last_data_pull": timezone.now().isoformat(), "lots_data": processed_lots_data, 
        "portfolio_summary_table_data": portfolio_summary_table_data, 
        "dividend_chart_data": dividend_chart_data, "metrics": current_metrics, 
        "has_lots": True, "performance_chart_data": performance_chart_data
    }
    cache.set(CACHE_KEY, final_data, CACHE_TIMEOUT)
    return JsonResponse(final_data, encoder=DecimalEncoder)

def home_view(request):
    if not request.user.is_authenticated:
        return render(request, 'home/home.html')
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        cache.delete(f'portfolio_data_{user.id}')
        if "update_goals" in request.POST:
            goal_form = GoalForm(request.POST, instance=profile) 
            if goal_form.is_valid(): 
                goal_form.save(); messages.success(request, 'Goals updated successfully!')
            else: messages.error(request, 'Please correct the errors in the Goal Settings form.')
        elif "add_lot" in request.POST:
            lot_form = LotForm(request.POST) 
            if lot_form.is_valid(): 
                new_lot = lot_form.save(commit=False); new_lot.user = user; new_lot.save()
                messages.success(request, f'Lot for {new_lot.ticker} added successfully!')
            else: messages.error(request, 'Please correct the errors in the Add Lot form.')
        elif "update_financial_settings" in request.POST:
            financial_settings_form = FinancialSettingsForm(request.POST, instance=profile)
            if financial_settings_form.is_valid():
                financial_settings_form.save(); messages.success(request, 'Financial settings updated successfully!')
            else: messages.error(request, 'Please correct the errors in the Financial Settings form.')
        return redirect("home:dashboard")
    context = {
        "goal_form": GoalForm(instance=profile), "lot_form": LotForm(),
        "financial_settings_form": FinancialSettingsForm(instance=profile), "edit_lot_form": LotForm(),
    }
    return render(request, 'home/home.html', context)

@login_required
@require_POST
def edit_lot(request, lot_id):
    lot = get_object_or_404(Lot, id=lot_id, user=request.user)
    form = LotForm(request.POST, instance=lot)
    if form.is_valid():
        form.save(); messages.success(request, f'Successfully updated lot for {lot.ticker}.')
        cache.delete(f'portfolio_data_{request.user.id}')
    else:
        error_str = " ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
        messages.error(request, f'Update failed. Please correct the errors: {error_str}')
    return redirect('home:dashboard')

@login_required
@require_POST
def delete_lot(request, lot_id):
    lot = get_object_or_404(Lot, id=lot_id, user=request.user)
    ticker = lot.ticker
    lot.delete(); messages.success(request, f'Successfully deleted lot for {ticker}.')
    cache.delete(f'portfolio_data_{request.user.id}')
    return redirect('home:dashboard')

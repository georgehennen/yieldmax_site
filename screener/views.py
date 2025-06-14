import yfinance as yf
from django.shortcuts import render
from .models import ETF
from .forms import ScreenerFilterForm
from decimal import Decimal
from datetime import timedelta, date
from django.core.cache import cache
from django.utils import timezone 
from django.http import JsonResponse
import json
import pandas as pd

class ExtendedEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, pd.Timestamp)): 
             return o.isoformat()
        return super().default(o)

def get_live_etf_metrics(etf):
    ticker = etf.ticker
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        price = info.get('regularMarketPrice', info.get('previousClose'))
        high_52w = info.get('fiftyTwoWeekHigh')
        low_52w = info.get('fiftyTwoWeekLow')
        divs = stock.dividends
        if not all([price, high_52w, low_52w]): return {'error': f'Missing essential price data for {ticker}'}
        price_dec = Decimal(str(price))
        median = (Decimal(str(high_52w)) + Decimal(str(low_52w))) / 2
        lower_median = (Decimal(str(low_52w)) + median) / 2
        percentvlower = ((price_dec - lower_median) / lower_median) * 100 if lower_median else Decimal(0)
        last_div_date = divs.index[-1].date() if not divs.empty else None
        last_div = Decimal(str(divs.iloc[-1])) if not divs.empty else Decimal(0)
        #--
        freq_days = etf.days_between_last_ex_dates()
        next_date = last_div_date + timedelta(days=freq_days) if last_div_date and freq_days else None
        div_multiplier = Decimal('365') / Decimal(freq_days) if freq_days and freq_days > 0 else Decimal(0)
        annual_yield = (last_div / price_dec) * Decimal(div_multiplier) * 100 if price_dec else Decimal(0)
        #--
        underlying_price, underlying_target, underlying_drop_pct, underlying_to_target_pct = None, None, None, None
        if etf.underlying_asset and etf.underlying_asset not in ['Unknown', 'Other', 'Multiple']:
            try:
                u_stock = yf.Ticker(etf.underlying_asset)
                six_months_ago = date.today() - timedelta(days=182)
                hist = u_stock.history(start=six_months_ago)
                if not hist.empty:
                    underlying_price = Decimal(str(hist['Close'].iloc[-1]))
                    high_6mo = Decimal(str(hist['High'].max()))
                    underlying_target = u_stock.info.get('targetMeanPrice')
                    if underlying_target: underlying_target = Decimal(str(underlying_target))
                    if underlying_price and high_6mo: underlying_drop_pct = ((underlying_price - high_6mo) / high_6mo) * 100
                    if underlying_price and underlying_target: underlying_to_target_pct = ((underlying_target - underlying_price) / underlying_price) * 100
            except Exception as e: print(f"Could not fetch underlying data for {etf.underlying_asset}: {e}")
        return {
            'ticker': ticker,
            'underlying_asset': etf.underlying_asset,
            'strategy': etf.strategy,
            'description': etf.description,
            'fund_issuer': etf.fund_issuer,
            'dividend_frequency': freq_days,
            'current_price': price_dec,
            'annual_yield_percentage': annual_yield,
            'price_vs_lower_median_percentage': percentvlower,
            'next_ex_dividend_date': next_date,
            'underlying_price': underlying_price,
            'underlying_target_price': underlying_target,
            'underlying_percent_from_6m_high': underlying_drop_pct,
            'underlying_percent_to_target': underlying_to_target_pct,
        }
    except Exception as e:
        print(f"Could not fetch yfinance data for {ticker}: {e}")
        return {'error': str(e)}

def get_screener_data_api(request):
    CACHE_KEY = "screener_etf_data"
    CACHE_TIMEOUT = 900
    cached_data = cache.get(CACHE_KEY)
    
    etf_data_list, last_data_pull = (cached_data.get('data'), cached_data.get('timestamp')) if cached_data else (None, None)
    
    if etf_data_list is None:
        etfs_qs = ETF.objects.all()
        etf_data_list = [d for d in (get_live_etf_metrics(etf) for etf in etfs_qs) if 'error' not in d]
        last_data_pull = timezone.now()
        cache.set(CACHE_KEY, {'data': etf_data_list, 'timestamp': last_data_pull}, CACHE_TIMEOUT)

    filtered_data = etf_data_list
    form = ScreenerFilterForm(request.GET)
    if form.is_valid():
        strategy = form.cleaned_data.get('strategy')
        if strategy: filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('strategy') in strategy]

        description = form.cleaned_data.get('description')
        if description: filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('description') in description]

        fund_issuer = form.cleaned_data.get('fund_issuer')
        if fund_issuer:
            filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('fund_issuer') in fund_issuer]


        min_yield = form.cleaned_data.get('min_yield')
        if min_yield is not None: filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('annual_yield_percentage') is not None and d['annual_yield_percentage'] >= Decimal(min_yield)]
        
        # Updated filtering logic based on the modified form
        max_pvlm = form.cleaned_data.get('max_pvlm')
        if max_pvlm is not None: filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('price_vs_lower_median_percentage') is not None and d['price_vs_lower_median_percentage'] <= Decimal(max_pvlm)]

        max_from_6m_high = form.cleaned_data.get('max_from_6m_high')
        if max_from_6m_high is not None: filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('underlying_percent_from_6m_high') is not None and d['underlying_percent_from_6m_high'] <= Decimal(max_from_6m_high)]

        min_to_target = form.cleaned_data.get('min_to_target')
        if min_to_target is not None: filtered_data = [d for d in filtered_data if isinstance(d, dict) and d.get('underlying_percent_to_target') is not None and d['underlying_percent_to_target'] >= Decimal(min_to_target)]
            
    response_data = {'etfs': filtered_data, 'last_data_pull': last_data_pull}
    return JsonResponse(response_data, encoder=ExtendedEncoder)

def screener_view(request):
    form = ScreenerFilterForm(request.GET)
    context = {'form': form}
    return render(request, 'screener/screener_list.html', context)
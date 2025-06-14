from django.core.management.base import BaseCommand
from screener.models import ETF, ExDividendRecord
import yfinance as yf

class Command(BaseCommand):
    help = 'Populates the database with initial YieldMax ETF data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting ETF population...')

        # Your provided static data
        YIELDMAX_INFO = {
            "QDTE": {
                "Underlying": "QQQ",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "Roundhill"
            },
            "XDTE": {
                "Underlying": "SPY",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "Roundhill"
            },
            "YBTC": {
                "Underlying": "BTC-USD",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "Roundhill"
            },
            "RDTE": {
                "Underlying": "IWM",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "Roundhill"
            },
            "YETH": {
                "Underlying": "ETH-USD",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "Roundhill"
            },
            "MAGY": {
                "Underlying": "MAGS",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Roundhill"
            },
            "PLTW": {
                "Underlying": "PLTR",
                "Strategy": "Bullish Leveraged",
                "Description": "Leverage",
                "Fund Issuer": "Roundhill"
            },
            "TSLW": {
                "Underlying": "TSLA",
                "Strategy": "Bullish Leveraged",
                "Description": "Leverage",
                "Fund Issuer": "Roundhill"
            },
            "COIW": {
                "Underlying": "COIN",
                "Strategy": "Bullish Leveraged",
                "Description": "Leverage",
                "Fund Issuer": "Roundhill"
            },
            "NVDW": {
                "Underlying": "NVDA",
                "Strategy": "Bullish Leveraged",
                "Description": "Leverage",
                "Fund Issuer": "Roundhill"
            },
            "AAPW": {
                "Underlying": "AAPL",
                "Strategy": "Bullish Leveraged",
                "Description": "Leverage",
                "Fund Issuer": "Roundhill"
            },
            "NVYY": {
                "Underlying": "NVDA",
                "Strategy": "Bullish Leveraged",
                "Description": "Put-Write",
                "Fund Issuer": "GraniteShares"
            },
            "TQQY": {
                "Underlying": "QQQ",
                "Strategy": "Bullish Leveraged",
                "Description": "Put-Buy/Write",
                "Fund Issuer": "GraniteShares"
            },
            "TSYY": {
                "Underlying": "TSLA",
                "Strategy": "Bullish Leveraged",
                "Description": "Put-Buy/Write",
                "Fund Issuer": "GraniteShares"
            },
            "XBTY": {
                "Underlying": "BTC-USD",
                "Strategy": "Bullish Leveraged",
                "Description": "Put-Buy/Write",
                "Fund Issuer": "GraniteShares"
            },
            "YSPY": {
                "Underlying": "SPY",
                "Strategy": "Bullish Leveraged",
                "Description": "Put-Write",
                "Fund Issuer": "GraniteShares"
            },
            "QQQY": {
                "Underlying": "QQQ",
                "Strategy": "Bullish",
                "Description": "Put-Write",
                "Fund Issuer": "Defiance"
            },
            "WDTE": {
                "Underlying": "SPY",
                "Strategy": "Bullish",
                "Description": "Put-Write",
                "Fund Issuer": "Defiance"
            },
            "IWMY": {
                "Underlying": "IWM",
                "Strategy": "Bullish",
                "Description": "Put-Write",
                "Fund Issuer": "Defiance"
            },
            "SPYT": {
                "Underlying": "SPY",
                "Strategy": "Bullish",
                "Description": "Credit Call Spreads",
                "Fund Issuer": "Defiance"
            },
            "USOY": {
                "Underlying": "USO",
                "Strategy": "Bullish",
                "Description": "Put-Write",
                "Fund Issuer": "Defiance"
            },
            "QQQT": {
                "Underlying": "QQQ",
                "Strategy": "Bullish",
                "Description": "Credit Call Spreads",
                "Fund Issuer": "Defiance"
            },
            "GLDY": {
                "Underlying": "GLD",
                "Strategy": "Bullish",
                "Description": "Put-Write",
                "Fund Issuer": "Defiance"
            },
            "MST": {
                "Underlying": "MSTR",
                "Strategy": "Bullish Leveraged",
                "Description": "Credit Call Spreads",
                "Fund Issuer": "Defiance"
            },
            "KQQQ": {
                "Underlying": "QQQ",
                "Strategy": "Bullish Leveraged",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "AMZP": {
                "Underlying": "AMZN",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "AAPY": {
                "Underlying": "AAPL",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "GOOP": {
                "Underlying": "GOOGL",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "MSFY": {
                "Underlying": "MSFT",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "NFLP": {
                "Underlying": "NFLX",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "TSLP": {
                "Underlying": "TSLA",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "Kurv"
            },
            "COII": {
                "Underlying": "COIN",
                "Strategy": "Bullish Leveraged",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "MSII": {
                "Underlying": "MSTR",
                "Strategy": "Bullish Leveraged",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "NVII": {
                "Underlying": "NVDA",
                "Strategy": "Bullish Leveraged",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "TSII": {
                "Underlying": "TSLA",
                "Strategy": "Bullish Leveraged",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "FEPI": {
                "Underlying": "TOPT",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "AIPI": {
                "Underlying": "AI",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "CEPI": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "RexShares"
            },
            "TSLY": {
                "Underlying": "TSLA",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "NVDY": {
                "Underlying": "NVDA",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "MSTY": {
                "Underlying": "MSTR",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "APLY": {
                "Underlying": "AAPL",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "AMZY": {
                "Underlying": "AMZN",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "GOOY": {
                "Underlying": "GOOGL",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "NFLY": {
                "Underlying": "NFLX",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "MSFO": {
                "Underlying": "MSFT",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "FBY": {
                "Underlying": "META",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "JPMO": {
                "Underlying": "JPM",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "DISO": {
                "Underlying": "DIS",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "PYPY": {
                "Underlying": "PYPL",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "ABNY": {
                "Underlying": "ABNB",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "AMDY": {
                "Underlying": "AMD",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "SNOY": {
                "Underlying": "SNOW",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "XOMO": {
                "Underlying": "XOM",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "PLTY": {
                "Underlying": "PLTR",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "CVNY": {
                "Underlying": "CVNA",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "MARO": {
                "Underlying": "MARA",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "MRNY": {
                "Underlying": "MRNA",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "AIYY": {
                "Underlying": "AI",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "HOOY": {
                "Underlying": "HOOD",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "CONY": {
                "Underlying": "COIN",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "BABO": {
                "Underlying": "BABA",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "GDXY": {
                "Underlying": "GDX",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "YBIT": {
                "Underlying": "BTC-USD",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "FIAT": {
                "Underlying": "COIN",
                "Strategy": "Bearish",
                "Description": "Synthetic Covered Put (Put-Write)",
                "Fund Issuer": "YieldMax"
            },
            "DIPS": {
                "Underlying": "NVDA",
                "Strategy": "Bearish",
                "Description": "Synthetic Covered Put (Put-Write)",
                "Fund Issuer": "YieldMax"
            },
            "CRSH": {
                "Underlying": "TSLA",
                "Strategy": "Bearish",
                "Description": "Synthetic Covered Put (Put-Write)",
                "Fund Issuer": "YieldMax"
            },
            "YQQQ": {
                "Underlying": "QQQ",
                "Strategy": "Bearish",
                "Description": "Synthetic Covered Put (Put-Write)",
                "Fund Issuer": "YieldMax"
            },
            "CHPY": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "GPTY": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "LFGY": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "QDTY": {
                "Underlying": "QQQ",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "RDTY": {
                "Underlying": "IWM",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "SDTY": {
                "Underlying": "SPY",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "ULTY": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "YMAG": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "YMAX": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "FEAT": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "FIVY": {
                "Underlying": "Multiple",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "XYZY": {
                "Underlying": "XYZ",
                "Strategy": "Bullish",
                "Description": "Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "OARK": {
                "Underlying": "ARKK",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "TSMY": {
                "Underlying": "TSM",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "SMCY": {
                "Underlying": "SMCI",
                "Strategy": "Bullish",
                "Description": "Synthetic Covered Call (Call-Write)",
                "Fund Issuer": "YieldMax"
            },
            "WNTR": {
                "Underlying": "MSTR",
                "Strategy": "Bearish",
                "Description": "Synthetic Covered Put (Put-Write)",
                "Fund Issuer": "YieldMax"
            }
        }

        etfs_created_count = 0
        etfs_updated_count = 0
        dividends_added = 0

        for ticker, info in YIELDMAX_INFO.items():
            
            # Use update_or_create to avoid duplicates and allow re-running the script
            obj, created = ETF.objects.update_or_create(
                ticker=ticker,
                defaults={
                    'underlying_asset': info.get('Underlying', 'Unknown'),
                    'strategy': info.get('Strategy', 'Unknown'),
                    'description': info.get('Description','Unknown'),
                    'fund_issuer': info.get('Fund Issuer', 'Unknown')
                }
            )
            
            if created:
                etfs_created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully created ETF: {ticker}'))
            else:
                etfs_updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated existing ETF: {ticker}'))

            try:
                ticker_obj = yf.Ticker(ticker)
                dividends = ticker_obj.dividends

                if not dividends.empty:
                    for ex_date in dividends.index[-10:]:  # only last 10
                        ExDividendRecord.objects.get_or_create(etf=obj, ex_date=ex_date.date())
                    print(f"✅ Added dividend history for {ticker}")
                    dividends_added += 1
                else:
                    print(f"⚠️ No dividend data for {ticker}")
            except Exception as e:
                print(f"❌ Error fetching dividends for {ticker}: {e}")

        self.stdout.write(self.style.SUCCESS(f'Population complete. Created: {etfs_created_count}, Updated: {etfs_updated_count}.'))
        self.stdout.write(self.style.SUCCESS(f'Population complete. added: {dividends_added} dividend data'))
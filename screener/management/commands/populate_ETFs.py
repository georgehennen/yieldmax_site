from django.core.management.base import BaseCommand
from screener.models import ETF

class Command(BaseCommand):
    help = 'Populates the database with initial YieldMax ETF data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting ETF population...')

        # Your provided static data
        YIELDMAX_INFO = {
            'TSLY': {'Underlying': 'TSLA', 'Strategy': 'Bullish'}, 'NVDY': {'Underlying': 'NVDA', 'Strategy': 'Bullish'},
            'MSTY': {'Underlying': 'MSTR', 'Strategy': 'Bullish'}, 'APLY': {'Underlying': 'AAPL', 'Strategy': 'Bullish'},
            'AMZY': {'Underlying': 'AMZN', 'Strategy': 'Bullish'}, 'GOOY': {'Underlying': 'GOOGL', 'Strategy': 'Bullish'},
            'NFLY': {'Underlying': 'NFLX', 'Strategy': 'Bullish'}, 'MSFO': {'Underlying': 'MSFT', 'Strategy': 'Bullish'},
            'FBY':  {'Underlying': 'META', 'Strategy': 'Bullish'}, 'JPMO': {'Underlying': 'JPM', 'Strategy': 'Bullish'},
            'DISO': {'Underlying': 'DIS', 'Strategy': 'Bullish'}, 'PYPY': {'Underlying': 'PYPL', 'Strategy': 'Bullish'},
            'ABNY': {'Underlying': 'ABNB', 'Strategy': 'Bullish'}, 'AMDY': {'Underlying': 'AMD', 'Strategy': 'Bullish'},
            'SNOY': {'Underlying': 'SNOW', 'Strategy': 'Bullish'}, 'XOMO': {'Underlying': 'XOM', 'Strategy': 'Bullish'},
            'PLTY': {'Underlying': 'PLTR', 'Strategy': 'Bullish'}, 'CVNY': {'Underlying': 'CVNA', 'Strategy': 'Bullish'},
            'MARO': {'Underlying': 'MARA', 'Strategy': 'Bullish'}, 'MRNY': {'Underlying': 'MRNA', 'Strategy': 'Bullish'},
            'AIYY': {'Underlying': 'AI', 'Strategy': 'Bullish'}, 'HOOY': {'Underlying': 'HOOD', 'Strategy': 'Bullish'},
            'CONY': {'Underlying': 'COIN', 'Strategy': 'Bullish'}, 'BABO': {'Underlying': 'BABA', 'Strategy': 'Bullish'},
            'GDXY': {'Underlying': 'GDX', 'Strategy': 'Bullish'}, 'YBIT': {'Underlying': 'BTC-USD', 'Strategy': 'Bullish'},
            'FIAT': {'Underlying': 'COIN', 'Strategy': 'Bearish'}, 'DIPS': {'Underlying': 'NVDA', 'Strategy': 'Bearish'},
            'CRSH': {'Underlying': 'TSLA', 'Strategy': 'Bearish'}, 'YQQQ': {'Underlying': 'QQQ', 'Strategy': 'Bearish'},
            'CHPY': {'Underlying': 'Multiple', 'Strategy': 'Bullish'}, 'GPTY': {'Underlying': 'Multiple', 'Strategy': 'Bullish'},
            'LFGY': {'Underlying': 'Multiple', 'Strategy': 'Bullish'}, 'QDTY': {'Underlying': 'QQQ', 'Strategy': 'Bullish'},
            'RDTY': {'Underlying': 'IWM', 'Strategy': 'Bullish'}, 'SDTY': {'Underlying': 'SPY', 'Strategy': 'Bullish'},
            'ULTY': {'Underlying': 'Multiple', 'Strategy': 'Bullish'}, 'YMAG': {'Underlying': 'Multiple', 'Strategy': 'Bullish'},
            'YMAX': {'Underlying': 'Multiple', 'Strategy': 'Bullish'}, 'FEAT': {'Underlying': 'Multiple', 'Strategy': 'Bullish'},
            'FIVY': {'Underlying': 'Multiple', 'Strategy': 'Bullish'}, 'XYZY': {'Underlying': 'XYZ', 'Strategy': 'Bullish'},
            'OARK': {'Underlying': 'ARKK', 'Strategy': 'Bullish'}, 'TSMY': {'Underlying': 'TSM', 'Strategy': 'Bullish'},
            'SMCY': {'Underlying': 'SMCI', 'Strategy': 'Bullish'}, 'WNTR': {'Underlying': 'MSTR', 'Strategy': 'Bearish'},
        }
        
        WEEKLY_ETFS = {"CHPY", "GPTY", "LFGY", "QDTY", "RDTY", "SDTY", "ULTY", "YMAG", "YMAX"}

        etfs_created_count = 0
        etfs_updated_count = 0

        for ticker, info in YIELDMAX_INFO.items():
            frequency = ETF.Frequency.WEEKLY if ticker in WEEKLY_ETFS else ETF.Frequency.MONTHLY
            
            # Use update_or_create to avoid duplicates and allow re-running the script
            obj, created = ETF.objects.update_or_create(
                ticker=ticker,
                defaults={
                    'underlying_asset': info.get('Underlying', 'Unknown'),
                    'strategy': info.get('Strategy', 'Unknown'),
                    'dividend_frequency': frequency,
                }
            )
            
            if created:
                etfs_created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully created ETF: {ticker}'))
            else:
                etfs_updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated existing ETF: {ticker}'))

        self.stdout.write(self.style.SUCCESS(f'Population complete. Created: {etfs_created_count}, Updated: {etfs_updated_count}.'))

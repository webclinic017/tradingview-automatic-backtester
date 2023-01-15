# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
load_dotenv()

# 環境変数を参照
import os
USER = os.getenv('TradingView_USERNAME')
PW = os.getenv('TradingView_PASSWORD')
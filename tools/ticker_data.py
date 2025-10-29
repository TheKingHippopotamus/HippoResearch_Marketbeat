import os
import csv
import pandas as pd
from tools.logger import setup_logging

# Setup logging
logger = setup_logging()

class TickerDataManager:
    """מנהל מרכזי לנתוני הטיקרים מה-CSV"""
    
    def __init__(self):
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "flat-ui__data.csv")
        self._ticker_data = {}
        self._sector_map = {}
        self._load_data()
    
    def _load_data(self):
        """טוען את הנתונים מה-CSV"""
        if os.path.exists(self.csv_path):
            try:
                # טעינה עם pandas לנוחות
                df = pd.read_csv(self.csv_path)
                
                # יצירת מילון טיקרים לנתונים מלאים
                for _, row in df.iterrows():
                    ticker = str(row.get('Tickers', '')).strip()
                    if ticker:
                        self._ticker_data[ticker] = {
                            "Security": str(row.get("Security", "")).strip(),
                            "GICS Sector": str(row.get("GICS Sector", "")).strip(),
                            "GICS Sub-Industry": str(row.get("GICS Sub-Industry", "")).strip(),
                            "Headquarters Location": str(row.get("Headquarters Location", "")).strip(),
                            "Date added": str(row.get("Date added", "")).strip(),
                            "CIK": str(row.get("CIK", "")).strip(),
                            "Founded": str(row.get("Founded", "")).strip()
                        }
                
                # יצירת מיפוי טיקרים לסקטורים (לשימוש עתידי)
                self._sector_map = dict(zip(df['Tickers'], df['GICS Sector']))
                
                logger.info(f"✅ Loaded data for {len(self._ticker_data)} tickers from CSV")
                
            except Exception as e:
                logger.warning(f"⚠️ Warning: Could not load ticker data: {e}")
        else:
            logger.warning("⚠️ Warning: CSV file not found, ticker data will be empty")
    
    def get_ticker_info(self, ticker):
        """מחזיר מידע על טיקר ספציפי"""
        return self._ticker_data.get(ticker.upper(), {})
    
    def get_sector(self, ticker):
        """מחזיר את הסקטור של טיקר ספציפי"""
        return self._sector_map.get(ticker.upper(), "")
    
    def get_all_tickers(self):
        """מחזיר את כל הטיקרים הזמינים"""
        return list(self._ticker_data.keys())
    
    def get_tickers_by_sector(self, sector):
        """מחזיר את כל הטיקרים בסקטור מסוים"""
        return [ticker for ticker, data in self._ticker_data.items() 
                if data.get('GICS Sector') == sector]
    
    def get_company_name(self, ticker):
        """מחזיר את שם החברה של טיקר"""
        return self._ticker_data.get(ticker.upper(), {}).get('Security', ticker)
    
    def get_sub_industry(self, ticker):
        """מחזיר את תת-התעשייה של טיקר"""
        return self._ticker_data.get(ticker.upper(), {}).get('GICS Sub-Industry', "")
    
    def get_headquarters(self, ticker):
        """מחזיר את מיקום המטה של טיקר"""
        return self._ticker_data.get(ticker.upper(), {}).get('Headquarters Location', "")
    
    def build_title(self, ticker, max_len=70):
        """בונה כותרת בפורמט: Ticker: Security | GICS Sector | GICS Sub-Industry"""
        ticker_info = self.get_ticker_info(ticker)
        security = ticker_info.get('Security', '').strip()
        sector = ticker_info.get('GICS Sector', '').strip()
        sub_industry = ticker_info.get('GICS Sub-Industry', '').strip()
        
        details = [s for s in [security, sector, sub_industry] if s]
        if details:
            title = f"{ticker}: " + " | ".join(details)
        else:
            title = ticker
            
        if len(title) > max_len:
            title = title[:max_len-1] + '…'
        return title
    
    def get_company_logo_url(self, ticker):
        """מייצר URL ללוגו החברה באמצעות Clearbit"""
        import re
        
        ticker_info = self.get_ticker_info(ticker)
        if ticker_info and 'Security' in ticker_info:
            # שימוש בשם החברה מה-CSV ליצירת דומיין טוב יותר
            company_name = ticker_info['Security']
            
            # המרת שם החברה לפורמט דומיין
            domain_name = company_name.lower()
            domain_name = re.sub(r'\s+(inc\.?|corp\.?|company|co\.?|ltd\.?|llc|plc|group|holdings|technologies|systems|solutions|international|enterprises|ventures|partners|associates|&|and)', '', domain_name)
            domain_name = re.sub(r'[^\w\s-]', '', domain_name)  # הסרת תווים מיוחדים
            domain_name = re.sub(r'\s+', '', domain_name)  # הסרת רווחים
            
            # הוספת סיומת .com
            return f"https://logo.clearbit.com/{domain_name}.com"
        else:
            # גיבוי לדומיין מבוסס טיקר
            company_domain = f"{ticker.lower()}.com"
            return f"https://logo.clearbit.com/{company_domain}"

# יצירת instance גלובלי לשימוש בכל המערכת
ticker_manager = TickerDataManager()

# פונקציות עזר לשימוש קל יותר
def get_ticker_info(ticker):
    """פונקציה גלובלית לקבלת מידע על טיקר"""
    return ticker_manager.get_ticker_info(ticker)

def get_sector(ticker):
    """פונקציה גלובלית לקבלת סקטור של טיקר"""
    return ticker_manager.get_sector(ticker)

def get_company_name(ticker):
    """פונקציה גלובלית לקבלת שם החברה"""
    return ticker_manager.get_company_name(ticker)

def build_title(ticker, max_len=70):
    """פונקציה גלובלית לבניית כותרת"""
    return ticker_manager.build_title(ticker, max_len)

def get_company_logo_url(ticker):
    """פונקציה גלובלית לקבלת URL לוגו"""
    return ticker_manager.get_company_logo_url(ticker) 


from tools.logger import setup_logging 
import subprocess
from datetime import datetime

logger = setup_logging()

# Import log_stage decorator
from tools.logger import log_stage





@log_stage("GIT")
def commit_and_push_changes(ticker):
    """Commit and push changes to repository after processing a ticker"""
    try:
        logger.info(f"🔄 Committing changes for {ticker}...")
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Create commit message
        commit_message = f"הוספת כתבה חדשה: {ticker} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Try to push, if it fails due to upstream issue, set upstream and try again
        try:
            subprocess.run(['git', 'push'], check=True)
        except subprocess.CalledProcessError as e:
            if "no upstream branch" in str(e) or "set-upstream" in str(e):
                logger.info("🔄 Setting upstream branch and pushing...")
                subprocess.run(['git', 'push', '--set-upstream', 'origin', 'main'], check=True)
            else:
                raise e
        
        logger.info(f"✅ Successfully committed and pushed changes for {ticker}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error during git operations: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during commit: {e}")
        return False
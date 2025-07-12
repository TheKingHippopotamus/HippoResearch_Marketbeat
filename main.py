#!/usr/bin/env python3
"""
MarketBit - Automated Market Research System
Main entry point for the entire system

This script provides a unified interface for:
- Processing individual tickers
- Processing all available tickers
- Monitoring and automation features
- System maintenance and cleanup
"""

import argparse
import sys
import os
from datetime import datetime
import time

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Import all modules
from scripts.logger import setup_logging, log_stage
from scripts.process_manager import process_all_tickers, process_single_ticker
from scripts.filemanager import load_ticker_metadata, migrate_existing_articles
from scripts.json_manager import load_unavailable_tickers, load_today_processed
from scripts.clean_metadata import clean_metadata_file
from scripts.ui_ux_manager import check_and_clear_unavailable_tickers, copy_static_files
from scripts.github_automation import commit_and_push_changes

# Setup logging
logger = setup_logging()

def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🦛 MarketBit Research                    ║
║              Automated Market Analysis System               ║
║                                                              ║
║  Features:                                                   ║
║  • Automated ticker processing                              ║
║  • LLM-powered article generation                           ║
║  • Real-time market data scraping                          ║
║  • Git automation and deployment                           ║
║  • Intelligent content management                           ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_status():
    """Print current system status"""
    logger.info("📊 System Status Report")
    logger.info("=" * 50)
    
    try:
        # Load ticker metadata
        ticker_metadata = load_ticker_metadata()
        total_tickers = len(ticker_metadata)
        logger.info(f"📈 Total tickers in database: {total_tickers}")
        
        # Load unavailable tickers
        unavailable = load_unavailable_tickers()
        logger.info(f"🚫 Unavailable tickers: {len(unavailable)}")
        
        # Load today's processed
        today_processed = load_today_processed()
        logger.info(f"✅ Processed today: {len(today_processed)}")
        
        # Calculate available for processing
        available = total_tickers - len(unavailable) - len(today_processed)
        logger.info(f"🔄 Available for processing: {available}")
        
        # Check articles directory
        articles_dir = "articles"
        if os.path.exists(articles_dir):
            html_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]
            logger.info(f"📄 Total articles generated: {len(html_files)}")
        else:
            logger.info("📄 Articles directory not found")
            
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error getting system status: {e}")

@log_stage("MAINTENANCE")
def run_maintenance():
    """Run system maintenance tasks"""
    logger.info("🔧 Starting system maintenance...")
    
    try:
        # Check and clear unavailable tickers if it's a new day
        check_and_clear_unavailable_tickers()
        logger.info("✅ Unavailable tickers check completed")
        
        # Clean metadata file
        clean_metadata_file()
        logger.info("✅ Metadata cleanup completed")
        
        # Copy static files
        copy_static_files("articles")
        logger.info("✅ Static files copied")
        
        logger.info("🎉 System maintenance completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during maintenance: {e}")

@log_stage("MIGRATION")
def run_migration():
    """Migrate existing articles to new format"""
    logger.info("🔄 Starting article migration...")
    
    try:
        migrate_existing_articles()
        logger.info("✅ Article migration completed")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")

def process_ticker_interactive():
    """Interactive ticker processing"""
    print_banner()
    print_system_status()
    
    while True:
        print("\n" + "=" * 50)
        print("🎯 Interactive Ticker Processing")
        print("=" * 50)
        print("1. Process single ticker")
        print("2. Process all available tickers")
        print("3. Show system status")
        print("4. Run maintenance")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            ticker = input("Enter ticker symbol (e.g., AAPL): ").strip().upper()
            if ticker:
                logger.info(f"🚀 Processing single ticker: {ticker}")
                success = process_single_ticker(ticker)
                if success:
                    logger.info(f"✅ Successfully processed {ticker}")
                else:
                    logger.error(f"❌ Failed to process {ticker}")
            else:
                logger.warning("⚠️ No ticker entered")
                
        elif choice == "2":
            confirm = input("Are you sure you want to process ALL available tickers? (y/N): ").strip().lower()
            if confirm == 'y':
                logger.info("🚀 Starting batch processing...")
                process_all_tickers()
            else:
                logger.info("⏹️ Batch processing cancelled")
                
        elif choice == "3":
            print_system_status()
            
        elif choice == "4":
            run_maintenance()
            
        elif choice == "5":
            logger.info("👋 Goodbye!")
            break
            
        else:
            logger.warning("⚠️ Invalid choice. Please enter 1-5.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MarketBit - Automated Market Research System",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--ticker', '-t',
        help="Process a single ticker (e.g., AAPL)"
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help="Process all available tickers"
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help="Start interactive mode"
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help="Show system status"
    )
    
    parser.add_argument(
        '--maintenance', '-m',
        action='store_true',
        help="Run system maintenance"
    )
    
    parser.add_argument(
        '--migrate',
        action='store_true',
        help="Migrate existing articles to new format"
    )
    
    parser.add_argument(
        '--commit', '-c',
        help="Commit changes for a specific ticker"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    try:
        if args.interactive:
            process_ticker_interactive()
            
        elif args.ticker:
            logger.info(f"🚀 Processing single ticker: {args.ticker}")
            success = process_single_ticker(args.ticker.upper())
            if success:
                logger.info(f"✅ Successfully processed {args.ticker}")
            else:
                logger.error(f"❌ Failed to process {args.ticker}")
                
        elif args.all:
            logger.info("🚀 Starting batch processing...")
            process_all_tickers()
            
        elif args.status:
            print_system_status()
            
        elif args.maintenance:
            run_maintenance()
            
        elif args.migrate:
            run_migration()
            
        elif args.commit:
            logger.info(f"📝 Committing changes for {args.commit}")
            success = commit_and_push_changes(args.commit.upper())
            if success:
                logger.info(f"✅ Successfully committed {args.commit}")
            else:
                logger.error(f"❌ Failed to commit {args.commit}")
                
        else:
            # Default: show help
            parser.print_help()
            print("\n" + "=" * 50)
            print("💡 Tip: Use --interactive for an easy-to-use menu")
            print("💡 Tip: Use --status to see current system state")
            print("=" * 50)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Operation cancelled by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

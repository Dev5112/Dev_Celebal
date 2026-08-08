import argparse
import sys
from pathlib import Path
from tabulate import tabulate
import colorama
from colorama import Fore

from src.database.connection import DatabaseManager
from src.analytics.models import ReportType
from src.analytics.executor import ReportGenerator

def main() -> None:
    colorama.init(autoreset=True)
    
    parser = argparse.ArgumentParser(
        description="E-Commerce Analytics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python report_cli.py --report revenue
  python report_cli.py --report top_customers --limit 20
  python report_cli.py --report retention --format csv
  python report_cli.py --report health_check
        """
    )
    
    parser.add_argument('--report', 
                       type=str,
                       required=True,
                       choices=[r.value for r in ReportType],
                       help='Report type to generate')
    
    parser.add_argument('--limit',
                       type=int,
                       default=10,
                       help='Limit number of results')
    
    parser.add_argument('--format',
                       type=str,
                       choices=['table', 'csv', 'json'],
                       default='table',
                       help='Output format')
    
    parser.add_argument('--output',
                       type=Path,
                       help='Save to file (optional)')
    
    parser.add_argument('--db',
                       type=Path,
                       default=Path('database/ecommerce.db'),
                       help='Database path')
                       
    parser.add_argument('--sql-dir',
                       type=Path,
                       default=Path('sql'),
                       help='Path to SQL scripts directory')
    
    args = parser.parse_args()
    
    if not args.db.exists():
        print(Fore.RED + f"ERROR: Database not found at {args.db}")
        sys.exit(1)
        
    try:
        with DatabaseManager(args.db) as db:
            generator = ReportGenerator(db, args.sql_dir)
            df = generator.generate_report(ReportType(args.report), limit=args.limit)
            
            if args.format == 'table':
                print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            elif args.format == 'csv':
                print(df.to_csv(index=False))
            elif args.format == 'json':
                print(df.to_json(orient='records', indent=2))
            
            if args.output:
                if args.format == 'csv':
                    df.to_csv(args.output, index=False)
                elif args.format == 'json':
                    df.to_json(args.output, orient='records', indent=2)
                else:
                    with open(args.output, 'w') as f:
                        f.write(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
                print(Fore.GREEN + f"\n✓ Report saved to {args.output}")
                
    except Exception as e:
        print(Fore.RED + f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

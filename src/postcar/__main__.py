import asyncio
from postcar.__about__ import __version__
from postcar.cli import handlers, parser


args = parser.parse_args()


if args.version:
    print(__version__)
    exit(0)

if args.command is None:
    parser.print_help()
    exit(1)

if (handler := handlers.get(args.command)) is None:
    print(f"handler for '{args.command}' not found")
    exit(1)

asyncio.run(handler(args=args))

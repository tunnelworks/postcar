import argparse
from postcar import config


def get_config(args: argparse.Namespace) -> config.Config:
    return config.Config(
        namespace=args.namespace,
        packages=args.packages,
        connection=config.ConnectionInfo(
            host=args.host,
            port=args.port,
            dbname=args.dbname,
            username=args.user,
            password=args.password,
        ),
    )

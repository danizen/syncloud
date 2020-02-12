import os
import sys
from argparse import ArgumentParser

from .utils import logger
from .setup import create_stack, setup_bucket_notification


DFLT_BUCKET_NAME = os.environ.get('SYNCLOUD_BUCKET_NAME')
DFLT_QUEUE_URL = os.environ.get('SYNCLOUD_QUEUE_URL')
DFLT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    'cf', 'bucket_template.yaml'
)
DFLT_PREFIX = os.environ.get('SYNCLOUD_PREFIX', '')
DFLT_PATH = os.environ.get('SYNCLOUD_PATH')
DFLT_INCLUDE = os.environ.get('SYNCLOUD_INCLUDE')
DFLT_EXCLUDE = os.environ.get('SYNCLOUD_EXCLUDE')


def require_opts(opts, *args):
    for arg in args:
        value = getattr(opts, arg):
        if value is None:
            print('--{} is required'.format(arg), file=sys.stderr)
            return True
    return False


def create_command(opts):
    if require_opts(opts, 'template', 'bucket', 'queue'):
        return 1
    create_stack(opts.template, opts.bucket, opts.queue)
    setup_bucket_notification(opts.bucket, opts.queue)
    print('create completed')
    return 0


def push_command(opts):
    if require_opts(opts, 'bucket', 'path'):
        return 1
    print('push - not yet implemented')
    return 1


def pull_command(opts):
    if require_opts(opts, 'queue', 'bucket', 'path'):
        return 1
    print('pull - not yet implemented')
    return 1


def create_parser(prog_name):
    # These common options can occur before or after one of the commands
    common = ArgumentParser(add_help=False)                                 
    common.add_argument(
        '--verbose', '-v',
        action='count', default=0,
        help='increase verbosity'
    )
    common.add_argument(
        '--bucket', '-b', metavar='NAME',
        default=DFLT_BUCKET_NAME,
        help='specify the bucket name'
    )
    common.add_argument(
        '--queue', '-q', metavar='NAME',
        default=DFLT_QUEUE_URL,
        help='specify the queue NAME'
    )


    # These options apply to the push/pull commands only
    pushpull = ArgumentParser(add_help=False)
    pushpull.add_argument(
        '--path', metavar='PATH',
        default=DFLT_PATH,
        help='Local directory path to watch for changes',
    )
    pushpull.add_argument(
        '--prefix', metavar='PREFIX',
        default=DFLT_PREFIX,
        help='Prefix to use when accessing S3',
    )
    pushpull.add_argument(
        '--include', metavar='PATTERN', nargs='+',
        default=DFLT_INCLUDE,
        help='A regular expression which will be applied to files'
    )
    pushpull.add_argument(
        '--exclude', metavar='PATTERN', nargs='+',
        default=DFLT_EXCLUDE,
        help='A regular expression which will be applied to files'
    )

    # the parser is organized into sub-parsers (commands)
    parser = ArgumentParser(prog=prog_name)
    sp = parser.add_subparsers(title="command(s)")

    # setup command
    create = sp.add_parser(
        'setup',
        parents=[common],
        help='create bucket and associated queue'
    )
    create.set_defaults(func=create_command)
    create.add_argument(
        '--template', metavar='PATH',
        default=DFLT_TEMPLATE_PATH,
        help='Path to the cloudformation template'
    )

    # push command
    push = sp.add_parser(
        'push',
        parents=[common, pushpull],
        help='push local files to the queue'
    )
    push.set_defaults(func=push_command)

    # pull command
    pull = sp.add_parser(
        'pull',
        parents=[common, pushpull],
        help='pull changes from the bucket locally'
    )
    pull.set_defaults(func=pull_command)
    return parser


def main_guts(args):
    parser = create_parser(args[0])
    opts = parser.parse_args(args[1:])
    if not hasattr(opts, 'func'):
        parser.print_help(sys.stderr)
        return 1
    if opts.verbose == 1:
        logger.setLevel(logging.INFO)
    elif opts.verbose > 1:
        logger.setLevel(logging.DEBUG)
    return opts.func(opts)


def main():
    logging.basicConfig()
    return main_guts(sys.argv)


if __name__ == '__main__':
    main()

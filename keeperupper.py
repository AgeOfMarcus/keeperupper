from configparser import ConfigParser
from argparse import ArgumentParser, Namespace
import requests

def read_config(filename: str) -> ConfigParser:
    config = ConfigParser()
    try:
        config.read(filename)
        return config
    except:
        return False

def error(text: str, json: bool):
    if json:
        print({'error': text})
    else:
        print('[!] Error:', text)
    exit(1)

def output(results: dict) -> str:
    fix = lambda s: f'"{s}"'
    alive = ', '.join(list(map(fix, results['alive'])))
    dead = ', '.join(list(map(fix, results['dead'])))
    return f'sites that were alive: {alive}. sites that were dead: {dead}.'

def parse_args():
    p = ArgumentParser()
    p.add_argument('-c', '--config', help='Configuration file to use', type=str, required=True)
    p.add_argument('-s', '--simple', help='Output simple information (number of sites alive:dead)', action='store_true')
    p.add_argument('-t', '--timeout', help='Override timeout with this value', type=int)
    p.add_argument('-n', '--name', help='Only check specific site by name', type=str)
    p.add_argument('-j', '--json', help='Output json only', action='store_true')
    
    args = p.parse_args()
    if args.simple and args.json:
        p.error('-s/--simple and -j/--json cannot be used in conjunction')
        exit(1)
    return args

def main(args: Namespace):
    config = read_config(args.config)

    if args.name:
        if args.name in config.sections():
            sites = [args.name]
        else:
            error(f'site {args.name} not found in config file {args.config}')
    else:
        sites = config.sections()
    
    results = {'alive': [], 'dead': []}
    for name in sites:
        site = config[name]

        try:
            r = requests.get(site['URL'], timeout=(args.timeout if args.timeout else int(site['Timeout'])))
            if r.status_code == int(site['Expected']):
                results['alive'].append(name)
            else:
                results['dead'].append(name)
        except requests.exceptions.ReadTimeout:
            results['dead'].append(name)
    
    if args.simple:
        if args.name:
            return f'{args.name} was ' + ('alive' if args.name in results['alive'] else 'dead') + '.'
        return f'{len(results["alive"])} sites were up. {len(results["dead"])} sites were unreachable.'

    if args.json:
        return results

    if args.name:
        return f'{args.name} was ' + ('alive' if results['alive'] else 'dead') + '.'

    return output(results)

if __name__ == '__main__':
    exit(print(main(parse_args())))
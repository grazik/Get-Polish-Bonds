import argparse
import requests
import pandas as pd
import urllib.parse as urlparse
from datetime import date
from operator import itemgetter

URL_BASE='https://gpw.notoria.pl/widgets/bonds/screener.php'
BOND_URL_BASE='https://gpwcatalyst.pl/instrument?nazwa={}'

parser = argparse.ArgumentParser()

parser.add_argument('--yf', help='yield to maturinity - from', type=float, default=1)
parser.add_argument('--yt', help='yield to maturinity - to', type=float, default=5)

parser.add_argument('--mf', help='maturnity - from', type=float, default=1)
parser.add_argument('--mt', help='maturnity - to', type=float, default=5)

parser.add_argument('--rate', '-r', help='Type of rates - ZC, XC, FC, IN', nargs='*')
parser.add_argument('--type', '-t', help='Type of bonds - TB, MB, CB, SB, MG', nargs='*')

parser.add_argument('--bondspot', '-b', help='Search BondSpot market', action='store_true')
parser.add_argument('--alternatives', '-a', help='Should search in alternative markets', action='store_true')

args = parser.parse_args()

GPW_REGULATED = 243
GPW_ALTERNATIVE = '243A'
BONDSPOT_REGULATED = 986
BONDSPOT_ALTERNATIVE = 989

offset_value = 0

YIELD_FROM='yf'
YIELD_TO='yt'

SORT_NAME='sort_name'
SORT_DIR='sort_dir'

MATURITY_FROM='blenf'
MATURITY_TO='blent'

OFFSET='offset'
TYPE='type[]'
RATE='rate[]'
MARKET='market[]'

BOND_TYPE_MAP = {
        'TB': 'Skarbowe',
        'MB': 'Komunalne',
        'CB': 'Korporacyjne',
        'SB': 'Spoldzielne',
        'MG': 'Listy zastawne',
}

BOND_RATE_MAP = {
        'ZC': 'Zerokuponowe',
        'XC': 'Staly kupon',
        'FC': 'Zmienny kupon',
        'IN': 'Indeksowama wartosc nominalna',
}

NAME_MAP = {
        'uname': 'Nazwa',
        'issuer': 'Emitent',
        'type': 'Typ',
        'rate': 'Kupon',
        'dt': 'Termin wykupu',
        'price': 'Kurs',
        'ir': 'Oprocentowanie',
        'y_invest': 'Zwrot z inwestycji brutto',
        'y_invest_net': 'Zwrot z inwestycji netto',
        'blen': 'Zapadalnosc',
        'ytm': 'Roczna stopa zwrotu brutto',
        'ytm_net':  'Roczna stopa zwrotu netto',
        'market': 'Rynek'
}

MARKET_MAP = {
        GPW_REGULATED: 'GPW',
        GPW_ALTERNATIVE: 'GPW Alternatywny',
        BONDSPOT_REGULATED: 'BondSpot',
        BONDSPOT_ALTERNATIVE: 'BondSpot Alternatywny',
}


def create_url(market, offset = 0):
    return URL_BASE + '?' + urlparse.urlencode({
        **({RATE: args.rate} if args.rate is not None else {}),
        **({TYPE: args.type} if args.type is not None else {}),
        OFFSET: offset,
        YIELD_TO: args.yt,
        YIELD_FROM: args.yf,
        MATURITY_TO: args.mt,
        MATURITY_FROM: args.mf,
        MARKET: [market] 
    }, True)

def process_type(bond_data):
    [bond_type, bond_rate, _] = bond_data.split('-')
    return [BOND_TYPE_MAP[bond_type], BOND_RATE_MAP[bond_rate]]

def process_bond(bond, market):
    ytm_n, ytm_b, blen = itemgetter('ytm_net', 'ytm', 'blen')(bond)
    
    [bond_type, bond_rate] = process_type(bond['type'])
    return {
            **bond,
            'type': bond_type,
            'rate': bond_rate,
            'y_invest': float(ytm_b) * float(blen),
            'y_invest_net': float(ytm_n) * float(blen),
            'market': MARKET_MAP[market],
    }


def get_data():
    data = []
    markets = list(filter(lambda m: m,[GPW_REGULATED, args.alternatives and GPW_ALTERNATIVE, args.bondspot and BONDSPOT_REGULATED, args.alternatives and args.bondspot and BONDSPOT_ALTERNATIVE]))
    for market in markets:
        shouldMakeRequest = True
        sub_data = []
        while shouldMakeRequest:
            url = create_url(market, len(sub_data))
            print('Calling: ', url)
            r = requests.get(url, headers={'Referer': 'https://gpwcatalyst.pl/'})
            response = r.json()
            new_bonds = response['screener']['bonds']
            shouldMakeRequest = not len(new_bonds) % 10
            sub_data = [*sub_data, *[process_bond(bond, market) for bond in new_bonds]]
        data = [*data, *sub_data]
    return data

def create_df(data):
    df = pd.DataFrame(data, columns=['market', 'uname', 'issuer', 'type', 'rate', 'price', 'ir', 'ytm', 'ytm_net', 'blen', 'y_invest', 'y_invest_net'])
    df['uname'] = df['uname'].apply(lambda x: f'=HYPERLINK("{BOND_URL_BASE.format(x)}"; "{x}")')
    df.columns = [NAME_MAP[name] for name in df.columns]
    return df

def save_to_excel(df, name):
    df.to_excel(name, float_format="%.2f")

data = get_data()
df = create_df(data)
save_to_excel(df, 'bonds-' + date.today().strftime("%d-%m-%Y") + '.xlsx')

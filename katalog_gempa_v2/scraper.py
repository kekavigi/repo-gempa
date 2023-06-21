# Membantu mem-fetch halaman
import requests
from requests.models import PreparedRequest
from random import uniform

from selectolax.parser import HTMLParser

# Berkaitan tentang waktu
from datetime import datetime, timedelta
from time import sleep

from typing import Optional  # pengingat tipe variabel, karena saya pikun
from tqdm import tqdm  # akan menampilkan progress-bar ketika looping

DATE_RANGE = timedelta(days=10)


def get_time(dt: datetime) -> str:
    '''Memformat waktu yang dipahami oleh form Event Request'''

    return dt.strftime('%Y-%m-%dT%H:%M:%S')
    # get_time(datetime(2019, 3, 8, 12, 30, 11))
    # 2019-03-08T12:30:11


def set_filename(directory: str, min_date: datetime, max_date: datetime) -> str:
    '''Menghasilkan nama berkas untuk HTML yang didapat'''

    _min = min_date.strftime('%Y-%m-%d')
    _max = max_date.strftime('%Y-%m-%d')
    return f'{directory}/{_min}-{_max}.html'


def save_html(
    directory: str,
    min_date: datetime,
    max_date: Optional[datetime] = None,
    institution: str = 'school',
    email: str = 'scraping@school.com',
) -> None:
    '''Mengunduh berkas HTML berisi data event gempa'''

    # Persiapan, secara personal, saya mengganggap `max_date`
    # tidak perlu wajib ada, karena secara implisit dapat
    # dihasilkan dengan bantuan `DATE_RANGE`
    max_date = max_date if max_date else min_date+DATE_RANGE

    # Dapatkan token form
    url_form = 'https://repogempa.bmkg.go.id/eventcatalog'
    _html = requests.get(url_form)
    if _html.status_code != 200:
        raise ConnectionError(
            f'Gagal mem-fetch form. (Error {_html.status_code})')
    _parsed = HTMLParser(_html.text)
    # lokasi token di berkas HTML
    token = _parsed.css_first('input[name="_token"]').attributes.get('value')

    # Lakukan request data gempa. Secara sederhana, kita
    # mencoba meminta data gempa tanpa perlu menge-klik
    # submit di halaman form Event Request
    url_event = 'https://repogempa.bmkg.go.id/getEvent'
    params = {
        '_token': token,
        'date_range': '',  # Tidak wajib
        'min_date': get_time(min_date),
        'max_date': get_time(max_date),
        'minmag': '0.0',
        'maxmag': '10.0',
        'mindepth': '0',
        'maxdepth': '1000',
        'north': '6',
        'west': '95',
        'east': '141',
        'south': '-11',
        'eventtype': 'preliminaryeq',
        'parameter': 'originfocal',  # Dapatkan mekanisme fokal gempa
        'email': email,
        'institution': institution,
    }
    req = PreparedRequest()
    req.prepare_url(url_event, params)
    _html = requests.get(req.url)
    if _html.status_code != 200:
        raise ConnectionError(
            f'Gagal mem-fetch hasil. (Error {_html.status_code})')

    # simpan HTML yang didapat sebagai bukti
    with open(set_filename(directory, min_date, max_date), 'w') as f:
        f.write(_html.text)


def main():
    # Data gempa paling tua yang tercatat di Repo Gempa
    start_day = datetime(2008, 11, 1, 0, 0, 0)
    end_day = datetime.now()

    with tqdm(total=(end_day-start_day).days) as pgbar:
        while start_day < datetime.now():
            # sebenarnya akan lebih baik untuk berhenti beberapa hari sebelum
            # *hari ini*, namun saya rasa ini juga sudah cukup.

            try:
                save_html('nraw', start_day)
            except ConnectionError:
                # Server error, coba abaikan hari ini dan scraping dari hari besok.
                # Alasan error terjadi akan dianalisis secara manual.
                start_day += timedelta(days=1)
                pgbar.update(1)
            else:
                # Data gempa dalam jangka waktu `DATE_RANGE` berhasil diunduh.
                # Mulai scraping dari awal waktu yang baru.
                start_day += DATE_RANGE
                pgbar.update(DATE_RANGE.days)
            finally:
                # Apapun yang terjadi, pada akhirnya kita perlu tunggu beberapa
                # detik sebelum lanjut mendownload data. Kita tidak ingin secara
                # tidak sengaja membuat server BMKG *down*.
                sleep(uniform(20, 40))   # detik

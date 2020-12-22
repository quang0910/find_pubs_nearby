import requests
import json
import time

url_base = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
location_pymi = '21.013111,105.799972'
keyword = 'beer'
radius = 2000


class ServerError(Exception):
    pass


def get_apikey():
    with open('apikey.txt', 'rt') as f:
        api_key = f.readline()
    return api_key[:-1]


def find_pubs(location, keyword, radius):
    pubs_beer = []
    params = {'location': location,
              'radius': radius,
              'keyword': keyword,
              'key': get_apikey()
              }
    ses = requests.Session()
    resp = ses.get(url_base, params=params)
    if resp.status_code // 100 == 5:
        raise ServerError('Cannot connect to Server!')
    data = resp.json()
    if not data:
        raise ValueError('Data not found!')
    pubs_beer.extend(data['results'])
    time.sleep(5)
    while 'next_page_token' in data:
        params['pagetoken'] = data['next_page_token']
        resp = ses.get(url_base, params=params)
        if resp.status_code // 100 == 5:
            raise ServerError('Cannot connect to Server!')
        data = resp.json()
        if not data:
            raise ValueError('Data not found!')
        pubs_beer.extend(data['results'])
        if len(pubs_beer) >= 50:
            break
        time.sleep(5)
    return pubs_beer[:50]


def create_geojson(beer_data):
    geojon_features = [
        {
            "type": "Feature",
            "geometry":{"type": "Point",
            "coordinates": [float(data['geometry']['location']['lng']),
                            float(data['geometry']['location']['lat'])]
                        },
            "properties": {"name": data['name'],
                           "Address": data['vicinity'],
                           },

        } for data in beer_data]
    geo_json_format = {"type": "FeatureCollection",
                       "features": geojon_features}
    with open('pymi_beer.geojson', 'wt') as f:
        json.dump(geo_json_format, f, ensure_ascii=False, indent=4)



def main():
    beer_location_data = find_pubs(location_pymi, keyword, radius)
    create_geojson(beer_location_data)


if __name__ == "__main__":
    main()

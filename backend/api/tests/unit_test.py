import json


def test_country_population_200(client):
    response = client.get(
        '/api/population/country?countries=Afghanistan,Austria&startYear=2005&years=1')

    mock_response = {
        "data": [
            {
                "country": "Afghanistan",
                "population": [
                    {
                        "amount": 25700000,
                        "year": 2005
                    }
                ]
            },
            {
                "country": "Austria",
                "population": [
                    {
                        "amount": 8250000,
                        "year": 2005
                    }
                ]
            }
        ],
        "ok": True,
        "status": 200
    }

    assert json.loads(response.get_data()) == mock_response


def test_country_population_400_1(client):
    response = client.get(
        '/api/population/country?countries=Afghanistan,Austria&years=1')

    mock_response = {
        "detail": "Missing query paramenter, you have to specify an initial year and how many years to recover.",
        "ok": False,
        "status": 400,
        "title": "Bad Request"
    }

    assert json.loads(response.get_data()) == mock_response


def test_country_population_400_2(client):
    response = client.get(
        '/api/population/country?countries=Afghanistan,Austria&startYear=2005')

    mock_response = {
        "detail": "Missing query paramenter, you have to specify an initial year and how many years to recover.",
        "ok": False,
        "status": 400,
        "title": "Bad Request"
    }

    assert json.loads(response.get_data()) == mock_response


def test_top_population_200(client):
    response = client.get('/api/population/top?year=2005')

    mock_response = {
        "data": [
            {
                "country": "China",
                "population": 1330000000
            },
            {
                "country": "India",
                "population": 1150000000
            },
            {
                "country": "United States",
                "population": 295000000
            },
            {
                "country": "Indonesia",
                "population": 226000000
            },
            {
                "country": "Brazil",
                "population": 186000000
            },
            {
                "country": "Pakistan",
                "population": 160000000
            },
            {
                "country": "Russia",
                "population": 144000000
            },
            {
                "country": "Bangladesh",
                "population": 139000000
            },
            {
                "country": "Nigeria",
                "population": 139000000
            },
            {
                "country": "Japan",
                "population": 128000000
            }
        ],
        "ok": True,
        "status": 200
    }

    assert json.loads(response.get_data()) == mock_response


def test_top_population_400(client):
    response = client.get('/api/population/top')

    mock_response = {
        "detail": "Missing query paramenter, you have to specify a year.",
        "ok": False,
        "status": 400,
        "title": "Bad Request"
    }

    assert json.loads(response.get_data()) == mock_response


def test_region_population_200(client):
    response = client.get('/api/population/region?year=2000')

    mock_response = {
        "data": [
            {
                "population": 809487000,
                "region": "africa"
            },
            {
                "population": 829522800,
                "region": "americas"
            },
            {
                "population": 3667105990,
                "region": "asia"
            },
            {
                "population": 804445990,
                "region": "europe"
            }
        ],
        "ok": True,
        "status": 200
    }

    assert json.loads(response.get_data()) == mock_response


def test_region_population_400(client):
    response = client.get('/api/population/region')

    mock_response = {
        "detail": "Missing query paramenter, you have to specify a year.",
        "ok": False,
        "status": 400,
        "title": "Bad Request"
    }

    assert json.loads(response.get_data()) == mock_response

def test_add_country_200(client):
    response = client.post('/api/population/add-country',
                           json={'country': 'Test', 'populations': [{'year': 2021, 'amount': 20}]})


def test_add_country_400(client):
    response = client.post('/api/population/add-country',
                           json={'country': 'Test', 'populations': []})


def test_edit_country_200(client):
    response = client.put('/api/population/edit-country', json=(
        {'country': 'Test', 'populations': [{'year': 2021, 'amount': 21}]}))


def test_edit_country_400(client):
    response = client.put('/api/population/edit-country', json=(
        {'country': 'Test', 'populations': []}))


def test_delete_country_200(client):
    response = client.delete('/api/population/delete-country?country=Test')

def test_delete_country_400(client):
    response = client.delete('/api/population/delete-country')
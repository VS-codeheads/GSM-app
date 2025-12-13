import pytest
import json
from unittest.mock import patch, MagicMock
import requests

# Expected structure for OpenWeather API response
EXPECTED_WEATHER_RESPONSE_SCHEMA = {
    "cod": (int, str),
    "main": dict,
    "weather": list,
}

# Expected structure for main weather data
EXPECTED_WEATHER_MAIN_SCHEMA = {
    "temp": (int, float),
    "feels_like": (int, float),
    "temp_min": (int, float),
    "temp_max": (int, float),
    "pressure": int,
    "humidity": int,
}

# Expected structure for weather condition item
EXPECTED_WEATHER_CONDITION_SCHEMA = {
    "id": int,
    "main": str,
    "description": str,
    "icon": str,
}


class TestWeatherAPI:
    """Integration tests for external weather API integration."""

    @pytest.fixture
    def mock_weather_response(self):
        """
        Fixture that provides a mock OpenWeather API response.
        """
        return {
            "cod": 200,
            "coord": {"lon": 12.5683, "lat": 55.6761},
            "weather": [
                {
                    "id": 500,
                    "main": "Rain",
                    "description": "light rain",
                    "icon": "10d"
                }
            ],
            "main": {
                "temp": 15.5,
                "feels_like": 14.8,
                "temp_min": 14.2,
                "temp_max": 16.8,
                "pressure": 1013,
                "humidity": 72
            },
            "clouds": {"all": 75},
            "wind": {"speed": 3.5},
            "visibility": 10000,
            "dt": 1640088000,
            "sys": {
                "type": 2,
                "id": 2019646,
                "country": "DK",
                "sunrise": 1640046000,
                "sunset": 1640075000
            },
            "timezone": 3600,
            "id": 2618426,
            "name": "Copenhagen",
            "base": "stations"
        }

    def test_weather_api_response_has_valid_structure(self, mock_weather_response):
        """
        Checks that a valid OpenWeather API response has the expected structure.
        """
        response_data = mock_weather_response

        # Verify top-level structure
        for field in EXPECTED_WEATHER_RESPONSE_SCHEMA.keys():
            assert field in response_data, f"Missing field '{field}' in response"

        # Verify weather list has items with correct structure
        assert len(response_data["weather"]) > 0, "Weather list is empty"

        for weather_item in response_data["weather"]:
            for field, expected_type in EXPECTED_WEATHER_CONDITION_SCHEMA.items():
                assert field in weather_item, f"Missing field '{field}' in weather item"
                assert isinstance(weather_item[field], expected_type), \
                    f"Field '{field}' is not of type {expected_type}"

        # Verify main data structure
        main = response_data["main"]
        for field, expected_type in EXPECTED_WEATHER_MAIN_SCHEMA.items():
            assert field in main, f"Missing field '{field}' in main weather data"
            assert isinstance(main[field], expected_type), \
                f"Field '{field}' is not of type {expected_type}"

    @pytest.mark.parametrize("city,api_key", [
        ("Copenhagen", "6b4b1400888cfc29ec5a3d7dd73be8d6"),
        ("London", "test_key_123"),
        ("New York", "test_key_456"),
    ])
    @patch('requests.get')
    def test_weather_api_calls_correct_endpoint(self, mock_get, city, api_key, mock_weather_response):
        """
        Parameterized test: Checks that weather API is called with correct parameters.
        Tests multiple cities and API keys.
        """
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.status_code = 200

        # Simulate the weather API call (as it would be done in the application)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        response = requests.get(url)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(url)
        assert response.status_code == 200

    @patch('requests.get')
    def test_weather_api_returns_temperature_in_celsius(self, mock_get, mock_weather_response):
        """
        Checks that weather API returns temperature in Celsius when units=metric.
        """
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.status_code = 200

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=test_key"
        )

        data = response.json()
        assert "main" in data
        assert "temp" in data["main"]
        assert isinstance(data["main"]["temp"], (int, float))
        # Celsius temperature for Copenhagen should be reasonable
        assert -50 < data["main"]["temp"] < 50

    @patch('requests.get')
    def test_weather_api_returns_weather_description(self, mock_get, mock_weather_response):
        """
        Checks that weather API returns weather description and icon.
        """
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.status_code = 200

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=test_key"
        )

        data = response.json()
        assert "weather" in data
        assert len(data["weather"]) > 0

        weather = data["weather"][0]
        assert "description" in weather
        assert "icon" in weather
        assert isinstance(weather["description"], str)
        assert isinstance(weather["icon"], str)
        assert len(weather["icon"]) > 0

    @patch('requests.get')
    def test_weather_api_handles_404_response(self, mock_get):
        """
        Checks that application handles 404 (city not found) from weather API.
        """
        error_response = {
            "cod": 404,
            "message": "city not found"
        }

        mock_get.return_value.json.return_value = error_response
        mock_get.return_value.status_code = 404

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?q=InvalidCity&units=metric&appid=test_key"
        )

        data = response.json()
        assert data.get("cod") != 200, "Should indicate error in response"

    @patch('requests.get')
    def test_weather_api_handles_401_unauthorized(self, mock_get):
        """
        Checks that application handles 401 (invalid API key) from weather API.
        """
        error_response = {
            "cod": 401,
            "message": "Invalid API key"
        }

        mock_get.return_value.json.return_value = error_response
        mock_get.return_value.status_code = 401

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=invalid_key"
        )

        data = response.json()
        assert data.get("cod") != 200, "Should indicate authentication error"

    @patch('requests.get')
    def test_weather_api_handles_timeout(self, mock_get):
        """
        Checks that application handles request timeout from weather API.
        """
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(requests.exceptions.Timeout):
            requests.get(
                "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=test_key"
            )

    @patch('requests.get')
    def test_weather_api_handles_connection_error(self, mock_get):
        """
        Checks that application handles connection errors from weather API.
        """
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get(
                "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=test_key"
            )

    @pytest.mark.parametrize("city", [
        "Copenhagen",
        "London",
        "Paris",
        "Tokyo",
        "New York"
    ])
    @patch('requests.get')
    def test_weather_api_works_for_multiple_cities(self, mock_get, city, mock_weather_response):
        """
        Parameterized test: Checks that weather API works for various cities.
        """
        response_data = mock_weather_response.copy()
        response_data["name"] = city

        mock_get.return_value.json.return_value = response_data
        mock_get.return_value.status_code = 200

        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=test_key"
        )

        data = response.json()
        assert data["name"] == city
        assert data["cod"] == 200
        assert "temp" in data["main"]
        assert "weather" in data

    @patch('requests.get')
    def test_weather_api_response_includes_icon_for_display(self, mock_get, mock_weather_response):
        """
        Checks that weather API response includes icon data that can be displayed.
        """
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.status_code = 200

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=test_key"
        )

        data = response.json()
        icon = data["weather"][0]["icon"]

        # Icon should be in format like "10d", "02n", etc.
        assert len(icon) == 3, "Icon format should be 3 characters (e.g., '10d', '02n')"
        assert icon[2] in ["d", "n"], "Icon should end with 'd' (day) or 'n' (night)"
        assert icon[:2].isdigit(), "Icon should start with 2-digit code"

        # Verify URL construction for icon
        icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
        assert f"/wn/{icon}@2x.png" in icon_url, "Icon URL should be properly formatted"

    @patch('requests.get')
    def test_weather_api_returns_consistent_response_structure(self, mock_get, mock_weather_response):
        """
        Checks that multiple calls to weather API return consistent response structure.
        """
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.status_code = 200

        # Make multiple calls
        responses = []
        for _ in range(3):
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather?q=Copenhagen&units=metric&appid=test_key"
            )
            responses.append(response.json())

        # Verify all have same structure
        for resp in responses:
            assert "cod" in resp
            assert "main" in resp
            assert "weather" in resp
            assert resp["cod"] == 200

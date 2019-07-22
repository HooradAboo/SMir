calendar = {"tasks": [{"tasks": ["Finish Project", ""], "task_list": "My Tasks"}],
            "weather": {"cod": 200, "wind": {"speed": 6.2, "deg": 140}, "dt": 1563779177,
                        "sys": {"sunrise": 1563759255, "sunset": 1563810423, "type": 1, "country": "IR",
                                "message": 0.0085, "id": 7464}, "clouds": {"all": 40}, "id": 112931,
                        "visibility": 10000, "base": "stations", "timezone": 16200, "name": "Tehran",
                        "weather": [{"main": "Clouds", "id": 802, "description": "scattered clouds", "icon": "03d"}],
                        "coord": {"lat": 35.7, "lon": 51.4},
                        "main": {"temp_max": 310.15, "humidity": 12, "temp_min": 310.15, "pressure": 1015,
                                 "temp": 310.15}}, "calendar": [{"date": "2019-07-23T15:30:00+04:30", "event": "Kish"}]}



print(calendar['weather'])
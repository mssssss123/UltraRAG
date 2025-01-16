import json
import aiohttp
from pathlib import Path
from loguru import logger

CITY_ID = (Path(__file__).parent / "cityId.json").as_posix()
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

class Weather:
    def __init__(self) -> None:
        self.url: str = 'http://aider.meizu.com/app/weather/listWeather?cityIds={area}'
        
        with open(CITY_ID, "r", encoding="utf8") as fr:
            city2id = json.load(fr)
        self.city2id = {item['countyname']: item['areaid'] for item in city2id}


    async def arun(self, area):
        area = area.strip().replace("市", "")
        city_id = self.city2id.get(area, "")
        url = self.url.format(area=city_id)
        logger.info(f"weather module requests url: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    response_json = await response.json()
                else:
                    raise ConnectionError(f"failed to connect {self.url} with {response.status_code}")
        try:
            answer = self.parase(response_json)
        except IndexError as e:
            answer = f"未查询到您所在地 {area} 的天气"
        return answer


    def parase(self, weather_data):
        city_info = weather_data["value"][0]
        city = city_info["city"]
        province = city_info["provinceName"]
        temp = city_info["realtime"]["temp"]
        sendible_temp = city_info["realtime"]["sendibleTemp"]
        weather = city_info["realtime"]["weather"]
        wind_dir = city_info["realtime"]["wD"]
        wind_speed = city_info["realtime"]["wS"]
        pm25 = city_info["pm25"]["pm25"]
        aqi = city_info["pm25"]["aqi"]
        air_quality = city_info["pm25"]["quality"]
        indexes = city_info["indexes"]
        
        # 输出基本天气信息
        text = f"当前城市：{province} {city}\n"
        text += f"实时温度：{temp}°C，体感温度：{sendible_temp}°C\n"
        text += f"天气：{weather}\n风向：{wind_dir}，风速：{wind_speed}\n"
        text += f"PM2.5：{pm25}，空气质量：{air_quality}（AQI: {aqi}）\n"
        
        # 输出各项指数
        text += "\n生活指数:\n"
        for index in indexes:
            text += f"- {index['name']}：{index['content']}（等级：{index['level']}）\n"
        
        return text


if __name__ == "__main__":
    import asyncio
    tools = Weather()
    print(asyncio.run(tools.arun("北京")))
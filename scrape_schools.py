import scrapy
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
import requests
import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import aiofiles as aiof


def get_districts():
    s = requests.Session()
    r = s.request("POST", "http://122.170.12.200/SatsInfraAnalysis/ResultScreen/State")
    soup = BeautifulSoup(r.content, "html.parser")
    return [
        r.find("a").text
        for r in soup.find("div", {"id": "District"})
        .find("table", {"id": "dev-table"})
        .find_all("td", {"class": "left"})
    ]


async def get_districts_data(dis, s):
    with open(f"outputs//schoolstats_{dis}.csv", "w") as f:
        response = await s.post(
            "http://122.170.12.200/SatsInfraAnalysis/ResultScreen/District", data={"district": dis}
        )
        soup = BeautifulSoup(await response.text(), "html.parser")
        blocks = [
            r.find("a").text
            for r in soup.find("div", {"id": "Pass"})
            .find("table", {"id": "dev-table"})
            .find_all("td", {"class": "left"})
        ]
        for block in blocks:
            response = await s.post(
                "http://122.170.12.200/SatsInfraAnalysis/ResultScreen/Block",
                data={"district": dis, "block": block},
            )
            soup = BeautifulSoup(await response.text(), "html.parser")
            schools = [
                r.find("a").text
                for r in soup.find("div", {"id": "Paris"})
                .find("table", {"id": "dev-table"})
                .find_all("td", {"id": "dis"})
                if r.find("a").text.isdigit()
            ]
            for school in schools:
                try:
                    response = await s.post(
                        "http://122.170.12.200/SatsInfraAnalysis/ResultScreen/School",
                        data={"district": dis, "block": block, "school_id": school},
                    )
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    school_details = [
                        r for r in soup.find("table", {"id": "dev-table"}).find_all("tr")
                    ]
                    for det in school_details:
                        dts = [sk.find_all("td") for sk in school_details if sk.find_all("td")]
                        for dt in dts:
                            f.write(
                                str.join("|", [dis, block, school] + [t.text for t in dt]) + "\n"
                            )
                except:
                    print(f"In exception getting data for  {school}")
                    pass
            f.flush()


async def get_school_data(districts):
    async with ClientSession() as session:
        await asyncio.gather(*[get_districts_data(dis, session) for dis in districts])


def main():
    districts = get_districts()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_school_data(districts))
    loop.close()


if __name__ == "__main__":
    main()

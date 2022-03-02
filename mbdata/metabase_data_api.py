import json
import requests

from requests import Session
from typing import Dict, Any, List, Mapping, cast
from typing_extensions import Literal


TResultFormat = Literal["json"]
TArrayOfRows = List[Dict[str, Any]]


class MetabaseDataApi:
    _url: str = None
    _user: str = None
    _password: str = None

    def __init__(self, url: str, user: str, password: str) -> None:
        """

        Your description goes here

        :param url: Metabase api url
        :param user: Metabase username
        :param password: Metabase password

        :return: new MetabaseApi instance
        """
        self._url = url
        self._user = user
        self._password = password

    @property
    def url(self) -> str:
        return self._url.strip("/")

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def session(self) -> Session:
        payload = dict(username=self.user,
                       password=self.password)

        response = requests.post(f"{self.url}/api/session",
                                 data=json.dumps(payload),
                                 headers={"Content-Type": "application/json"})

        response.raise_for_status()

        json_body = response.json()

        json_body["X-Metabase-Session"] = json_body.pop("id")
        json_body["Content-Type"] = "application/json"

        session = requests.Session()

        session.headers.update(json_body)

        return session

    def get_card_data(self, card_id: str, export_format: TResultFormat = "json") -> TArrayOfRows:
        """POST /api/card/:card-id/query/:export-format

        Run the query associated with a Card, and return its results as a file in the specified format. Note that this expects the parameters as serialized JSON in the ‘parameters’ parameter.

        :param card_id: you can get the card ID from the card url. The integer is needed, not the whole name.
        :param export_format: json, rest is not documented
        :return: returns json array of rows

        """
        if export_format != "json":
            raise ValueError(export_format)

        end_point = f"api/card/{card_id}/query/{export_format}"


        response = self.session.post(f"{self.url}/{end_point}")

        response.raise_for_status()

        return cast(TArrayOfRows, response.json())


    def get_query_data(self, query: str, database_id: int = None, tags: Mapping[str, Any] = None, parameters: List[Any] = None) -> TArrayOfRows:

        """POST /api/dataset

        Send a query to metabase, get max 2k rows back. This endpoint suports the metabase frontend visualisations

        :param query: a valid sql query. Flavor depends on your database type.
        :param database_id: Metabase database id, you can find it in the URL when navigating to the connection.
        :param tags: not documented
        :param parameters: not documented
        :return: returns json array of rows
        """

        end_point = f"api/dataset"

        payload = {
            "type": "native",
            "native": {
                "query": query,
                "template-tags": tags or {}
            },
            "database": database_id,
            "parameters": parameters or []
        }

        response = self.session.post(f"{self.url}/{end_point}",
                                     json=payload)
        response.raise_for_status()

        json_body = response.json()

        rows = json_body["data"]["rows"]
        cols = [c.get("display_name") for c in json_body["data"]["cols"]]

        return [dict(zip(cols, row)) for row in rows]

    def export_from_query(self, query: str, database_id: int = None, export_format: str = "json", tags: Mapping[str, Any] = None) -> bytes:
        """POST /api/dataset/:export-format

        Send a query to metabase and get results. Max 1m rows. You can choose the format, suggested json.

        :param query: a valid sql query. Flavor depends on your database type.
        :param database_id: Metabase database id, you can find it in the URL when navigating to the connection.
        :param export_format: json, csv, or xlsx. For xslx you will probably want to write the contents to file.
        :param tags: not documented
        :return: Returns the file contents (eg, json export format returns json rows)
        """

        end_point = f"api/dataset/{export_format}"

        request_query = {
            "type": "native",
            "native": {
                "query": query,
                "template-tags": tags or {}
            },
            "database": database_id,
        }
        request_data = {
            "query": json.dumps(request_query)
        }

        s = self.session
        s.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

        response = s.post(url=f"{self.url}/{end_point}", data=request_data)
        response.raise_for_status()
        
        # return the content as a stream of bytes to be parsed by the caller
        return response.content


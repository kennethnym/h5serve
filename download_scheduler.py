import asyncio
from enum import Enum
from typing import Any, Optional
import aiohttp
from h5grove.fastapi_utils import os
from numpy import random


class DownloadRequestStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class DownloadRequest:
    def __init__(
        self, request_id: int, status: DownloadRequestStatus, path: str | None
    ) -> None:
        self.request_id = request_id
        self.status = status
        self.path = path

    def to_json(self) -> dict[str, Any]:
        return {
            "requestId": self.request_id,
            "status": self.status,
            "path": self.path,
        }


class DownloadScheduler:
    def __init__(self, http_client: aiohttp.ClientSession) -> None:
        self._pending_requests: dict[int, DownloadRequest] = {}
        self._http_client = http_client

    def _new_request_id(self) -> int:
        id = random.randint(0, 2147483647)
        while id in self._pending_requests:
            id = random.randint(0, 2147483647)

        return id

    def get_download_request(self, request_id: int) -> Optional[DownloadRequest]:
        try:
            return self._pending_requests[request_id]
        except KeyError:
            return None

    def schedule(self, session_id: str, datafile_id: str) -> DownloadRequest:
        request_id = self._new_request_id()
        request_params = {
            "sessionId": session_id,
            "datafileIds": datafile_id,
            "compress": "false",
        }
        download_request = DownloadRequest(
            request_id, status=DownloadRequestStatus.IN_PROGRESS, path=None
        )

        self._pending_requests[request_id] = download_request

        asyncio.ensure_future(self._start_download(request_params, request_id))

        return download_request

    async def _start_download(self, params: dict[str, str], request_id: int):
        request = self._pending_requests[request_id]

        if not request:
            return

        response = await self._http_client.get(
            "https://idsdev2.isis.cclrc.ac.uk:8181/ids/getData", params=params
        )

        cd = response.content_disposition
        if not cd:
            request.status = DownloadRequestStatus.ERROR
            return

        file_name = cd.filename
        if not file_name:
            request.status = DownloadRequestStatus.ERROR
            return

        request.path = file_name

        with open(request.path, "wb") as f:
            async for data in response.content.iter_any():
                f.write(data)

        request.status = DownloadRequestStatus.COMPLETE

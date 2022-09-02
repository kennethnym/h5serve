import os
import aiohttp
import fastapi
from fastapi import FastAPI, HTTPException
from h5grove.fastapi_utils import router, settings

from download_scheduler import DownloadScheduler

app = FastAPI()

# This configures the folders that contain hdf5 files to be served
settings.base_dir = os.path.abspath(os.path.join(".", "hdf5_files"))

# Include FastAPI router defined by h5groove
app.include_router(router)

app.state.http_client = aiohttp.ClientSession()
app.state.download_scheduler = DownloadScheduler(app.state.http_client)


@app.get("/request")
async def request(request: fastapi.Request):
    """
    An endpoint to request a datafile to be served by this server.
    After receiving a request, the server will begin downloading the datafile to hdf5_files.
    """

    session_id = request.query_params["sessionId"]
    datafile_id = request.query_params["datafileId"]

    download_scheduler: DownloadScheduler = request.app.state.download_scheduler

    return download_scheduler.schedule(session_id, datafile_id).to_json()


@app.get("/request/{request_id}")
async def request_status(request: fastapi.Request):
    request_id = request.path_params["request_id"]
    download_scheduler: DownloadScheduler = request.app.state.download_scheduler

    download_request = download_scheduler.get_download_request(int(request_id))

    if not download_request:
        raise HTTPException(status_code=404, detail="Request not found.")

    return download_request.to_json()

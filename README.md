# h5 serve
A FastAPI server that serves requested HDF5 files

## Prerequisites

- `poetry`
- Python `^3.10`

## How it works

It uses `h5groove`'s provided FastAPI router for interfacing with `@h5web/app`'s preview frontend.
However, it requires that the HDF5 files to be on the local filesystem of the server.

`h5serve` provides 2 additional endpoints, `POST /request` and `GET /request/{request_id}`.

`POST /request` is for requesting an HDF5 file to be previewed. The server will begin downloading the HDF5 file to `./hdf5_files/{name}`.
`GET /request/{request_id}` returns the request object, containing the status of the request, and the path to the HDF5 file relative to `./hdf5_files` when the request is complete.

Once the file has been downloaded, client can supply the file path returned by the server to `@h5web/app`. It can then interact with this server as normal.

## Running the server

1. `poetry install`
2. `poetry run uvicorn main:app --reload`
3. Server is now running on `localhost:8000`

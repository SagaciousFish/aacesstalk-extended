from uvicorn.workers import UvicornWorker

class DevelopmentWorker(UvicornWorker):
    CONFIG_KWARGS = dict(
        port="3000"
    )
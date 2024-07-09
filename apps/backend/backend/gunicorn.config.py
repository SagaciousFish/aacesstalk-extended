bind = "0.0.0.0:80"
workers = 1
proc_name = "aacesstalk_backend"
reload = False
worker_class = "uvicorn.workers.UvicornWorker"
accesslog="../../logs/access.log"
errorlog="../../logs/error.log"
daemon = True

def on_starting(server):
    print('Started master process of AACessTalk backend.')
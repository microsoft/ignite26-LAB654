import os

import uvicorn

from .app import build_app

if __name__ == "__main__":
    uvicorn.run(build_app(), host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "8000")),
                proxy_headers=True, forwarded_allow_ips="*")

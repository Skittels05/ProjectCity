from modules import api, utils
from modules.config import config_values
import uvicorn

if __name__ == "__main__":
    utils.print_logo()
    uvicorn.run(
        api.app,
        host="0.0.0.0",
        port=config_values.PORT,
        ssl_keyfile=config_values.SSL_KEYFILE,
        ssl_certfile=config_values.SSL_CERTFILE
    )

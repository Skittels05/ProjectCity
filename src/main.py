from modules import api, utils
import uvicorn

if __name__ == "__main__":
    utils.print_logo()
    uvicorn.run(api.app, host="0.0.0.0", port=8000)

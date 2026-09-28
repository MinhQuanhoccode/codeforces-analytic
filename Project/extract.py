import requests
import json
from config import HANDLE


def fetch_submissions (handle: str, count: int = 50) :
    url = "https://codeforces.com/api/user.status" #Public API của Codeforces
    params = {
        "handle": handle,
        "from": 1,
        "count": count,
    }

    response = requests.get(url, params=params, timeout= 10)
    ##HTTP LOI
    response.raise_for_status()

    data = response.json()

    ##API LOI
    if data["status"] != "OK":
        raise ValueError(f"API tra ve loi: {data}")
    return data["result"]

    ##Run
if __name__ == "__main__":
    submissions = fetch_submissions(HANDLE, count=10)
    print(json.dumps(submissions[0], indent=2, ensure_ascii=False))

    print(f"\nLay duoc {len(submissions)} submissions.")
    print("Cac key co trong 1 submission: ", list(submissions[0].keys()))
    for s in submissions:
        print(s["id"], s.get("verdict"), s["problem"]["name"])
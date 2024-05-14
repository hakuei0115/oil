import json, requests
from datetime import datetime
from fastapi import FastAPI, Request, Response
app = FastAPI()

class Scrape:
    def __init__(self, request_data):
        self.start_date = self._parse_date(request_data.get('start_date'))
        self.end_date = self._parse_date(request_data.get('end_date'))
        
    def _parse_date(self, date_str):
        try:
            if date_str:
                valid_date = datetime.strptime(date_str, "%Y-%m-%d")
                date_str = date_str.replace("-", "/")
                return date_str
        except ValueError as e:
            raise ValueError(f"Invalid date format. {str(e)}")
        return "init"
    
    def _process_data(self, data):
        formate_data = [];
        
        try:
            data = data.get("data", {}).get("gasoline", [])
            
            for item in data:
                formate_data.append({
                    'date': item.get('Date'),
                    "oil": {
                        "cpc": self._get_oil_detail(item, "A"),
                        "fpcc": self._get_oil_detail(item, "B"),
                    }
                })
            return {"result": formate_data}
        except KeyError as e:
            raise KeyError(f"Invalid data format. {str(e)}")
        
    def _get_oil_detail(self, i, prefix):
        return [
            {"title": "92無鉛汽油", "price": i.get(f"{prefix}92")},
            {"title": "95無鉛汽油", "price": i.get(f"{prefix}95")},
            {"title": "98無鉛汽油", "price": i.get(f"{prefix}98")},
            {"title": "超級/高級柴油", "price": i.get(f"{prefix}chai")}
        ]
    
    def get_result(self):
        files = {
            "start": self.start_date,
            "end": self.end_date
        }
        request = requests.post("https://www2.moeaea.gov.tw/oil111/Gasoline/RetailPrice/load", data=files)
        result = self._process_data(request.json())
        return result

@app.post('/oil_history')
async def oil_history(request: Request):
    try:
        request_data = await request.json()
        result = Scrape(request_data).get_result()
        return Response(content=json.dumps(result), media_type='application/json')
    except Exception as e:
        return Response(content=json.dumps({"error_msg": str(e)}), media_type='text/plain')
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="test:app", host="127.0.0.1", port=8000, reload=True)
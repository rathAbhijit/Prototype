import json

def build_code_update_event(code):
    return json.dumps({
        "type": "code_update",
        "payload": {
            "code": code
        }
    })

def parse_event(text_data):
    return json.loads(text_data)
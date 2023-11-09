import json
import logging
import mimetypes
import os
from typing import Tuple

import requests
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Indexing:
    def __init__(self):
        self.auth_url = os.getenv('AUTH_URL')
        self.app_client_id = os.getenv('APP_CLIENT_ID')
        self.app_client_secret = os.getenv('APP_CLIENT_SECRET')
        self.jwt_token = "MkxxN3lYcVZaWkpROElMVENBbFphSkd2Z3E4Og=="
        # self._get_jwt_token()

    def _get_jwt_token(self) -> str:
        """Connect to the server and get a JWT token."""
        token_endpoint = f"{self.auth_url}/oauth2/token"
        session = OAuth2Session(self.app_client_id, self.app_client_secret, scope="")
        # try:
        #     token = session.fetch_token(token_endpoint, grant_type="client_credentials")
        # except requests.exceptions.JSONDecodeError:
        #     print("JSONDecodeError: The API response is not in JSON format.")
        #     # Handle this case, such as logging the response content.
        # except requests.exceptions.RequestException as e:
        #     print(f"RequestException: {e}")
        #     # Handle other request-related exceptions
        token = session.fetch_token(token_endpoint, grant_type="client_credentials")
    
        return token["access_token"]
    
    def upload_file(self, customer_id: int, corpus_id: int, idx_address: str, uploaded_file, file_title: str) -> Tuple[requests.Response, bool]:
            """Uploads a file to the corpus."""
            # Determine the MIME type based on the file extension
            extension_to_mime_type = {
                '.txt': 'text/plain',
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                # ... add more mappings as needed
            }
            # file_extension = os.path.splitext(uploaded_file.name)[-1]
            mime_type = extension_to_mime_type.get('.pdf', 'application/octet-stream')

            post_headers = {
                "Authorization": f"Bearer {self.jwt_token}"
            }
            
            try:
                file = uploaded_file.read()  
                # file= open('.\vectara_employee_handbook-4524365135dc70a59977373c37601ad1.pdf', 'r').read()
                files = {"file": (file_title, file, mime_type)}
                response = requests.post(
                    f"https://{idx_address}/v1/upload?c={customer_id}&o={corpus_id}",
                    files=files,
                    headers=post_headers
                )
            
                if response.status_code != 200:
                    logging.error("REST upload failed with code %d, reason %s, text %s",
                                response.status_code,
                                response.reason,
                                response.text)
                    return response, False
                return response, True
            except Exception as e:
                logging.error("An error occurred while uploading the file: %s", str(e))
                return None, False
    
class Searching:
    def __init__(self):
        self.customer_id = os.getenv('CUSTOMER_ID')
        self.api_key = os.getenv('API_KEY')
    
    def send_query(self, corpus_id, query_text, num_results, summarizer_prompt_name, response_lang, max_summarized_results):
        api_key_header = {
            "customer-id": self.customer_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        data_dict = {
            # "query": [
            #     {
            #         "query": query_text,
            #         "num_results": num_results,
            #         "corpus_key": [{"customer_id": self.customer_id, "corpus_id": corpus_id}],
            #         'summary': [
            #             {
            #                 'summarizerPromptName': summarizer_prompt_name,
            #                 'responseLang': response_lang,
            #                 'maxSummarizedResults': max_summarized_results
            #             }
            #         ]
            #     }
            # ]

            
  "query": [
    {
      "query": query_text,
      "start": 0,
      "numResults": 5,
      "contextConfig": {
        "charsBefore": 30,
        "charsAfter": 30,
        "sentencesBefore": 3,
        "sentencesAfter": 3,
        "startTag": "<b>",
        "endTag": "</b>"
      },
      "corpusKey": [
        {
          "customerId": self.customer_id,
          "corpusId": 3,
          "semantics": "DEFAULT",
          "dim": [
            {
              "name": "string",
              "weight": 0
            }
          ],
          "metadataFilter": "part.lang = 'eng'",
          "lexicalInterpolationConfig": {
            "lambda": 0.5
          }
        }
      ],
      "rerankingConfig": {
        "rerankerId": 272725717
      },
      "summary": [
        {
          "summarizerPromptName": "string",
          "maxSummarizedResults": 0,
          "responseLang": "string"
        }
      ]
    }
  ]

        }

        payload = json.dumps(data_dict)

        response = requests.post(
            "https://api.vectara.io/v1/query",
            data=payload,
            verify=True,
            headers=api_key_header
        )

        if response.status_code == 200:
            print("Request was successful!")
            data = response.json()
            texts = [item['text'] for item in data['responseSet'][0]['response'] if 'text' in item]
            return texts
        else:
            print("Request failed with status code:", response.status_code)
            print("Response:", response.text)
            return None
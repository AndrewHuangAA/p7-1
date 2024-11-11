import os
import json
import pathlib
import requests
import response

class FuncClient(object):
    _instance = None
    ROOT = 'http://127.0.0.1:8080/usFunc/'
    DISTANCEMETHOD_URL= ROOT + "distance_method/" 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass

    def _send_request(self, url: str, request_body: str):

            response = requests.post("http://127.0.0.1:8000/token/", data={
            "username": 'admin',
            "password": 'user1234'
            })
            response_json = response.json()
            response_json
            #以上Secured API
            
            request_header = {
                "Authorization": f"Bearer {response_json['access']}", #Secured API
                "Content-Type"  : "application/json"
            }
            response = requests.post(url, data=json.dumps(request_body), headers=request_header)
            
            return response  
        
    def pairtrading_backtesting(self, params: dict, method:str)->dict:
        
            request_body = {
                "params" : params,
                "method":method
            }                       
            #调用内部方法 _send_request 发送请求，将 DISTANCEMETHOD_URL 作为请求地址，将 request_body 作为请求的内容。
            #response 是服务器的响应对象。
            response = self._send_request(self.DISTANCEMETHOD_URL, request_body)
            print('status_code',response.status_code)
            if response.status_code == 200:
                return response.json()['detail']
            
            elif response.status_code == 404:
                print("It has no trading pair found!")
                print(response.json()['msg'])
            else:
                print("Something wrong at get spreads, status code:", response.status_code)
                print(response.json()['msg'])
                
            return None  
        
         
        
        
        
        
        
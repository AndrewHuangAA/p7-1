from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.db import connection
import json
import datetime
import numpy as np
import pandas as pd
from pathlib import Path
import multiprocessing
from tqdm import tqdm
from tqdm import trange
from functools import partial
from itertools import permutations
from lib.strategy import load, stock

class ViewSetValidate(object):
    
    def check_params(self, payload: dict, required_params: list, valid_params: list) -> bool:

        # request body is empty
        if not payload:
            self.response = Response(data={"msg":"params is empty"})
            self.response.status_code = 402
            return False
        
        # request body contain invalid parameters
        invalid = set(payload.keys()) - set(valid_params)
        missing = set(required_params) - set(payload.keys())
        msg = ""
        
        # all parameters is valid
        if not invalid and not missing:
            for key in set(valid_params) - set(payload.keys()):
                payload[key] = None
            return True
        
        msg = msg + f"invalid parameters {invalid}" if invalid else msg
        msg = msg + f"required parameters {missing} is missing" if missing else msg
        self.response = Response(data={"msg":msg})        
        self.response.status_code = 402
        return False
    
    def validate_params(self, params) -> bool:
        return True
    
    def validate_method(self, method) -> bool:
        if method not in ['distance']:
            msg = "method must in ['distance']"
            self.response = Response(data={"msg":msg})
            self.response.status_code = 402
            return False
        return True

class PairTradingBacktestingViewSet(viewsets.ModelViewSet, ViewSetValidate):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = None
    parser_classes = (JSONParser,)
    response = None
    required_params = ["params", "method"]
    valid_params = ["params", "method"]
       
    def _validate(self, payload:dict) -> bool:
        
        return (self.check_params(payload, self.required_params, self.valid_params)) and (
                self.validate_params(payload['params'])) and (
                self.validate_method(payload['method']))
                
    def create(self, request):

        method = request.data.get("method")
        params = request.data.get("params")

        # check input 
        if not self._validate(request.data):
            return self.response
        
        results = {}
        if method =="distance":
            results = load(
                stock_name = str(params["stock_name"]), 
                sub_stock_name = str(params["sub_stock_name"]), 
                start_day = str(params["start_day"]), 
                end_day = str(params["end_day"]), 
                # window_size = int(params["window_size"]), 
                # n_times = int(params["n_times"]),
                )
        
            # object.run()        
            # results["trading_signals"] = dict(object.trading_signals)
            # results["exe_trading_signals"] = object.exe_trading_signals
            # results["daily_profits"] = object.daily_profits
            # results["total_values"] = object.total_values
            # results["entry_point"] = object.entry_point
            # results["exit_point"] = object.exit_point
            # results["spread"] = object.spread.reset_index().to_json(orient='records')
            # results["middle_line"] = object.rolling_mean.reset_index().to_json(orient='records')
            # results["upper_line"] = object.upper_line.reset_index().to_json(orient='records')
            # results["lower_line"] = object.lower_line.reset_index().to_json(orient='records')
    
            
        # results = json.dumps(results, indent=4, ensure_ascii=False)
        # results = json.loads(results)
        
        # # not found in database
        # if len(results) == 0:
        #     self.response = Response(data={"msg":"not found"})
        #     self.response.status_code = 404
        #     return self.response
        
        # self.response = Response(data={"msg":"Succeed", 'detail':results})  
        # self.response.status_code = 200
        # return self.response
    
        # 直接返回结果，而不需要多余的 JSON 序列化
        if not results:
            self.response = Response(data={"msg": "not found"}, status=404)
            return self.response
        
        self.response = Response(data={"msg": "Succeed", "detail": results}, status=200)
        return self.response


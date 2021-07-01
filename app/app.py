import uuid, os
import json
import re
from .heathcareDataModel import dataModel
from fastapi import FastAPI, HTTPException, BackgroundTasks

app=FastAPI() # creating fastapi object
healthcareDictList=[] # healthcareDictList will cotain records of all providers

# filling healthcareDictList using data.json file
if os.path.exists('data.json'):
    with open('data.json', 'r') as myfile:
        data=myfile.read()
    healthcareDictList=json.loads(data)

# if data.json is not present it is created and updated with each change in healthcareDictList
def writeinfile():
    with open("data.json", 'w') as data:
        json.dump([pn for pn in healthcareDictList], data)


@app.get("/")
def welcome() -> dict:
    return {"message": "Welcome to Healthcare provider system."}

@app.get("/healthcareDict")
def getAllProviders() -> dict:
    return {"providers": healthcareDictList}

@app.get("/healthcare/{providerID}")
def getprovider(providerID) -> dict:
    for data in healthcareDictList:
        if data["providerID"]==providerID:
            return {"providers": data}
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/healthcare")
async def addProvider(data:dataModel, background_task:BackgroundTasks) -> dict:
    error=""
    pattern=re.compile(r"[0-9]*")
    data_dict=data.dict()
    if len(data_dict["phone"]) == 10:
        isPhoneNo=pattern.match(data_dict["phone"])
        if not isPhoneNo:
            error+="phone number should be 10 digit number"
            raise HTTPException(status_code=400, detail=error) # bad request
    else:
        error+="phone number should be 10 digit number"
        raise HTTPException(status_code=400, detail=error) # bad request
    id=str(uuid.uuid4())
    data_dict["providerID"]=id
    healthcareDictList.append(data_dict)
    background_task.add_task(writeinfile) # runs the write opeartio on data.json in background asynchronously
    return {"meassage": "data has been added"}
    
@app.put("/healthcare/{providerID}")
async def updateProvider(providerID:str, DATA:dict, background_task:BackgroundTasks) -> dict:
    for data in healthcareDictList:
        if data["providerID"]==providerID:
            for key in DATA.keys():
                if key=="phone":
                    error=""
                    pattern=re.compile(r"[0-9]*")
                    if len(DATA["phone"]) == 10:
                        isPhoneNo=pattern.match(DATA["phone"])
                        if not isPhoneNo:
                            error+="phone number should be 10 digit number"
                            raise HTTPException(status_code=400, detail=error) # bad request
                    else:
                        error+="phone number should be 10 digit number"
                        raise HTTPException(status_code=400, detail=error)
                data[key]=DATA[key]  
            background_task.add_task(writeinfile)# runs the write opeartio on data.json in background asynchronously
            return {"meassage": f"data of provider {providerID} has been updated"}
    
    raise HTTPException(status_code=404, detail="Item not found")
    
       
@app.delete("/healthcare/{providerID}")
async def deleteProvider(providerID:str, background_task:BackgroundTasks) -> dict:
    for data in healthcareDictList:
        if data["providerID"]==providerID:
            healthcareDictList.remove(data)
            background_task.add_task(writeinfile)# runs the write opeartio on data.json in background asynchronously
            return {"meassage": f"data of provider {providerID} has been deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/healthcare")
async def deleteAllProvider(background_task:BackgroundTasks) -> dict:
    for data in healthcareDictList:
        healthcareDictList.remove(data)
    background_task.add_task(writeinfile)# runs the write opeartio on data.json in background asynchronously
    return {"meassage": "data of all provider has been deleted"}
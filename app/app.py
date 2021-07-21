import uuid, os
import shutil
import json
import re
from .heathcareDataModel import dataModel
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

imageFolder='/home/user1/PythonPrac/fastapi/pythonFlaskApi/img/'

app=FastAPI() # creating fastapi object

origins = [
    "http://127.0.0.1:5500",
    "localhost:5500"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



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

@app.get("/image/{providerID}")
def getImage(providerID):
    for data in healthcareDictList:
        if data["providerID"]==providerID:
            fullPath=os.path.join(imageFolder, data["image"])
            return FileResponse(fullPath)

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
    pattern=re.compile(r"[0-9]{10}")
    data_dict=data.dict()
    if len(data_dict["phone"]) == 10:
        isPhoneNo=pattern.match(data_dict["phone"])
        if not isPhoneNo:
            error+="phone number should be 10 digit number"
            return {"message":error}# bad request
    else:
        error+="phone number should be 10 digit number"
        return {"message":error} # bad request
    id=str(uuid.uuid4())
    data_dict["providerID"]=id
    healthcareDictList.append(data_dict)
    background_task.add_task(writeinfile) # runs the write opeartio on data.json in background asynchronously
    return {"message": "data has been added"}

@app.post("/uploadimage")
async def create_upload_file(file: UploadFile = File(...)):
    fullPath=os.path.join(imageFolder, file.filename)
    with open(f'{fullPath}', 'wb') as FILE:
        shutil.copyfileobj(file.file, FILE)
    return {"filename": file.filename}

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
                            return {"message":error} # bad request
                    else:
                        error+="phone number should be 10 digit number"
                        return {"message":error}
                data[key]=DATA[key]  
            background_task.add_task(writeinfile)# runs the write opeartio on data.json in background asynchronously
            return {"message": f"data of provider {providerID} has been updated"}
    
    return {"message":"Item not Found"}
    
       
@app.delete("/healthcare/{providerID}")
async def deleteProvider(providerID:str, background_task:BackgroundTasks) -> dict:
    for data in healthcareDictList:
        if data["providerID"]==providerID:
            healthcareDictList.remove(data)
            background_task.add_task(writeinfile)# runs the write opeartio on data.json in background asynchronously
            return {"message": f"data of provider {providerID} has been deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/healthcare")
async def deleteAllProvider(background_task:BackgroundTasks) -> dict:
    for data in healthcareDictList:
        healthcareDictList.remove(data)
    background_task.add_task(writeinfile)# runs the write opeartio on data.json in background asynchronously
    return {"message": "data of all provider has been deleted"}


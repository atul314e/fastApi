from pydantic import BaseModel
class dataModel(BaseModel):
    providerID=""
    active:bool=True
    name:str
    qualification:str
    speciality:str
    phone:str
    department:str="Not Applicable"
    organization:str
    location:str=""
    description:str=""
    image:str
    address:str
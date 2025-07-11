from pydantic import BaseModel


class UserNameDempgraphicAnalysisResponseModel(BaseModel):
    name_popularity: float
    surname_popularity: float
    males_name_popularity: float
    females_name_popularity: float
    males_surname_popularity: float
    females_surname_popularity: float

from typing import List
from pydantic import BaseModel, Field, ValidationError
import os
import re
import json
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import spacy

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

nlp = spacy.load("en_core_web_trf")

def clean_text(text):
    text = text.strip()# Remove unnecessary spaces at the start and end
    text = re.sub(r'\s+', ' ', text)# Reduce multiple spaces to one
    #text = re.sub(r'[^\x00-\x7F\s.,;!?\'"-]', '', text)  # Keep ASCII characters only
    text = text.lower()# Convert text to lowercase
    #text = re.sub(r'\b2[o0]2[i1]\b', '2021', text)# Fix "2o2i" or similar to "2021"
    #text = re.sub(r'\b(o)', '0', text)# Replace standalone "o" with "0" in years
    text = re.sub(r'\n\s*\n', '\n', text)# Remove blank lines
    return text

#on definie le model de base dans une class
class ResumeData(BaseModel):
    names: List[str] = Field(default_factory=list)
    occupations: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    educations: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    orgs: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    percentages: List[str] = Field(default_factory=list)
    monetary_values: List[str] = Field(default_factory=list)
    quantities: List[str] = Field(default_factory=list)
    works_of_art: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    laws: List[str] = Field(default_factory=list)
    ordinals: List[str] = Field(default_factory=list)
    cardinals: List[str] = Field(default_factory=list)

pdf_path = r'C:\Users\HP\Desktop\CV_NORMALIZER\Stockholm-Resume-Template-Simple.pdf'

images = convert_from_path(pdf_path)#convertir pdf en image

# Extract text from each image using Tesseract OCR
text = ""
for i, image in enumerate(images):
    page_text = pytesseract.image_to_string(image, lang='eng')
    text += page_text

cleaned_text = clean_text(text)#apres l'extraction, on nettoie le texte

doc = nlp(cleaned_text)
#on definit le dict ou on va inserer les entites
raw_data = {
    "names": [],
    "occupations": [],
    "languages": [],
    "educations": [],
    "interests": [],
    "orgs": [],
    "locations": [],
    "products": [],
    "dates": [],
    "percentages": [],
    "monetary_values": [],
    "quantities": [],
    "works_of_art": [],
    "events": [],
    "laws": [],
    "ordinals": [],
    "cardinals": []
}
#il  faut definir les entites qu'il sait pas deja 
occupation_keywords = ["engineer", "developer", "designer", "manager", "scientist", "analyst"]
education_keywords = ["degree", "university", "college", "bachelor", "master", "phd", "diploma"]
interest_keywords = ["sports", "music", "arts", "reading", "traveling", "movies", "coding"]

# Process named entities to extract relevant information
for ent in doc.ents:
    if ent.label_ == "PERSON":
        raw_data["names"].append(ent.text)
    if ent.label_ == "ORG" or any(keyword in ent.text.lower() for keyword in education_keywords):
        raw_data["educations"].append(ent.text)
    if ent.label_ == "LANGUAGE":
        raw_data["languages"].append(ent.text)
    if ent.label_ == "ORG":
        raw_data["orgs"].append(ent.text)
    if ent.label_ in ["GPE", "LOC"]:
        raw_data["locations"].append(ent.text)
    if ent.label_ == "PRODUCT":
        raw_data["products"].append(ent.text)
    if ent.label_ == "DATE":
        raw_data["dates"].append(ent.text)
    if ent.label_ == "PERCENT":
        raw_data["percentages"].append(ent.text)
    if ent.label_ == "MONEY":
        raw_data["monetary_values"].append(ent.text)
    if ent.label_ == "QUANTITY":
        raw_data["quantities"].append(ent.text)
    if ent.label_ == "WORK_OF_ART":
        raw_data["works_of_art"].append(ent.text)
    if ent.label_ == "EVENT":
        raw_data["events"].append(ent.text)
    if ent.label_ == "LAW":
        raw_data["laws"].append(ent.text)
    if ent.label_ == "ORDINAL":
        raw_data["ordinals"].append(ent.text)
    if ent.label_ == "CARDINAL":
        raw_data["cardinals"].append(ent.text)

# Manually parse interests based on keywords
for token in doc:
    if token.text.lower() in interest_keywords:
        raw_data["interests"].append(token.text)
for token in doc:
    if token.text.lower() in occupation_keywords:
        raw_data["occupations"].append(token.text)

# Remove duplicates by converting to a set
for key in raw_data:
    raw_data[key] = list(set(raw_data[key]))

# Validate and organize data using Pydantic
try:
    validated_data = ResumeData(**raw_data)
    json_data = validated_data.model_dump_json(indent=4)  # Convert to JSON
    print(json_data)

    # Optionally, save the JSON to a file
    with open("validated_extracted_data.json", "w") as json_file:
        json_file.write(json_data)

except ValidationError as e:
    print("Validation Error:", e)




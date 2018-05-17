
from azure.cognitiveservices.vision.customvision.training import training_api
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import prediction_endpoint
from azure.cognitiveservices.vision.customvision.prediction.prediction_endpoint import models

import os
import sys
import json, requests
import time


azure_region = "southcentralus"
training_key = "your training key"  # from settings pane on customvision.ai
prediction_key =  "your prediction key"  #

project_name = ""
tagname = ""
imageFile = ""


# what the args should look like
'''
dowhat = "train" #predict" | "uppload" | "train" | 
project_name = "newapi"

tagname = "Cat"
imagefolder = ".\\images\\cats"

dowhat = "predict" 
imageFile = "./133-0.jpg"
project_name = 'gearhack'
'''
if (len(sys.argv)>0):
    dowhat = sys.argv[1]
    project_name = sys.argv[2]
if (len(sys.argv)> 2):
    if (len(sys.argv)< 4):
        print('usage: vtest.py upload|train [project_name, tagename, imagefolder]')
    else: 
        if (dowhat=="predict"):
            imageFile = sys.argv[3]
        else:
            tagname = sys.argv[3]
            imagefolder = sys.argv[4]
            print(f' {dowhat} project_name: {project_name}, tagename: {tagname}, imagefolder: {imagefolder}')



# Check if the project with project_name exists and if not create ir
project_id = ""
trainer = training_api.TrainingApi(training_key)
projects = trainer.get_projects()

for projectx in projects:
    if (projectx.name == project_name):
        project_id = projectx.id
        project = projectx

if (project_id==""):
    print(f'project {project_name} not found, creating it')
    project = trainer.create_project(project_name)
    project_id = project.id
else:
    print(f'project found id = {project.id}')



def upload_images():
# method for uploading images    
    print (f'{project_id}')
    alltags = trainer.get_tags(project_id)

    # get the tag id if the tag exsts otherwise create a tag and get the id
    tagExists = False
    for i in range(0,len(alltags.tags)):
        if (alltags.tags[i].name == tagname):
            tagExists = True
            tagid = alltags.tags[i].id
            break
    if (tagExists == False):
        tagid = trainer.create_tag(project_id, tagname).id
    #print (f'{tagid}')

    # iterate over the folder and upload a file at a time
    for filename in os.listdir(imagefolder):
        print (f'adding training image: {filename} with tag: {tagid}')
        imagefile = imagefolder + "\\" + filename
        with open(imagefile, mode="rb") as img_data: 
            trainer.create_images_from_data(project_id, img_data.read(), [ tagid ])

# if upload is requested
if (dowhat=="upload"):
    upload_images()

# if training is requested
if (dowhat=="train"):
    try: 
        iteration_id = trainer.train_project(project_id).id
        iteration = trainer.get_iteration(project.id, iteration_id)
        while (iteration.status == "Training"):
            iteration = trainer.get_iteration(project.id, iteration.id)
            print ("Training status: " + iteration.status)
            time.sleep(1)
        print ("Training Completed")
    except Exception as e:      
        print("[Errno {0}]".format(e))
        print("Training can be initited only when thers is new content since last training")
        print("Also to train there must be a minimum of 2 Tags and minimum 5 omages per Tag")
   

# if prediction is requested
if (dowhat=="predict"):
    iterations = trainer.get_iterations(project_id)
    # we are using the first iteration but you can select any iteration as necessary
    iteration_id = iterations[0].id

    host = "https://southcentralus.api.cognitive.microsoft.com/customvision/v2.0/Prediction/"
    
    

    headers = {"Prediction-key":prediction_key}

    # if the filename is specified for prediction
    if (imageFile != ""):
        predictor = prediction_endpoint.PredictionEndpoint(prediction_key)
        path = project_id+"/image/?iterationId="+iteration_id
        predictionUrl = host + path
        print (f'Prediction URL: {predictionUrl}')
        
        with open(imageFile, mode="rb") as test_data:
            #iteration_id = "Iteration 1"
            print (f'project id: {project_id}   iteration id: {iteration_id}')
            imagedata = test_data.read()
            response = requests.post(predictionUrl, headers=headers, data=imagedata)
            responseJ = json.loads(response.text)
            predictions = responseJ['predictions']

            for prediction in predictions:
                print (f"Tag: {prediction['tagName']},  Probability: {prediction['probability']}")

    # this is hardcoded URL to show how to use URL instead of a local file
    else:
        path = project_id+"/url/?iterationId="+iteration_id
        predictionUrl = host + path
        print (f'Prediction URL: {predictionUrl}')
        # this is the URL to the image that you want to get the prediction on
        jsonObj = {"Url":"http://1.bp.blogspot.com/-FTKHZ2sZOvY/TeH0DyNO4II/AAAAAAAAA4w/ihIseEnfaac/s1600/Funny-Dog.jpg"}
        
        # anpther test image from ESRI collection
        # jsonObj = {"Url":"https://services.arcgis.com/b6gLrKHqgkQb393u/ArcGIS/rest/services/PhotoSurvey_PropertyCondition/FeatureServer/0/58/attachments/105"}

        response = requests.post(predictionUrl, headers=headers, json=jsonObj)
        responseJ = json.loads(response.text)
        predictions = responseJ['predictions']

        for prediction in predictions:
            print (f"Tag: {prediction['tagName']},  Probability: {prediction['probability']}")

    ##### The following code is using the python sdk (as is the code above) but it's not working
    ##### so for now we are making direct REST calls to Custom Vision
    #predictor = prediction_endpoint.PredictionEndpoint(prediction_key)
    #test_img_url = "http://1.bp.blogspot.com/-FTKHZ2sZOvY/TeH0DyNO4II/AAAAAAAAA4w/ihIseEnfaac/s1600/Funny-Dog.jpg"
    #results = predictor.predict_image_url(project_id, iteration_id, url=test_img_url)
    #with open(".\\images\\Test\\dog1test.jpg", mode="rb") as test_data:
    #    #iteration_id = "Iteration 1"
    #    print (f'project id: {project_id}   iteration id: {iteration_id}')
    #    imagedata = test_data.read()
    #    result = predictor.predict_image(project_id, imagedata, iteration_id)
    #    for prediction in result.predictions:
    #        print("\t" + prediction.tag + ": {0:.2f}%".format(prediction.probability * 100))


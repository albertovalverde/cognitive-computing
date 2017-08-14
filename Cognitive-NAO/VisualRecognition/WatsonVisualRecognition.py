import json, time, pprint, pickle
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3 as VisualRecognition

class VisRecHandler:
    def __init__(self, credentials, config):
	
	print credentials["api_key"]
        self.version = credentials["version"] # Release date of the desired API version. Specify dates in YYYY-MM-DD format. REQUIRED.
        self.api_key = credentials["api_key"] # The API key. Required.
        self.visual_recognition = VisualRecognition(self.version, api_key=self.api_key)
        self.classifier_ID = open('Resources/Visual Recognition/ListOfVrClassifiers.csv', 'r').readlines()[0].split(',')[1]
        self.numToReturn = config["vrNumToReturn"]
        self.threshold = config["vrConfThreshold"]

        self.printClassCreationSuccess()

    def printClassCreationSuccess(self):
        print "\nVisual recognition class successfully initialised.\n"

    def identifyPicture(self, image_file):
        start_time = time.time()
        with open(join(dirname(__file__), ".." + image_file), 'rb') as image_file:
            visualRecognitionResponse = self.visual_recognition.classify(images_file=image_file)

        # print json.dumps(visualRecognitionResponse, indent=2)

        top_classification = visualRecognitionResponse["images"][0]["classifiers"][0]["classes"][0].get("class", "Unknown")
        top_confidence = round(visualRecognitionResponse["images"][0]["classifiers"][0]["classes"][0].get("score", 0)*100, 0)
        all_classifications = visualRecognitionResponse["images"][0]["classifiers"][0]["classes"]

        time_elapsed = round(time.time() - start_time, 1)

        identifiedPicture = {
        'top_confidence': top_confidence,
        'top_classification': top_classification,
        'time_elapsed': time_elapsed,
        'all_classifications': all_classifications
        }

        return identifiedPicture

    def identifyCustomClassifier(self, image_file):
        start_time = time.time()
        with open(join(dirname(__file__), ".." + image_file), 'rb') as image_file:
            identifiedPicture = self.visual_recognition.classify(images_file=image_file, classifier_ids=self.classifier_ID, threshold=self.threshold)
        print json.dumps(identifiedPicture, indent=2)
        time_elapsed = round(time.time() - start_time, 1)

        if identifiedPicture["images"][0]["classifiers"]:
            list_length = min(len(identifiedPicture["images"][0]["classifiers"][0]["classes"]), self.numToReturn)

            results = range(list_length)
            classification_list = range(list_length)
            confidence_list = range(list_length)

            for i in range(list_length):
                classification = identifiedPicture["images"][0]["classifiers"][0]["classes"][i]["class"]
                confidence = round(identifiedPicture["images"][0]["classifiers"][0]["classes"][i]["score"]*100, 1)
                # print "Classification is", classification
                # print "Corresponding confidence is", confidence
                results[i] = [classification, confidence]

        for i in range(list_length):
            classification_list[i] = results[i][0]
            confidence_list[i] = results[i][1]
        top_result_index = max(xrange(len(confidence_list)), key=confidence_list.__getitem__)

        top_classification = classification_list[top_result_index]
        top_confidence = confidence_list[top_result_index]

        identifiedPicture = {
        'top_confidence': top_confidence,
        'top_classification': top_classification,
        'time_elapsed': time_elapsed#,
        # 'all_classifications': all_classifications
        }
        return identifiedPicture

    def recogniseText(self, image_file):
        start_time = time.time()
        with open(join(dirname(__file__), ".." + image_file), 'rb') as image_file:
            visualRecognitionResponse = self.visual_recognition.recognize_text(images_file=image_file)

        # print json.dumps(visualRecognitionResponse, indent=2)
        
        text = visualRecognitionResponse["images"][0]["text"].split("\n")

        time_elapsed = round(time.time() - start_time, 1)

        identifiedPicture = {
        "text": text,
        "time_elapsed": time_elapsed
        }
        return identifiedPicture

    def recogniseFaces(self, image_file):
        start_time = time.time()
        with open(join(dirname(__file__), ".." + image_file), 'rb') as image_file:
            visualRecognitionResponse = self.visual_recognition.detect_faces(images_file=image_file)
        print(json.dumps(visualRecognitionResponse, indent=2))
        # .json response contains faces, which contains 'age', 'face_location', 'gender'. It will contain 'identity' if it recognises the person (e.g. in case of famous persons).
        time_elapsed = round(time.time() - start_time, 1)

        identifiedPicture = {
        "time_elapsed": time_elapsed
        }
        identifiedPicture["person_recognised"] = visualRecognitionResponse["images"][0].get("faces", 0)
        try:
            identifiedPicture["identity_recognised"] = visualRecognitionResponse["images"][0]["faces"][0].get("identity", 0)
        except:
            identifiedPicture["identity_recognised"] = 0

        if identifiedPicture["person_recognised"]:
            faces = visualRecognitionResponse["images"][0]["faces"][0]
            identifiedPicture["age"] = faces["age"] # contains min, max, score. Will not necessarily contain min if it is a very young person.
            identifiedPicture["age_min"] = faces["age"].get("min", 0)
            identifiedPicture["age_max"] = faces["age"].get("max", 120)
            identifiedPicture["gender"] = faces["gender"].get("gender", "genderless person")
            identifiedPicture["gender_confidence"] = round(faces["gender"]["score"]*100, 0)

        if identifiedPicture["identity_recognised"]:
            identifiedPicture["identity"] = faces["identity"]["name"]
            identifiedPicture["identity_confidence"] = round(faces["identity"]["score"]*100, 0)
            identifiedPicture["identity_hierarchy"] = faces["identity"]["type_hierarchy"].split('/')[1:]

        return identifiedPicture

# Printing a .json
# print(json.dumps(visualRecognitionResponse, indent=2))

# RESPONSE FOR FACIAL Recognition
# {
#     "images": [
#         {
#             "faces": [
#                 {
#                     "age": {
#                         "max": 54,
#                         "min": 45,
#                         "score": 0.372036
#                     },
#                     "face_location": {
#                         "height": 75,
#                         "left": 256,
#                         "top": 93,
#                         "width": 67
#                     },
#                     "gender": {
#                         "gender": "MALE",
#                         "score": 0.99593
#                     },
#                     "identity": {
#                         "name": "Barack Obama",
#                         "score": 0.989013,
#                         "type_hierarchy": "/people/politicians/democrats/barack
# obama"
#                     }
#                 }
#             ],
#             "image": "prez.jpg"
#         }
#     ],
#     "images_processed": 1
# }
# }

# RESPONSE FOR TEXT MATCHING
# {
#     "images": [
#         {
#             "resolved_url": "https://raw.githubusercontent.com/watson-developer-cloud/doc-tutorial-downloads/master/visual-recognition/sign.jpg",
#             "source_url": "https://github.com/watson-developer-cloud/doc-tutorial-downloads/raw/master/visual-recognition/sign.jpg",
#             "text": "notice\nincreased\ntrain traffic",
#             "words": [
#                 {
#                     "line_number": 0,
#                     "location": {
#                         "height": 32,
#                         "left": 210,
#                         "top": 124,
#                         "width": 79
#                     },
#                     "score": 0.989161,
#                     "word": "notice"
#                 },
#                 {
#                     "line_number": 1,
#                     "location": {
#                         "height": 33,
#                         "left": 192,
#                         "top": 159,
#                         "width": 124
#                     },
#                     "score": 0.985497,
#                     "word": "increased"
#                 },
#                 {
#                     "line_number": 2,
#                     "location": {
#                         "height": 26,
#                         "left": 172,
#                         "top": 206,
#                         "width": 64
#                     },
#                     "score": 0.98167,
#                     "word": "train"
#                 },
#                 {
#                     "line_number": 2,
#                     "location": {
#                         "height": 32,
#                         "left": 243,
#                         "top": 195,
#                         "width": 101
#                     },
#                     "score": 0.993642,
#                     "word": "traffic"
#                 }
#             ]
#         }
#     ],
#     "images_processed": 1
# }

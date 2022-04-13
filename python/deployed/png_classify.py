

import cv2
from image_classifier import ImageClassifier
from image_classifier import ImageClassifierOptions


def sorting_hat(model: str, max_results: int, num_threads: int, enable_edgetpu: bool,image):
    
    # Initialize the image classification model
    options = ImageClassifierOptions(num_threads=num_threads,max_results=max_results,enable_edgetpu=enable_edgetpu)
    classifier = ImageClassifier(model, options)

    # List classification results
    categories = classifier.classify(image)
    # Show classification results on the image
    
    top_score = 0
    class_name = ''
    
    for idx, category in enumerate(categories):
        
        score = round(category.score, 2)
        if (score > top_score):
            class_name = category.label
            top_score = score
        
    result_text = class_name[:-4] + ' ' + str(top_score)
    if (top_score < 0.7):
        result_text = 'unsure'
    text_location = (2, 96)
    cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
              1, (0,0,0), 1)


    return image
    


def main():
    
    png = cv2.imread('weevil.png')

    image = sorting_hat('model.tflite', int(2), int(2),
      bool(False), png)
    
    cv2.imshow('image_classification', image)
    cv2.waitKey()


if __name__ == '__main__':
  main()

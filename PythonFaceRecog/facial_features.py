import cv2
import numpy as np
from skimage.color import rgb2lab
import dlib

class FacialFeatureAnalyzer:
    def __init__(self):
        # Initialize dlib's face detector and facial landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
    def analyze_image(self, image_path):
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not read the image")
        
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = self.detector(rgb_image)
        if len(faces) == 0:
            raise ValueError("No faces detected in the image")
        
        # Get the first face
        face = faces[0]
        
        # Get facial landmarks
        landmarks = self.predictor(rgb_image, face)
        
        # Analyze features
        features = {
            'skin_color': self._analyze_skin_color(rgb_image, landmarks),
            'eye_color': self._analyze_eye_color(rgb_image, landmarks),
            'hair_color': self._analyze_hair_color(rgb_image, face),
            'hair_length': self._analyze_hair_length(landmarks),
            'complexion': self._analyze_complexion(rgb_image, landmarks)
        }
        
        return features
    
    def _analyze_skin_color(self, image, landmarks):
        # Get skin region (cheeks)
        left_cheek = self._get_region(image, landmarks, 1, 2, 3)
        right_cheek = self._get_region(image, landmarks, 13, 14, 15)
        
        # Average the colors
        skin_color = np.mean([left_cheek, right_cheek], axis=0)
        return self._get_color_name(skin_color)
    
    def _analyze_eye_color(self, image, landmarks):
        # Get eye regions
        left_eye = self._get_region(image, landmarks, 36, 37, 38, 39, 40, 41)
        right_eye = self._get_region(image, landmarks, 42, 43, 44, 45, 46, 47)
        
        # Average the colors
        eye_color = np.mean([left_eye, right_eye], axis=0)
        return self._get_color_name(eye_color)
    
    def _analyze_hair_color(self, image, face):
        # Get hair region (top of head)
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        hair_region = image[max(0, y-h//4):y, x:x+w]
        
        if hair_region.size == 0:
            return "Unknown"
            
        hair_color = np.mean(hair_region, axis=(0,1))
        return self._get_color_name(hair_color)
    
    def _analyze_hair_length(self, landmarks):
        # Estimate hair length based on face proportions
        face_height = landmarks.part(8).y - landmarks.part(27).y
        hair_top = landmarks.part(27).y - face_height//4
        
        if hair_top < 0:
            return "Short"
        else:
            return "Long"
    
    def _analyze_complexion(self, image, landmarks):
        # Analyze skin texture and color variation
        skin_region = self._get_region(image, landmarks, 1, 2, 3, 13, 14, 15)
        lab_image = rgb2lab(skin_region.reshape(1, -1, 3))
        l_channel = lab_image[:, :, 0]
        
        # Calculate standard deviation of lightness
        std_dev = np.std(l_channel)
        
        if std_dev < 5:
            return "Smooth"
        elif std_dev < 10:
            return "Normal"
        else:
            return "Rough"
    
    def _get_region(self, image, landmarks, *indices):
        points = np.array([[landmarks.part(i).x, landmarks.part(i).y] for i in indices])
        x, y, w, h = cv2.boundingRect(points.astype(np.int32))
        return image[y:y+h, x:x+w]
    
    def _get_color_name(self, rgb_color):
        # Convert RGB to color names
        r, g, b = rgb_color
        
        if r > 200 and g > 200 and b > 200:
            return "Light"
        elif r < 50 and g < 50 and b < 50:
            return "Dark"
        elif r > g and r > b:
            return "Reddish"
        elif g > r and g > b:
            return "Greenish"
        elif b > r and b > g:
            return "Bluish"
        else:
            return "Mixed"

def main():
    analyzer = FacialFeatureAnalyzer()
    
    # Get image path from user
    image_path = input("Enter the path to the image: ")
    
    try:
        features = analyzer.analyze_image(image_path)
        print("\nFacial Features Analysis:")
        print("------------------------")
        for feature, value in features.items():
            print(f"{feature.replace('_', ' ').title()}: {value}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 
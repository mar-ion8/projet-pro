import cv2
chemin = r"C:\Users\ambri\Desktop\Master TELENVI\S3\PPro\projet_pro_telenvi_donnees\01_videos\DO Blum.insv"


cap = cv2.VideoCapture(chemin)
print(cap.isOpened())#doit afficher True
print(cap.get(cv2.CAP_PROP_FPS))

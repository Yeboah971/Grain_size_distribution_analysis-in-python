
import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io


img = cv2.imread("grains2.jpg", 0)

pixels_to_um = 0.5 # (1 px = 500 nm) 

#cropped_img = img[0:450, :]   #Crop the scalebar region
#no need for denoising 
#Otherwise, try Median or NLM
plt.hist(img.flat, bins=100, range=(0,255))

#Change the grey image to binary by thresholding. 
ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

cv2.imshow("Thresholded Image", thresh)
cv2.waitKey(0)

#Step 3: Clean up image, if needed (erode, etc.) and create a mask for grains

kernel = np.ones((3,3),np.uint8) 
eroded = cv2.erode(thresh,kernel,iterations = 1)
dilated = cv2.dilate(eroded,kernel,iterations = 1)

cv2.imshow("Threshold Image", thresh)
cv2.imshow("Dilated", dilated)
cv2.waitKey(0)


# Now, we need to apply threshold, meaning convert uint8 image to boolean.
mask = dilated == 255  #Sets TRUE for all 255 valued pixels and FALSE for 0
#print(mask)   #Just to confirm the image is not inverted.
#io.imshow(mask[250:280, 250:280])

#label each grain 
s = [[1,1,1],[1,1,1],[1,1,1]]
#label_im, nb_labels = ndimage.label(mask)
labeled_mask, num_labels = ndimage.label(mask, structure=s)

#The function outputs a new image that contains a different integer label

#Let's color the labels to see the effect
img2 = color.label2rgb(labeled_mask, bg_label=0)

cv2.imshow('Colored_Grains.jpg', img2)
cv2.waitKey(0)


#Measure the properties of each grain (object)

# regionprops function in skimage measure module calculates useful parameters for each object.

clusters = measure.regionprops(labeled_mask, img)  #send in original image for Intensity measurements
#print(clusters[0].perimeter)

#Can print various parameters for all objects
#for prop in clusters:
    #print('Label: {} Area: {}'.format(prop.label, prop.area))
    
#Output into a CSV file

propList = ['Area',
            'equivalent_diameter', #Added... verify if it works
            'orientation', #Added, verify if it works. Angle btwn x-axis and major axis.
            'MajorAxisLength',
            'MinorAxisLength',
            'Perimeter',
            'MinIntensity',
            'MeanIntensity',
            'MaxIntensity']    
    

output_file = open('image_measurements.csv', 'w')
output_file.write(',' + ",".join(propList) + '\n') #join strings in array by commas, leave first cell blank
#First cell blank to leave room for header (column names)

for cluster_props in clusters:
    #output cluster properties to the excel file
    output_file.write(str(cluster_props['Label']))
    for i,prop in enumerate(propList):
        if(prop == 'Area'): 
            to_print = cluster_props[prop]*pixels_to_um**2   #Convert pixel square to um square
        elif(prop == 'orientation'): 
            to_print = cluster_props[prop]*57.2958  #Convert to degrees from radians
        elif(prop.find('Intensity') < 0):          # Any prop without Intensity in its name
            to_print = cluster_props[prop]*pixels_to_um
        else: 
            to_print = cluster_props[prop]     #Reamining props, basically the ones with Intensity in its name
        output_file.write(',' + str(to_print))
    output_file.write('\n')
output_file.close()   #Closes the file, otherwise it would be read only. 

















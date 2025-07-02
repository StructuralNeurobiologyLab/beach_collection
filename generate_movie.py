import os
import cv2
import numpy as np
import moviepy

folder = 'Z:\\Jonas Hemesath\\beach_collection_videos\\1751371037'


def sort_images_naturally(fns):

    numbers = [int(fn.rstrip('.png').lstrip('image')) for fn in fns]

    new_list = []

    for x, y in zip(numbers, fns):
        new_list.append((x, y))

    new_list = sorted(new_list, key=lambda element: element[0])

    numbers_sorted, fns_sorted = [], []

    for x, y in new_list:
        numbers_sorted.append(x)
        fns_sorted.append(y)
    return fns_sorted

if not '\\' in folder:
    leica_path = 'images/' + folder + '/leica_cam/'
    pylon_path = 'images/' + folder + '/pylon_cam/'
else:
    leica_path = folder + '/leica_cam/'
    pylon_path = folder + '/pylon_cam/'

leica_fns = [img for img in os.listdir(leica_path) if img.endswith('png')]
pylon_fns = [img for img in os.listdir(pylon_path) if img.endswith('png')]

leica_images = [leica_path + img for img in sort_images_naturally(leica_fns)]
pylon_images = [pylon_path + img for img in sort_images_naturally(pylon_fns)]

duration_leica = os.stat(leica_images[-1]).st_ctime - os.stat(leica_images[0]).st_ctime
duration_pylon = os.stat(pylon_images[-1]).st_ctime - os.stat(pylon_images[0]).st_ctime

fps_leica = len(leica_images) / duration_leica
fps_pylon = len(pylon_images) / duration_pylon

#frame_size_leica = cv2.imread(leica_images[0]).shape
#frame_size_pylon = cv2.imread(pylon_images[0]).shape

#frame_template = np.zeros((frame_size_leica[0] + frame_size_pylon[0], frame_size_pylon[1], 3))
#fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#video = cv2.VideoWriter('images/'+folder+'/video.mp4', fourcc, fps, (frame_template.shape[1], frame_template.shape[0]), isColor=True)

#if not os.path.isdir('images/' + folder + '/merged'):
#    os.makedirs('images/' + folder + '/merged')
#merged_path = 'images/' + folder + '/merged/'

#for i, leica_image in enumerate(leica_images[0:100]):
#    print(i+1, 'of', len(leica_images))
#    leica_img = cv2.imread(leica_image)
#    pylon_img = cv2.imread(pylon_images[int(i/(len(leica_images) - 1) * (len(pylon_images) - 1))])
#    #print(pylon_img)
#
#    frame_template[0:frame_size_leica[0], 0:frame_size_leica[1], :] = leica_img
#    frame_template[frame_size_leica[0]:frame_size_leica[0]+frame_size_pylon[0], 0:frame_size_pylon[1], :] = pylon_img
#    #print(frame_template)
#    frame_template = frame_template
#    cv2.imwrite(merged_path + 'image' + str(i) + '.png', frame_template)
#    #cv2.imshow("image", frame_template)
#    #cv2.waitKey()
#    video.write(frame_template)
#image_files_pre = [img for img in os.listdir(merged_path) if img.endswith('png')]
#image_files = [merged_path + img for img in sort_images_naturally(image_files_pre)]
if not '\\' in folder:
    print('Generating leica movie')

    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(leica_images, fps=fps_leica)
    clip.write_videofile('images/'+folder+'/video_leica.mp4')

    print('Generating pylon movie')
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(pylon_images, fps=fps_pylon)
    clip.write_videofile('images/'+folder+'/video_pylon.mp4')

else:
    print('Generating leica movie')

    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(leica_images, fps=fps_leica)
    clip.write_videofile(folder + '/video_leica.mp4')

    print('Generating pylon movie')
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(pylon_images, fps=fps_pylon)
    clip.write_videofile(folder + '/video_pylon.mp4')

cv2.destroyAllWindows()







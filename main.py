import os
import sys
import cv2
import pickle
import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":
    args = sys.argv
    try:
        qid = int(args[1])
    except:
        print("Please input questionnaire ID.")
        exit()

    max_id = 16
    if (qid < 0) or (qid > max_id):
        print("ID must be 1 - %d"%(max_id))
        exit()

    ori_dir = os.path.join("images", "original")
    enc_dir = os.path.join("images", "encorded")
    ckpt_path = "ckpt.pickle"
    cont_dir = "contours"
    idl_dir = "id_lists"
    mask_dir = "masks"

    res_path = "results_%d.pickle"%(qid)
    if os.path.exists(res_path):
        print("You have already answered.")
        val = input("Are you sure answer the questionnaire again? [y/n]\n>> ")
        if val != "y":
            exit()   

    im_types = ["people", "ex"]
    im_nums = [50, 10]
    image_num = sum(im_nums)

    if os.path.exists(ckpt_path):
        with open(ckpt_path, "rb") as f:
            results = pickle.load(f)
            try:
                last_im_name = results[-1][0]
                last_im_type = last_im_name.split("_")[0]
                last_im_id = int(last_im_name.split("_")[1])
                resume = True
            except:
                resume = False
    else:
        results = []
        resume = False

    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10, 4))

    if resume:
        if last_im_id == im_nums[0]:
            start_type_id = 1
            start_im_id = 0
        else:
            start_type_id = im_types.index(last_im_type)
            start_im_id = last_im_id
    else:
        start_type_id = 0
        start_im_id = 0

    for type_id in range(start_type_id, len(im_types)):
        im_type = im_types[type_id]
        im_ids = im_nums[type_id]

        for im_id_ in range(start_im_id, im_ids):
            start_im_id = 0
            im_id = im_id_ + 1
            im_name = "%s_%d" % (im_type, im_id)

            img_ori = cv2.imread(os.path.join(ori_dir, "%s.jpg"%im_name))
            img_enc = cv2.imread(os.path.join(enc_dir, "%s.jpg"%im_name))

            with open(os.path.join(idl_dir, "%s.pickle"%(im_name)), "rb") as f:
                idl = pickle.load(f)

            with open(os.path.join(cont_dir, "%s.pickle"%(im_name)), "rb") as f:
                ctl = pickle.load(f)

            
            ax1.tick_params(
                labelbottom=False, labelleft=False, labelright=False, labeltop=False,
                bottom=False, left=False, right=False, top=False
                )
            ax2.tick_params(
                labelbottom=False, labelleft=False, labelright=False, labeltop=False,
                bottom=False, left=False, right=False, top=False
                )
            ax1.imshow(img_ori[:,:,::-1])
            ax2.imshow(img_enc[:,:,::-1])
            plt.tight_layout()
            plt.pause(0.01)

            image_id = im_id if im_type == "people" else im_id + im_nums[0]
            print("This is the picture No.%03d / %03d."%(image_id, image_num))

            ci = 0

            masks = np.zeros((len(idl) + 1, *img_ori.shape[:2]), dtype=np.bool)
            img1s = np.zeros((len(idl) + 1, *img_ori.shape), dtype=np.uint8)
            img1s[0,...] = img_ori.copy()

            while True:
                print("------------------------------------------")
                print("image %3d / %3d, number of ROI %3d / %3d"\
                % (image_id, image_num, ci, len(idl)))
                print("------------------------------------------")
                print(" n : Increase the number of ROI")
                print(" b : Decrease the number of ROI")
                print(" e : This number of ROI is the best")
                print(" i : Interrupt and save now state")
                print("------------------------------------------")
                val = input("Your answer >> ")

                if val == "e":
                    results.append([im_name, ci])
                    break

                elif val == "n":
                    if ci == len(idl):
                        print("Cannot increase the number of ROI.")
                        continue
                    else:
                        ci += 1
                        mask_img = cv2.imread(os.path.join(mask_dir, im_name, "mask_%d.png"%(idl[ci - 1])), cv2.IMREAD_GRAYSCALE).astype(np.bool)
                        masks[ci,:,:] = masks[ci-1,:,:] + mask_img
                        mask = np.tile(masks[ci,:,:], (3, 1, 1)).transpose(1, 2, 0)
                        img2 = np.where(mask > 0, img_ori, img_enc)
                        if np.all(img1s[ci,...] == 0):
                            img1s[ci,...] = cv2.drawContours(img1s[ci-1,...].copy(), ctl[idl[ci-1]], -1, (0, 0, 255), 3)                     

                elif val == "b":
                    if ci == 0:
                        print("Cannot decrease the number of ROI.")
                        continue
                    else:
                        ci -= 1
                        mask = np.tile(masks[ci,:,:], (3, 1, 1)).transpose(1, 2, 0)
                        img2 = np.where(mask > 0, img_ori, img_enc)

                elif val == "i":
                    with open(ckpt_path, "wb") as f:
                        pickle.dump(results, f)
                    print("Interrupted the questionnaire and save now results to 'ckpt.pickle'.")
                    exit()                

                else:
                    print("Please input 'n', 'b', or 'e'.")
                    continue
                
                ax1.imshow(img1s[ci,:,:,::-1])
                ax2.imshow(img2[:,:,::-1])
                plt.pause(0.01)

    with open(res_path, "wb") as f:
        pickle.dump(results, f)
    
    print("------------------------------------------")
    print("This questionnaire is completed.")
    print("Saved the result to 'results.pickle'.")
    print("Please submit this file to")
    print("https://www.dropbox.com/request/YuiPhxZhZH4NokBZqJ09")
    print("Thank you very much for your cooperation.")
    print("------------------------------------------")
            
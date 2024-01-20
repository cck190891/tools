import roboflow
import os
from multiprocessing.pool import ThreadPool
from tqdm import tqdm

class roboflow_multiupload(object):
    def __init__(self,project,dataset,thread=32,split_type=['valid','train','test'],num_retry_uploads=10) -> None:
        self.project=project
        self.dataset_path=dataset
        self.split_type=list(set(split_type) & set(os.listdir(dataset))) 
        self.upload_list=[]
        self.num_retry_uploads=num_retry_uploads
        self.thread=thread
        self.make_upload_list()
        self.go_pool()
        
    def make_upload_list(self):
        for split in self.split_type:
            image_path=os.path.join(dataset,split,'images')
            labels_path=os.path.join(dataset,split,'labels')
            for img in os.listdir(image_path):
                img_path = image_path + "/" + img
                filename=os.path.splitext(img)
                anno_path=labels_path + "/" + filename[0]+'.txt'
                self.upload_list.append([img_path,anno_path,split,self.num_retry_uploads])

    def single_upload_wrapper(self,single_params):
        #沒標記資料單純上傳影像
        if os.path.exists(single_params[1]):
            self.project.single_upload(
                image_path=single_params[0],
                annotation_path=single_params[1],
                split=single_params[2],
                num_retry_uploads=single_params[3],
            )
        else:
            self.project.single_upload(
                image_path=single_params[0],
                split=single_params[2],
                num_retry_uploads=single_params[3],
            )
        self.process_bar.update(1)

    def go_pool(self):
        pool=ThreadPool(self.thread)
        self.process_bar=tqdm(total=len(self.upload_list),desc='upload')
        pool.map(self.single_upload_wrapper,self.upload_list)
        pool.close()
        pool.join()
        self.process_bar.close()
    def __str__(self) -> str:
        print(len(self.upload_list))


if __name__=='__main__':
    #要儲存的位置與yolo資料集路徑
    #dataset---train
    #       |    |--images
    #       |    L--labels
    #       |--valid
    #       |    |--images
    #       |    L--labels
    #       L--test  
    #            |--images
    #            L--labels

    api_key="api-key"
    workspace='workspace-url'
    project='project-name'
    dataset='dataset_path'

    rf = roboflow.Roboflow(api_key=api_key)
    workspace=rf.workspace(workspace)
    project=workspace.project(project)
    roboflow_multiupload(project,dataset,thread=32,split_type=['valid','train','test'],num_retry_uploads=10)

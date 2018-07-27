
import os, shutil, collections

counter_dict = collections.defaultdict(int)

src_dir = {'train': './nlp/cnndata/train', 'test': './nlp/cnndata/test'}

# I use the new string formatting feature f-string in python v3,
# please change the format string according to your python version
for i in range(1, 6):
    os.mkdir('./nlp/cnndata/%s_train' % i)
    os.mkdir('./nlp/cnndata/%s_test' % i)

for tag, folder in src_dir.items():
    for file in os.listdir(folder):
        score = int(round(float(file.split('.txt')[0].split('_')[-1])))
        counter_dict['{0}_{1}'.format(score,tag)] += 1
        shutil.copy2('./{0}/{1}'.format(folder,file), './nlp/cnndata/{0}_{1}/{2}'.format(score,tag, file))

# defaultdict(<class 'int'>,
# {'2_train': 3019, '1_train': 2981, '5_train': 6000, '4_test': 1500, '2_test': 2000, '5_test': 500})
print(counter_dict)

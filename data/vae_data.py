import os
import torch

class TensorfileDataset():
    def __init__(self, opt, phase):
        self.opt = opt
        if opt.varying_length:
            self.datatensor = torch.load(os.path.join(opt.dataroot, f'{phase}.pt'))['data']
            self.datatensor = torch.cat(self.datatensor, dim = 0)
        else:
            if phase == 'train' and opt.missing_data_prob>=0 and opt.missing_data_prob<1:
                loaded = torch.load(os.path.join(opt.dataroot, f'{phase}_missing_{opt.missing_data_prob}.pt'))
                self.datatensor = loaded['data']
                self.mask = loaded['mask']
                
                # Remove masked image from the training data
                not_missing = []
                for i in range(self.datatensor.shape[0]):
                    for j in range(self.datatensor.shape[1]):
                        if torch.sum(self.datatensor[i][j]).item() > 0:
                            not_missing.append(self.datatensor[i][j].reshape(opt.n_channels, opt.isize*opt.isize))
                self.datatensor = torch.cat(not_missing, dim=0)
                
            else:
                self.datatensor = torch.load(os.path.join(opt.dataroot, f'{phase}.pt'))['data']
                    
        # Reshape data to the desired size
        self.datatensor = self.datatensor.reshape(-1, opt.n_channels, opt.isize, opt.isize).to(opt.device)
        
    
    def __len__(self):
        return self.datatensor.shape[0]

    def __getitem__(self, idx):      
        im = self.datatensor[idx]  
        sample = {'data': im}
        if self.opt.missing_data_prob>=0 and self.opt.missing_data_prob<1:
            sample['index'] = self.mask_nonzero[idx]
        return sample
        
        
def load_dataset(opt):
    dataset = {}
    for phase in opt.splits:
        dataset[phase] = TensorfileDataset(opt, phase=phase)
        print(f"{phase}: total number of images: {dataset[phase].datatensor.shape[0]}")
    print('>> Data loaded')
    return dataset
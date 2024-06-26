import pandas as pd
import numpy as np
from TSA.utils import print_red

def process_indata(data):
    def process_df(df):
        # take df, return numpy array, header and index (so that we can reconstruct the df later)
        arr = df.to_numpy()
        header = df.columns
        index = df.index
        scaling_factor = [max(abs(arr[:,i])) for i in range(arr.shape[1])]
        arr = arr / scaling_factor
        return arr, header, index, scaling_factor

    if isinstance(data, pd.DataFrame):
        return process_df(data)
    else:
        raise NotImplementedError('Data type not supported. Please provide a pandas DataFrame.')

def clusters_to_df(clusters:list, header, scaling_factors, ref_index=None, index_method:str='first'):
    if type(ref_index) not in [pd.Index, list, np.ndarray, range, pd.RangeIndex]:
        ref_index = range(clusters[-1]['original_indices'][-1]+1)
        print_red('Warning in clusters_to_df(): ref_index not provided - set to [0,1,2,..]')

    if index_method in ['first', 'last', 'all', 'span']:
        #build index from original_indices
        #if len(original_indices)>1, the make the index "{first_index}-{last_index}"
        built_index = []
        for cluster in clusters:
            i = cluster['original_indices']
            if index_method == 'first':
                ind = i[0] # index to use from ref_index
                built_index.append(ref_index[ind])
            elif index_method == 'last':
                built_index.append(i[-1])
                built_index.append(ref_index[ind])
            elif index_method == 'all':
                built_index.append(';'.join([str(ref_index[ind]) for ind in i]))
            elif index_method == 'span':
                if len(i)>1:
                    built_index.append(f'{ref_index[i[0]]}-{ref_index[i[-1]]}')
                else:
                    built_index.append(ref_index[i[0]])
    else:
        raise ValueError('Invalid index_method value. Please provide "first", "last", "all" or "span".')

    data = np.array([clusters[i]['centroid'] for i in range(len(clusters))])
    data = data*scaling_factors
        
    """if len(data)>len(index_method):
        index_method = range(len(data))
        print_red('Warning in process_outdata(): Index length does not match data length. Index set to range(len(data)).')"""

    return pd.DataFrame(data, columns=header, index=built_index)

def decompress_df(compressed_df:pd.DataFrame, weights=None):
    # If weights==None, the 'Weights' column is used
    # throw an error if 'Weights' column is not present
    if 'weights' not in compressed_df.columns.str.lower():
        if weights is None:
            raise ValueError('Weights column not found in compressed_df. Please provide weights as an argument.')
        else: 
            compressed_df['Weights'] = weights


    # Initialize an empty DataFrame with the same columns as agg_df
    decompressed_df = pd.DataFrame(columns=compressed_df.columns) # for plotting

    # Loop through each row in agg_df
    for index, row in compressed_df.iterrows():
        # Repeat the current row 'Weights' times and append to the decompressed_df
        # np.repeat creates an array of the index, repeated 'Weights' times
        repeated_rows = [row.values.tolist() for _ in range(int(row["Weights"]))]
        decompressed_rows = pd.DataFrame(repeated_rows, columns=compressed_df.columns)
        decompressed_df = pd.concat([decompressed_df, decompressed_rows], ignore_index=True)
    
    return decompressed_df

def process_outdata_array(data:np.ndarray, header, scaling_factor, index=None):
    if type(index) not in [pd.Index, list, np.ndarray, range]:
        index = range(len(data))
        print_red('Warning in process_outdata_array(): Index not provided. Index set to range(len(data)).')

    return pd.DataFrame(data*scaling_factor, columns=header, index=index)
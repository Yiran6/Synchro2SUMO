import pandas as pd
import numpy as np
import synchro_parser

class NodeIDMappingTable():

    def __init__(self, filename, synchro_df, parse_errors):
        transfer_id = pd.read_csv(filename)
        transfer_id = transfer_id[['sumoid','synchroid']].astype({'sumoid': str})
        missing_id = transfer_id[~transfer_id['synchroid'].isin(np.unique(synchro_df["Timeplans"]['INTID']))]
        
        for synchroid in missing_id['synchroid']:
            synchro_missing_info = synchro_parser.parseLanes(synchro_df, synchroid)
        parse_errors.append(f"synchro node {synchroid} not found in mapping table: {synchro_missing_info}")
            
        available_id = transfer_id[transfer_id['synchroid'].isin(np.unique(synchro_df["Timeplans"]['INTID']))]

        #make a convert list
        self.sumo2synchro = {}
        for sumoid in available_id['sumoid']:
            self.sumo2synchro[sumoid] = list(available_id['synchroid'][available_id['sumoid']==sumoid])[0]

        self.synchro2sumo = {}
        for sumoid in self.sumo2synchro:
            self.synchro2sumo[self.sumo2synchro[sumoid]] = sumoid
            
    def get_available_synchro_ids(self):
        return self.synchro2sumo.keys()
        
    def get_sumo_id(self, synchro_id):
        return self.synchro2sumo.get(synchro_id, None)
        
    def get_synchro_id(self, sumo_id):
        return self.sumo2synchro.get(sumo_id, None)        
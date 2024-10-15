import numpy as np
import synchro_parser
import pandas as pd
import phase_mapping
from phase_mapping import *
from sumo_xml_parser import SumoXmlParser
from synchro_sumo_id_mapping import NodeIDMappingTable

def read_translate_table(filename):
    transfer_id = pd.read_csv(filename)
    transfer_id = transfer_id[['sumoid','synchroid']].astype({'sumoid': str})
    return transfer_id


    
if __name__ == '__main__':
    #check the ids
    parse_errors = []
    
    # input paths here
    base_path = r"../SmallArterial/"
    transfer_file = base_path+"transfer_sigid.csv"
    synchro_csv_file = base_path+"test_arterial.csv"
    sumo_xml_file = base_path+"test_arterial.net.xml"
    
    output_file = base_path+'signal_additional2.add.xml'
    
    synchro_df = synchro_parser.parse_synchro_csv(synchro_csv_file)
    
    id_mapping = NodeIDMappingTable(transfer_file, synchro_df, parse_errors)

    #translate the dict we are interested

    available_synchro_ids = id_mapping.get_available_synchro_ids()
    sumo_data = SumoXmlParser(sumo_xml_file)
    
    synchro_signal_info = {}
    
    #available_synchro_ids =[id_mapping.get_synchro_id('2053744124')]
    for synchro_id in available_synchro_ids:
        
        sumo_id = id_mapping.get_sumo_id(synchro_id)
        synchro_signal_info[synchro_id] = synchro_parser.combine_synchro_dict(synchro_df, synchro_id)
        all_synchro_dirs = set(phase_mapping.extract_dir_info(synchro_signal_info[synchro_id]))
        
        traffic_directions = set(map(lambda s: s[0:2],all_synchro_dirs))
        print('\n', synchro_id, all_synchro_dirs, '\n')
        
        unique_inbound_edges = []
        for connection_index in sumo_data.sumo_signal_info[sumo_id].keys():
            sumo_movement = sumo_data.sumo_signal_info[sumo_id][connection_index]
            if ':' not in sumo_movement['fromEdge']  and sumo_movement['fromEdge'] not in unique_inbound_edges:
                unique_inbound_edges.append(sumo_movement['fromEdge'])

        if len(unique_inbound_edges) != len(traffic_directions):
            parse_errors.append(f"synchro node {synchro_id} does not have the same number of inbounds with SUMO {sumo_id}")
            continue
        '''
        print ("direction", all_synchro_dirs, unique_inbound_edges)
        inbound_direction_mapping = {}
        for edge_id in unique_inbound_edges:
            slope_info = sumo_data.sumo_nbsw[edge_id]
            possible_dir = phase_mapping.get_start_dir(slope_info, traffic_directions)
            print(slope_info, possible_dir)
            if possible_dir in traffic_directions:
                inbound_direction_mapping[edge_id]=possible_dir
                traffic_directions.remove(possible_dir)
        '''
        flag, inbound_direction_mapping = phase_mapping.direction_mapping(sumo_data, sumo_id, unique_inbound_edges, traffic_directions, parse_errors)
        if not flag:
            parse_errors.append(f"synchro node {synchro_id} map inbounds with SUMO {sumo_id} failed")
            continue
        for connection_index in sumo_data.sumo_signal_info[sumo_id].keys():    
            sumo_movement = sumo_data.sumo_signal_info[sumo_id][connection_index]

            if ':' not in sumo_movement['fromEdge']:
                if sumo_movement['fromEdge'] not in inbound_direction_mapping:
                    parse_errors.append(f"synchro node {synchro_id} match inbound failed")
                    break
                if sumo_movement['dir'] == 's': 
                    synchro_dir = 'T'
                else:
                    synchro_dir = sumo_movement['dir'].upper()
                sumo_movement["synchro_dir"] = inbound_direction_mapping[sumo_movement['fromEdge']]+synchro_dir
        print ("test", sumo_data.sumo_signal_info[sumo_id])
        
        for connection_index in sumo_data.sumo_signal_info[sumo_id].keys():    
            sumo_movement = sumo_data.sumo_signal_info[sumo_id][connection_index]
            if ':' in sumo_movement['fromEdge']:
                phase_mapping.process_pedestrian_crossing(sumo_id, sumo_data, sumo_movement, all_synchro_dirs, parse_errors)
        #print(sumo_data.sumo_signal_info[sumo_id])
        
    
    # Main Function: Run All Intersections
    control_type = {0:'static',1:'actuated', 2:'actuated', 3:'actuated'}

    validids = {}
    valid = 0
    all = 0
    
    with open(output_file, 'w') as f:
        f.writelines('<additional>\n')
        for id in available_synchro_ids:
            print("/tprocessing signal:", id)
            sumo_id = id_mapping.get_sumo_id(id)
            ret = createSignalTimingPlan(synchro_signal_info[id], sumo_data.sumo_signal_info[sumo_id]) 
            linkDur = buildlinkDuration(synchro_signal_info[id], sumo_data.sumo_signal_info[sumo_id])
            if ret:
                i = 0
                #for r in ret:
                #    print (i, r)
                #    i+=1
                #for s in synchro_signal_info[id]:
                #    print (' ', s, synchro_signal_info[id][s])
                #print(id, ret)
                for i in sumo_data.sumo_signal_info[sumo_id]:
                    print (sumo_data.sumo_signal_info[sumo_id][i])
                synchroid = id
                timeplans = synchro_df["Timeplans"]
                types =str(control_type[list(timeplans['DATA'][(timeplans['INTID']==synchroid) & (timeplans['RECORDNAME']=='Control Type')])[0]])
                offsets = str(list(timeplans['DATA'][(timeplans['INTID']==synchroid) & (timeplans['RECORDNAME']=='Offset')])[0])
                
                sumo_data.generateXml(f, sumo_id, ret, linkDur, types, int(float(offsets)))
                validids[id] = sumo_id
                valid += 1

            all +=1
        print (len(available_synchro_ids), all, valid)
        f.writelines('</additional>\n')
        
    #print(available_synchro_ids)
    
    print("\n".join(parse_errors))
    

import pandas as pd
from io import StringIO
from collections import OrderedDict
import numpy


# Specify the file path
file_path = r'C:\Program Files (x86)\Trafficware\Version10\Sample Files\Dual ring-P01.csv'
def parse_synchro_csv(file_path):
    # Initialize a dictionary to store DataFrames for each section
    dataframes = {}

    # Read the CSV file section by section
    with open(file_path, 'r') as file:
        current_section = None
        section_data = []

        for line in file:
            if line.startswith('[') and line.endswith(']\n'):
                if current_section:
                    # Create DataFrame for the current section
                    dataframes[current_section] = pd.read_csv(StringIO(''.join(section_data)), low_memory=False, skip_blank_lines=False, header=1)
                    section_data = []

                current_section = line.strip()[1:-1]
            else:
                section_data.append(line)

        # Create DataFrame for the last section
        if current_section:
            dataframes[current_section] = pd.read_csv(StringIO(''.join(section_data)), low_memory=False,skip_blank_lines=False, header=1)

    # Print the dataframes
    # print("Timeplans DataFrame:")
    # print(dataframes.keys())

    return dataframes
    
#transfer synchro csv
def parseSignal(synchro_df, intId):
    phases = synchro_df.get("Phases")
    #print(phases.columns)
    selected_data = ['BRP','MinGreen', 'MaxGreen', \
                     'Yellow', 'AllRed', 'Recall',\
                     'Walk', 'DontWalk', 'PedCalls']
    
    #get available phase
    phase_min_green = phases[(phases['RECORDNAME']=='MinGreen') & (phases['INTID']==intId)]
    phase_min_green = phase_min_green[phase_min_green.columns[~phase_min_green.isnull().all()]]
    if 'RECORDNAME' in phase_min_green:
        del phase_min_green['RECORDNAME']
    if 'INTID' in phase_min_green:
        del phase_min_green['INTID']
    
    phase_info = list(phase_min_green)
    result = {}
    
    for phs in phase_info:
       # print(phs)
        signal_data = list(phases[phs][(phases['RECORDNAME'].isin(selected_data)) & (phases['INTID']==intId)])
        res = dict(zip(selected_data, signal_data))
        result[phs] = {}
        result[phs] = res
    return(result)      

def parsePhases(signal_dict, intId):
    #signal_dict = parseSignal(synchro_df.get("Phases"), intId)
    phs = list(signal_dict.keys())
    print(signal_dict)     
    brp_dict = {}
    for i in phs:
        brp_dict[signal_dict[i]['BRP']] = i
    print (brp_dict.items())
    brp_dict = dict(OrderedDict(sorted(brp_dict.items())))
    
    brps = {}
    for brpinfo in brp_dict:
        brp_info = str(brpinfo)
        if brp_info[0] not in brps:
            brps[brp_info[0]] = {}
            brps[brp_info[0]][brp_info[1]] = []
            brps[brp_info[0]][brp_info[1]].append(brp_dict[int(brpinfo)])
        else:
            if brp_info[1] not in brps[brp_info[0]]:
                brps[brp_info[0]][brp_info[1]] = []
                brps[brp_info[0]][brp_info[1]].append(brp_dict[int(brpinfo)])
            else:
                brps[brp_info[0]][brp_info[1]].append(brp_dict[int(brpinfo)])
    
    return(brps)        

def parseLanes(synchro_df, intId):
    #print(intId)
    lanes_df = synchro_df.get("Lanes").copy()
    
    lanes_df = lanes_df[~lanes_df['INTID'].isnull()].astype({'INTID': int})
    #print(lanes_df)
    lanes_df = lanes_df[lanes_df['INTID']==intId]
    lanes_df.index = lanes_df['RECORDNAME']
    
    traffic_movement_data = {}
    inbound_nodes = {}
    need_lookup = []
    for traffic_movement in lanes_df.columns:

        if traffic_movement in ['RECORDNAME', 'INTID', 'PED', 'HOLD']:
            continue
            
        if not "Up Node" in lanes_df[traffic_movement]:
            continue
        val = lanes_df[traffic_movement][['Up Node']].astype("float")
        if numpy.isnan(val[0]):
            continue
        
        up_node = int(lanes_df[traffic_movement]['Up Node'])
        dest_node = int(lanes_df[traffic_movement]['Dest Node'])
        traffic_movement_data[traffic_movement] = {
            "UpNode": up_node,
            "DestNode": dest_node,
            "Lanes": lanes_df[traffic_movement]['Lanes'],
            "Protected": [],
            "Permitted": []
        }

        # Synchro may support up to 4 phases
        for i in range(1, 5):
            key = f'Phase{i}'
            
            if key in lanes_df.index:
                val = lanes_df[traffic_movement][[key]].astype("float")[0]
                if not numpy.isnan(val) and int(lanes_df[traffic_movement][key])>0:
                    traffic_movement_data[traffic_movement]["Protected"].append(f"D{int(lanes_df[traffic_movement][key])}")
                
            key = f'PermPhase{i}'
            
            if key in lanes_df.index:
                val = lanes_df[traffic_movement][[key]].astype("float")[0]
                if not numpy.isnan(val) and int(lanes_df[traffic_movement][key])>0:
                    traffic_movement_data[traffic_movement]["Permitted"].append(f"D{int(lanes_df[traffic_movement][key])}")
        
        if len(traffic_movement_data[traffic_movement]['Protected']) + len(traffic_movement_data[traffic_movement]['Permitted']) == 0:
            need_lookup.append([up_node, dest_node, traffic_movement])
        else:
            if up_node not in inbound_nodes:
                inbound_nodes[up_node] = [traffic_movement]
            else:
                inbound_nodes[up_node].append(traffic_movement)
    
    # Check if one way street
    total_lanes_per_bound = {}
    for movement in traffic_movement_data:
        bound = movement[0:2]
        if bound not in total_lanes_per_bound:
            total_lanes_per_bound[bound] = int(traffic_movement_data[movement]["Lanes"])
        else:
            total_lanes_per_bound[bound] += int(traffic_movement_data[movement]["Lanes"])
            
    
    phases = {}
    for pair in need_lookup:
        up_node =  pair[0]
        dest_node = pair[1]
        movement = pair[2]
        if total_lanes_per_bound[movement[0:2]] == 0:
            continue
        if (up_node in inbound_nodes):
            possible_list = inbound_nodes[up_node]
        elif (dest_node in inbound_nodes):
            possible_list = inbound_nodes[dest_node]
        else:
            print(f"did not found possible list for movement {movement} at node {intId}")
            continue
        if len(possible_list) == 0:
            print(f"did not found possible list for movement {movement} at node {intId}")
            continue
            
        if movement[-1] == 'T':
            type = 'Protected'
        else:
            type = 'Permitted'
        if len(possible_list) == 1:
            traffic_movement_data[movement][type] = traffic_movement_data[possible_list[0]]['Protected']
        else:
            through_movement = movement[0:2]+'T'
            if through_movement in possible_list:
                traffic_movement_data[movement][type] = traffic_movement_data[through_movement]['Protected']
            else:
                traffic_movement_data[movement][type] = traffic_movement_data[possible_list[0]]['Protected']
    phases = {}
    for bound in traffic_movement_data:
        movement_data = traffic_movement_data[bound]
        for phase in movement_data['Protected']:
            if phase not in phases:
                phases[phase] = {"protected": []}
            elif "protected" not in phases[phase]:
                phases[phase]["protected"] = []    
            phases[phase]['protected'].append(bound)
            
        for phase in movement_data['Permitted']:
            if phase not in phases:
                phases[phase] = {"permitted": []}
            elif "permitted" not in phases[phase]:
                phases[phase]["permitted"] = []
            phases[phase]["permitted"].append(bound)            
    return phases
    
def parseLanesDeprecated(synchro_df, intId):
    lanes = synchro_df.get("Lanes")
    #print(lanes.columns)
    data_info = list(lanes['RECORDNAME'][lanes['INTID']==intId])

    data_phase = {'protect':[], 'permit':[]}
    for i in range(data_info.index('LostTime')):
        if 'Phase' in data_info[i]:
            if 'Perm' not in data_info[i]:
                data_phase['protect'].append(data_info[i])
            else:
                data_phase['permit'].append(data_info[i])         
    
    #print(data_phase)
    if data_phase == []:
        print(intId)

    else:
        result = {}
        if data_phase['protect'] != []:
            phase_dt_pro = lanes[(lanes['RECORDNAME'].isin(data_phase['protect'])) & (lanes['INTID']==intId)]
            #print(phase_dt_pro)
            phase_dt_pro = phase_dt_pro[phase_dt_pro.columns[~phase_dt_pro.isnull().all()]]
            #print(phase_dt_pro)
            del(phase_dt_pro['RECORDNAME'])
            del(phase_dt_pro['INTID'])
            direction = list(phase_dt_pro.columns)
            for i in direction:
                phs = list(phase_dt_pro[i][phase_dt_pro[i].notnull()])                
                for p in phs:
                    p = int(p)
                    if p > 0:
                        if 'D'+str(p) not in result:
                            result['D'+str(p)] = {}
                            result['D'+str(p)]['protected'] = []
                            result['D'+str(p)]['protected'].append(i)
                        else:
                            result['D'+str(p)]['protected'].append(i)
                        
        if data_phase['permit'] != []:
            phase_dt_per = lanes[(lanes['RECORDNAME'].isin(data_phase['permit'])) & (lanes['INTID']==intId)]
            phase_dt_per = phase_dt_per[phase_dt_per.columns[~phase_dt_per.isnull().all()]]
            del(phase_dt_per['RECORDNAME'])
            del(phase_dt_per['INTID'])
            direction = list(phase_dt_per.columns)
            for i in direction:
                phs = list(phase_dt_per[i][phase_dt_per[i].notnull()])
                for p in phs:
                    p = int(p)
                    if p>0:
                        if 'D'+str(p) not in result:
                            result['D'+str(p)] = {}
                            result['D'+str(p)]['permitted'] = []
                            result['D'+str(p)]['permitted'].append(i)
                        else:
                            if 'permitted' not in result['D'+str(p)]:
                                result['D'+str(p)]['permitted'] = []
                                result['D'+str(p)]['permitted'].append(i)
                            else:
                                result['D'+str(p)]['permitted'].append(i)
    return(result)

def combine_synchro_dict(synchro_df, intId):
    result = parseSignal(synchro_df, intId)
    phase_info = parseLanes(synchro_df, intId)
    phase_key = list(phase_info.keys())

    for phs in phase_key:
        
        for pro_per in list(phase_info[phs].keys()): 
            result[phs][pro_per] = phase_info[phs][pro_per]
        
    result['brp_info'] = parsePhases(result, intId)
    return(result)

    
       
    
if __name__ == '__main__':
    base_path = r"C:/Users/Fu/Documents/Projects/sumoproj/Dearborn/"
    transfer_file = base_path+"transfer_sigid.csv"
    synchro_csv_file = base_path+"Dearborn.csv"
    synchro_csv_df = parse_synchro_csv(synchro_csv_file)
    print (synchro_csv_df["Lanes"].tail())
    r = combine_synchro_dict(synchro_csv_df, 9)
    print (r)
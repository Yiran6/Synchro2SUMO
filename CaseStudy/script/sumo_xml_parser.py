from lxml import etree as ET
from collections import OrderedDict
import numpy as np

class SumoXmlParser():
    def __init__(self, filename, sumo_ids_filter = None):
        self.filename = filename
        tree = ET.parse(self.filename)
        self.root = tree.getroot()
        self.__parse_sumo_xml(self.filename, sumo_ids_filter)
        self.__parse_edges()

    def __parse_sumo_xml(self, filename, sumo_ids_filter = None):
        #get traffic signal info
        sumo_signal_info = {}
        inbound_edges = {}
        
        for connection in self.root.findall('connection'):
            #get the tlLogic_ids
            tlLogic_ids = connection.get('tl')
            #if tlLogic_ids not in sumo_network_ids:
            #    sumo_network_ids.append(tlLogic_ids)
            if tlLogic_ids is None:
                continue
            
            if sumo_ids_filter is None or tlLogic_ids in sumo_ids_filter:
                if tlLogic_ids not in sumo_signal_info:
                    sumo_signal_info[tlLogic_ids] = {}
                connection_index = connection.get('linkIndex')
                if connection_index is None:
                    continue
                
                inbound_edge_id = connection.get('from')
                if (inbound_edge_id not in inbound_edges) and ':' not in inbound_edge_id: 
                    inbound_edges[inbound_edge_id] = tlLogic_ids
                
                sumo_signal_info[tlLogic_ids][connection_index] = {}
                sumo_signal_info[tlLogic_ids][connection_index]['dir'] = connection.get('dir')
                sumo_signal_info[tlLogic_ids][connection_index]['fromEdge'] = connection.get('from')
                sumo_signal_info[tlLogic_ids][connection_index]['fromLane'] = connection.get('fromLane')
                sumo_signal_info[tlLogic_ids][connection_index]['toEdge'] = connection.get('to')
                sumo_signal_info[tlLogic_ids][connection_index]['toLane'] = connection.get('toLane')
                
        self.sumo_signal_info = sumo_signal_info
        self.inbound_edges = inbound_edges
        

    def generateXml(self, f, signal_id, ret, linkDur, types, offsets, programId = 1):
        f.writelines('\t<tlLogic id="%s" type="%s" programID="%d" offset="%d">\n' % (signal_id, types, programId, offsets))
        
        if types == 'actuated':
            f.write('\t\t<param key="detector-gap" value="2.0"/>\n')
            f.write('\t\t<param key="file" value="NULL"/>\n')
            f.write('\t\t<param key="freq" value="300"/>\n')
            f.write('\t\t<param key="max-gap" value="3.0"/>\n')
            f.write('\t\t<param key="passing-time" value="2.0"/>\n')
            f.write('\t\t<param key="show-detectors" value="false"/>\n')
            f.write('\t\t<param key="vTypes" value=""/>\n')
        if ret:
            for r in ret:
                i = 0
                name = r.get("name", "")
                if isinstance(r['next'], int):
                    next = str(r['next'])
                else:
                    next = " ".join([str(s) for s in r['next']])
                if 'minDur' in r:
                    if types == 'actuated':
                        duration = r['minDur']
                    else:
                        duration = r['maxDur']
                    print("r", r)
                    f.write('\t\t<phase name="%s" duration="%.1f" maxDur="%.1f" minDur="%.1f" next="%s" state="%s"/>\n' % (name, duration, r['maxDur'], r['minDur'],  next, r['state']))
                else:       
                    f.write('\t\t<phase name="%s" duration="%.1f" next="%s" state="%s"/>\n' % (name, r['duration'],  next, r['state']))
            for l in linkDur:
                f.write('\t\t<param key="linkMaxDur:%d" value="%.1f"/>\n' % (l, linkDur[l]['linkMaxDur']))
                f.write('\t\t<param key="linkMinDur:%d" value="%.1f"/>\n' % (l, linkDur[l]['linkMinDur']))
        f.write('\t</tlLogic>\n')
    
    @staticmethod
    def get_slope(shape_info):
        c1 = shape_info[0].split(',')
        c2 = shape_info[1].split(',')
        # (x2,y2) is closer to the intersection.
        x1 = float(c1[0])
        y1 = float(c1[1])
        x2 = float(c2[0])
        y2 = float(c2[1])
        
        X = x2 - x1
        Y = y2 - y1
        if X == 0:
            slope = np.inf
        else:
            slope = Y/X
        return([X, Y, slope])


    def __parse_edges(self):
        self.sumo_nbsw = {}
        self.crossing_dict = {}
        for edge in self.root.findall('edge'):
            edgeids = edge.get('id')
            if edgeids in self.inbound_edges.keys():
                #print(edgeids)
                for lane in edge.findall('lane'):
                    #selected the last two points
                    shape_info = lane.get('shape').split(' ')[-2:]
                    shape_slope = self.get_slope(shape_info)
                    self.sumo_nbsw[edgeids] = shape_slope
                    break 
            if edge.get('function') == 'crossing':
                self.crossing_dict[edgeids] = edge.get('crossingEdges').split(' ')
                

if __name__ == "__main__": 
    x = SumoXmlParser('')
    print(x.sumo_nbsw)
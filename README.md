# Citation
If you use this code in your research or project, please cite our conference publication:

Zhang, Y., Fu, M., & Ban, X. (2024, July). Integration Traffic Signal Control From Synchro to SUMO. In SUMO Conference Proceedings (Vol. 5, pp. 147-162).

```bibtex
@inproceedings{zhang2024integration,
  title={Integration Traffic Signal Control From Synchro to SUMO},
  author={Zhang, Yiran and Fu, Mingjian and Ban, Xuegang},
  booktitle={SUMO Conference Proceedings},
  volume={5},
  pages={147--162},
  year={2024}
}
```

DOI: [doi.org/10.52825/scp.v5i.1112](https://doi.org/10.52825/scp.v5i.1112)

# Code structure
The example modules / code can be found at: CaseStudy/script
* test_main.py: This script serves as the primary entry point for this project. It integrates the core functionality, processes input data, and generates desired outputs.
* synchro_parser.py: Parse the Synchro CSV file
* sumo_xml_parser.py: Parse the SUMO XML file
* synchro_sumo_id_mapping.py: A mapping table between Synchro & Sumo Node IDs
* phase_mapping.py: Script to mapping signal phases from Synchro to SUMO

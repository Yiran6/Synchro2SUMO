# Citation
If you use this code in your research or project, please cite our conference publication:

Zhang, Y., Fu, M., & Ban, X. (2024). **Integration Traffic Signal Control From Synchro to SUMO.** SUMO Conference Proceedings, 5, 147–162.

```bibtex
@article{Zhang_Fu_Ban_2024,
  title = {Integration Traffic Signal Control From Synchro to SUMO},
  volume = {5},
  url = {https://www.tib-op.org/ojs/index.php/scp/article/view/1112},
  journal = {SUMO Conference Proceedings},
  author = {Zhang, Yiran and Fu, Mingjian and Ban, Xuegang},
  year = {2024},
  month = {Jul.},
  pages = {147--162}
}
```

DOI: [doi.org/10.52825/scp.v5i.1112](https://doi.org/10.52825/scp.v5i.1112)

# Code structure
The example modules / code can be found at: CaseStudy/script
* test_main.py: This script serves as the primary entry point for this project. It integrates the core functionality, processes input data, and generates desired outputs.
* synchro_parser.py: Parse the Synchro CSV file
* sumo_xml_parser.py: Parse the SUMO XML file
* synchro_sumo_id_mapping.py: A mapping table between Synchro & Sumo Node IDs, from transfer_sigid.csv
* phase_mapping.py: Script to mapping signal phases from Synchro to SUMO. 

# repo-gempa

This dataset is taken from the Earthquake Repository managed by BMKG (an Indonesian non-departmental government agency). BMKG changed their site design in early 2023, and this resulted in two different datasets.

The new dataset (`katalog_gempa_v2.tsv`) is taken from the *Preliminary Earthquake Catalog* which includes focal mechanism data (if any). It contains earthquake event data from 1 Nov 2008 to 15 Apr 2023, but may not be accurate for some of the last earthquake events recorded. There are 38 variables in this dataset, each with a descriptive name.

On the other hand, the old dataset (`katalog_gempa.csv`) contains earthquake event data from 1 Nov 2008 to 26 Jan 2023. The variables collected in this dataset are:

- `tgl`: date of the event
- `ot`: timestamp of the event
- `lat`: latitude of the event epicentre (degree), ranging from 6N to 11S
- `lon`: longitude of the event epicentre (degree), ranging from 142E to 94E
- `depth`: depth of the event (km)
- `mag`: magnitude of the event, ranging from 1 up to 9.5
- `remark`: Flinn-Engdahl regions of the event
- sometimes, the focal mechanism of the event is measured. In that case, `dip1`, `strike1`, `rake1`, `dip2`, `strike2`, and `rake2` values are not empty.

Kaggle version of this dataset can be accessed at [earthquakes-in-indonesia](https://www.kaggle.com/datasets/kekavigi/earthquakes-in-indonesia).

### Acknowledgements
Meteorology, Climatology, and Geophysical Agency (Badan Meteorologi, Klimatologi, dan Geofisika; BMKG) Earthquake Repository (http://repogempa.bmkg.go.id/repo_new/)
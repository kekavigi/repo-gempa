### Content

This dataset is scraped from the Earthquake Repository managed by BMKG (an Indonesian non-departmental government agency). Main variables collected in this repository are:

- `tgl`: date of the event from 1 Nov 2008
- `ot`: timestamp of the event
- `lat`: latitude of the event epicentre (degree), ranging from 6N to 11S
- `lon`: longitude of the event epicentre (degree), ranging from 142E to 94E
- `depth`: depth of the event (km)
- `mag`: magnitudo of the event, ranging from 1 up to 9.5
- `remark`: Flinn–Engdahl regions of the event

Sometimes, the focal mechanism of the event is measured. In that case, `dip1`, `strike1`, `rake1`, `dip2`, `strike2`, and `rake2` values isn't empty. See an example of [focal mechanism visualization](http://repogempa.bmkg.go.id/repo_new/viewfm.php?strike1=99.5&dip1=56.9&rake1=118.8&strike2=234.29&dip2=42.7&rake2=53.5&tgl=2022/02/03&ot=11:37:45.161&lat=7.50&lon=119.67&ketlat=S&ketlon=E&depth=10&mag=5.1&remark=Flores+Sea+&status=unset) created by BMKG.

Kaggle repository for this data can be accessed at https://www.kaggle.com/datasets/kekavigi/earthquakes-in-indonesia.

### Acknowledgements
Meteorology, Climatology, and Geophysical Agency (Badan Meteorologi, Klimatologi, dan Geofisika; BMKG) Earthquake Repository (http://repogempa.bmkg.go.id/repo_new/)
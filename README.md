# iSTAGING-Tools

After proper installation, the tools can be used as follows

```shell
 python -m iSTAGING.main --data_file istaging.pkl.gz --harmonization_model_file MUSE_harmonization_model.pkl
```

where `istaging.pkl.gz` and `MUSE_harmonization_model.pkl` are the data and
harmonization models, respectively.

## Setup for development
Install Python version 3.8.8 or newer. Verify with

```shell
python --version # should be 3.8.8 or newer
```

### Linux (CUBIC)
```shell
python -m venv .env
.env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt 
python -m pip install -e . # assuming in `iSTAGING-Tools` folder
```

### Windows 10
Assuming current working directory is `iSTAGING-Tools`.
```shell
python -m venv .env
& .env/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e . # assuming in `iSTAGING-Tools` folder
```



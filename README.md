# iSTAGING-Tools

## Setup

### Linux (CUBIC)
```shell
python -m venv .env
.env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt 
python -m pip install -e iSTAGING-Tools
cd .env
git clone git@github.com:rpomponio/neuroHarmonize.git
cd neuroHarmonize
git pull origin pull/9/head
python -m pip install -e .
```

### Windows 10
Assuming current working directory is `iSTAGING-Tools`.
```shell
python -m venv .env
& .env/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
cd .env
git clone git@github.com:rpomponio/neuroHarmonize.git
cd neuroHarmonize
git pull origin pull/9/head
python -m pip install -e .
```



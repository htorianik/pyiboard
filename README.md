# PyIBoard v0.2.7
This is IBs core written on Python.

Demo you can see on this [video](https://google.com).

[image_1](http://google.com)
[image_2](http://google.com)

## how to deploy me?
```bash
python3 -m venv pyiboard-env 
cd pyiboard-env
git clone https://github.com/D34DStone/pyiboard

. ./bin/activate
cd pyiboard

# I don't proud of this, but I didn't write initial script...
mkdir var && mkdir resources/uploads

# to reload db
python3 init_db.py
# to run server
python3 run.py
```

## how to configurate me?
### resource structure
All resources placed in ```/resources```
```/resources/public``` -- resources that you can always get like scripts, styles, fonts 
You should keep any kind of media in ```resources/public/board-images```

Also there is ```/resources/uploads``` dir. This folder just for server, you should't touch it.
There is media uploaded by users.

### boards config
There is something horrible, idk how it works. Sometimes I'll fix it.
Generally this is instruction how to fill boards table.

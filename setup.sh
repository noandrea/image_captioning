#|/bin/bash
# build docker image
# docker build -t welance/dn2018 .

virtualenv --python=python3 p3dn
# source p2dn/bin/activate
source ./p3dn/bin/activate

pip install numpy
pip install opencv-python
pip install opencv-contrib-python
pip install scipy
pip install matplotlib
pip install ipython
pip install jupyter
pip install pandas
pip install sympy
pip install nose
pip install tqdm
pip install tensorflow
pip install scikit-image
pip install nltk
pip install psycopg2
pip install pynacl
pip install flask
pip install flask_socketio
pip install eventlet

python -m nltk.downloader punkt
